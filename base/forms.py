from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import QueryDict
from django.utils.http import MultiValueDict
from .models import Order, Season, ProductVariation, ProductImage, Product


class OrderForm(forms.ModelForm):
    donation = forms.FloatField(
        min_value=0,
        max_value=1_000,
        required=False,
        label="Make a Donation",
        widget=forms.TextInput(attrs={"id": "donation-input"}),
    )

    user_id = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "uid-input"}), label=""
    )
    product = forms.IntegerField(
        widget=forms.HiddenInput(attrs={"id": "product-input"}), label=""
    )
    delivery_instructions = forms.CharField(
        label="Pickup Specifactions",
        widget=forms.Textarea(attrs={"placeholder": "John Doe will pick this up..."}),
    )

    def clean_product(self):
        product_id = self.cleaned_data["product"]
        try:
            product = ProductVariation.objects.get(id=product_id)
        except ProductVariation.DoesNotExist:
            print("ERROR 1" * 100)
            raise forms.ValidationError("Selected Product Not Found")

        if product.quantity_in_stock <= 0:
            print("ERROR 2" * 100)
            raise forms.ValidationError("Product Sold Out")

        if not product.product.in_season():
            raise forms.ValidationError("Product is not being sold at this time.")

        return product

    class Meta:
        model = Order
        exclude = ["open", "season"]


class SeasonForm(forms.ModelForm):
    season_id = forms.IntegerField(required=True, widget=forms.HiddenInput())

    def is_valid(self) -> bool:
        if not super().is_valid():
            return False

        try:
            markup_json = self.cleaned_data["markup"]
            last_day = -1
            for key, val in markup_json.items():
                assert type(key) is str, "Key is not string"
                assert type(val) in (float, int), "Val is not int or float"
                assert key.isdigit(), "Key is not digit"
                assert val >= 0, "Val is not greater than 0"
                assert int(key) > last_day, "Invalid day order"
                last_day = int(key)
        except AssertionError | ValueError:
            self.add_error("markup", "Invalid markup pattern.")
            return False

        return True

    class Meta:
        model = Season
        exclude = ["add_key"]


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductFormFamily:
    product_form: "ProductForm"
    variation_forms: list["ProductVariationForm"]

    def __init__(self, data: QueryDict, files: MultiValueDict, prefix: str):
        normal_data = {}
        variant_data = {}

        normal_files = {}
        variant_files = {}

        self.variation_forms = []

        for key, val in files.lists():
            split_key: list[str] = key.split("-")

            if split_key.__len__() < 2:
                normal_files[key] = val[0]
                continue
            else:
                v_key = split_key[0]

            if not v_key.startswith(prefix):
                normal_files[key] = val[0]
                continue

            try:
                var_id = float(v_key.removeprefix(prefix))
            except ValueError:
                normal_files[key] = val[0]
                continue

            if var_id not in variant_data:
                variant_files[var_id] = {}

            variant_files[var_id][key] = val

        for key, val in data.items():
            split_key: list[str] = key.split("-")

            if split_key.__len__() < 2:
                normal_data[key] = val
                continue
            else:
                v_key = split_key[0]

            if not v_key.startswith(prefix):
                normal_data[key] = val
                continue

            try:
                var_id = float(v_key.removeprefix(prefix))
            except ValueError:
                normal_data[key] = val
                continue

            if var_id not in variant_data:
                variant_data[var_id] = {}

            variant_data[var_id][key] = val

        self.product_form = ProductForm(normal_data, normal_files)
        for key, val in variant_data.items():
            self.variation_forms.append(
                ProductVariationForm(
                    val, variant_files.get(key, {}), prefix=f"{prefix}{key}"
                )
            )

    def is_valid(self) -> bool:
        results = [x.is_valid() for x in self.variation_forms]
        results.append(self.product_form.is_valid())
        return all(results)

    def save(self):
        product = self.product_form.save()

        for variation_form in self.variation_forms:
            variation_form.instance = ProductVariation(product=product)
            variation_form.save(product)


class ProductForm(forms.ModelForm):
    group_members = forms.JSONField(widget=forms.TextInput)

    class Meta:
        model = Product
        fields = ["name", "logo", "production_cost", "season", "group_members"]

    def clean_add_key(self) -> dict:
        if self.instance.season.add_key != self.cleaned_data["add_key"]:
            raise forms.ValidationError("Add key is invalid.")

        return self.cleaned_data["add_key"]

    def clean_group_members(self) -> dict:
        try:
            group_members_json = self.cleaned_data["group_members"]
            for key, val in group_members_json.items():
                assert type(key) is str, "Key is not string"
                assert type(val) is str, "Val is not string"
                assert len(key) > 0, "Key too short."
                assert len(val) > 0, "Val too short."
        except AssertionError:
            raise forms.ValidationError("Invalid group name pattern.")

        return group_members_json


class ProductVariationForm(forms.ModelForm):
    images = MultiImageField(required=True)

    class Meta:
        model = ProductVariation
        fields = ["quantity_in_stock", "size", "variant_label"]

    def save(self, product: Product):
        variation = ProductVariation(
            **{x: self.cleaned_data[x] for x in self.Meta.fields}, product=product
        )
        variation.save()

        for image in self.cleaned_data["images"]:
            ProductImage.objects.create(variation=variation, image=image)
