from typing import Any
from django import forms
from .models import Order, Season, Product, ProductImage
from . import keys

# from django.conf.global_settings import DATA_UPLOAD_MAX_NUMBER_FILES


class OrderForm(forms.ModelForm):
    donation = forms.FloatField(
        min_value=0,
        max_value=10000,
        required=False,
        label="Make a Donation",
        widget=forms.TextInput(attrs={"id": "donation-input"}),
    )

    user_id = forms.CharField(widget=forms.HiddenInput(attrs={"id": "uid-input"}))

    def is_valid(self) -> bool:
        print("validating")
        if not super().is_valid():
            return False
        print("validating2")

        if self.instance.product.quantity_in_stock <= 0:
            self.add_error(None, "Product is out of stock.")
            return False

        print("validating3")
        if not self.instance.product.in_season():
            self.add_error(None, "Product not being sold at this time.")
            return False

        print("validating4")
        return True

    class Meta:
        model = Order
        exclude = ["product", "open", "season"]


class SeasonForm(forms.ModelForm):
    season_id = forms.IntegerField(required=True, widget=forms.HiddenInput())

    def is_valid(self) -> bool:
        if not super().is_valid():
            return False

        try:
            markup_json = self.cleaned_data["markup"]
            last_day = -1
            for key, val in markup_json.items():
                assert type(key) == str, "Key is not string"
                assert type(val) in (float, int), "Val is not int or float"
                assert key.isdigit(), "Key is not digit"
                assert val >= 0, "Val is not greater than 0"
                assert int(key) > last_day, "Invalid day order"
                last_day = int(key)
        except:
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


class ProductForm(forms.ModelForm):
    name = forms.CharField(
        label="Product Name", max_length=Product._meta.get_field("name").max_length
    )
    images = MultiImageField(required=True)
    add_key = forms.CharField(required=True)
    group_members = forms.JSONField(widget=forms.TextInput(attrs={"readonly": True}))

    def is_valid(self) -> bool:
        if not super().is_valid():
            return False

        print(self.cleaned_data["group_members"])
        try:
            group_members_json = self.cleaned_data["group_members"]
            for key, val in group_members_json.items():
                assert type(key) == str, "Key is not string"
                assert type(val) == str, "Val is not string"
                assert len(key) > 0, "Key too short."
                assert len(val) > 0, "Val too short."
        except:
            self.add_error("markup", "Invalid group name pattern.")
            return False

        real_key = keys.get_hour_key(self.instance.season.add_key)
        if real_key != self.cleaned_data["add_key"]:
            self.add_error(
                "add_key",
                "Add key invalid. Ensure the key has not expired.",
            )
            return False

        return True

    class Meta:
        model = Product
        exclude = ["season"]

    def save(self, commit: bool = ...) -> Any:
        result = super().save(commit)

        images = []
        for img in self.cleaned_data["images"]:
            images.append(ProductImage(product=self.instance, image=img))

        ProductImage.objects.bulk_create(images)

        return result
