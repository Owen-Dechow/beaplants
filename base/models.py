from random import choice

from django.db import models
from django.utils import timezone

PRODUCT_SIZE_OPTIONS = [
    ("small", "Small"),
    ("medium", "Medium"),
    ("large", "Large"),
]


LETTER_SET = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def image_upload(instance, filename):
    upload_to = "images/"
    extension = filename.split(".")[-1]
    uid = "".join([choice(LETTER_SET) for i in range(20)])

    return upload_to + uid + "." + extension


class Season(models.Model):
    def __str__(self):
        return str(self.sales_date_start)

    sales_date_start = models.DateField()
    markup = models.JSONField()
    add_key = models.CharField(max_length=20)
    contacts = models.TextField()

    def get_markup(self):
        days_past_start = timezone.now().date() - self.sales_date_start
        current_section = 0

        for key in self.markup:
            key = int(key)
            if days_past_start.days >= key:
                current_section = max(current_section, key)

        print(current_section)

        return self.markup[str(current_section)]

    def valid_markup_json(self):
        return str(self.markup).replace("'", '"')

    def valid_sales_date_start_format(self):
        return self.sales_date_start.strftime(r"%Y-%m-%d")

    def string_id(self):
        return str(self.id)

    def days_till_sale(self):
        time_till = self.sales_date_start - timezone.now().date()
        return time_till.days

    @classmethod
    def generate_key(cls):
        return "-".join(
            "".join([choice(LETTER_SET) for j in range(3)]) for i in range(3)
        )


class Product(models.Model):
    def __str__(self):
        return self.name

    group_members = models.JSONField()
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to=image_upload)
    production_cost = models.FloatField()
    season = models.ForeignKey(to=Season, on_delete=models.CASCADE)
    description = models.TextField()

    def price(self):
        return self.production_cost * (self.season.get_markup() + 1)

    def formatted_price(self):
        return "${:,.2f}".format(self.price())

    def quantity_in_stock(self):
        return sum(
            x.quantity_in_stock for x in ProductVariation.objects.filter(product=self)
        )

    def sold_out(self):
        return self.quantity_in_stock() <= 0

    def in_season(self):
        if self.season != Season.objects.last():
            return False

        return self.season.sales_date_start <= timezone.now().date()

    def can_be_sold(self):
        if self.sold_out():
            return False

        return self.in_season()


class ProductVariation(models.Model):
    def __str__(self):
        return f"{self.id}: {self.product.name}"

    quantity_in_stock = models.IntegerField()
    size = models.CharField(choices=PRODUCT_SIZE_OPTIONS, max_length=20)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    variant_label = models.CharField(max_length=255)

    def sold_out(self):
        return self.quantity_in_stock <= 0


class ProductImage(models.Model):
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload)


class Order(models.Model):
    def __str__(self):
        return str(self.product)

    product = models.ForeignKey(to=ProductVariation, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone_number = models.CharField(max_length=16)
    delivery_instructions = models.CharField(max_length=500)
    donation = models.FloatField(blank=True, null=True)
    user_id = models.CharField(max_length=100)
    open = models.BooleanField(default=True)
    season = models.ForeignKey(to=Season, on_delete=models.CASCADE)


class Filter(models.Model):
    def __str__(self):
        return f"({self.user_id}) | ({self.size}) | ({self.sort}) | ({self.search})"

    user_id = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    sort = models.CharField(max_length=50)
    search = models.TextField()
    season = models.ForeignKey(to=Season, on_delete=models.CASCADE)


class ProductView(models.Model):
    def __str__(self):
        return f"({self.user_id}) | ({self.product})"

    user_id = models.CharField(max_length=100)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    season = models.ForeignKey(to=Season, on_delete=models.CASCADE)
