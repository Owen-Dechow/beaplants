from django.db import models
from . import keys
from django.utils import timezone

PRODUCT_SIZE_OPTIONS = [
    ("small", "Small"),
    ("medium", "Medium"),
    ("large", "Large"),
]


class Season(models.Model):
    def __str__(self):
        return str(self.sales_date_start)

    sales_date_start = models.DateField()
    markup = models.JSONField()
    add_key = models.CharField(max_length=20)
    contacts = models.TextField()

    def get_markup(self):
        return self.markup["0"]

    def valid_markup_json(self):
        return str(self.markup).replace("'", '"')

    def valid_sales_date_start_format(self):
        return self.sales_date_start.strftime(r"%Y-%m-%d")

    def get_current_key(self):
        return keys.get_hour_key(self.add_key)

    def string_id(self):
        return str(self.id)


class Product(models.Model):
    def __str__(self):
        return self.name

    group_members = models.JSONField()
    name = models.CharField(max_length=100)
    quantity_in_stalk = models.IntegerField()
    size = models.CharField(choices=PRODUCT_SIZE_OPTIONS, max_length=20)
    logo = models.ImageField(upload_to="images/")
    production_cost = models.FloatField()
    season = models.ForeignKey(to=Season, on_delete=models.CASCADE)
    description = models.TextField()

    def price(self):
        return self.production_cost + self.production_cost * self.season.get_markup()

    def formatted_price(self):
        return "${:,.2f}".format(self.price())

    def sold_out(self):
        return self.quantity_in_stalk <= 0

    def in_season(self):
        if self.season != Season.objects.last():
            return False

        return self.season.sales_date_start <= timezone.now().date()

    def can_be_sold(self):
        if self.sold_out():
            return False

        return self.in_season()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/")


class Order(models.Model):
    def __str__(self):
        return str(self.product)

    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone_number = models.CharField(max_length=16)
    student_deliverer = models.CharField(max_length=200)
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
