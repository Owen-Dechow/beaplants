from io import BytesIO
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.conf.global_settings import EMAIL_HOST_USER
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.conf import settings
from random import random
from . import keys
from . import xlsx

from . import models
from . import forms


########## UTILS ##########
def str_val_2_404(
    string, max_length=None, min_length=None, options=None, char_options=None
):
    ERR = lambda str: f"STRING VALIDATION FAILED: '{str}'"

    if max_length and len(string) > max_length:
        raise Http404(f"{ERR(string)} exceeds max length: {max_length}")

    if min_length and len(string) < min_length:
        raise Http404(f"{ERR(string)} under min length: {min_length}")

    if options and string not in options:
        raise Http404(f"{ERR(string)} not in options: {options}")

    if char_options:
        for l in string:
            if l not in char_options:
                raise f"{ERR(string)} character '{l}' not found in char_options: {char_options}"


########## VIEWS ##########
def landing_page(request: WSGIRequest):
    season = models.Season.objects.filter().last()
    products = models.Product.objects.select_related("season").filter(season=season)
    products = list(sorted(products, key=lambda x: random()))
    context = {
        "products": products,
        "season": season,
        "hero_info": settings.HOMEPAGE_INFO,
    }

    return render(request, "home.html", context)


@login_required
@transaction.atomic
def manage_page(request: WSGIRequest):
    if request.method == "POST":
        if "season_id" not in request.POST:
            raise Http404("Season Un Identifiable")

        if request.POST["season_id"] == "-1":
            instance = models.Season(
                add_key=keys.create_secret_key(
                    models.Season._meta.get_field("add_key").max_length
                )
            )
        else:
            instance = get_object_or_404(models.Season, id=request.POST["season_id"])

        form = forms.SeasonForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = None

    seasons = models.Season.objects.order_by("-id").all()
    orders = models.Order.objects.select_related("product").filter(open=True)
    context = {"seasons": seasons, "form": form, "orders": orders}
    return render(request, "manage.html", context)


@transaction.atomic
def product_submissions_page(request: WSGIRequest):
    if request.method == "POST":
        print("H?hhjhhg")
        season = models.Season.objects.last()
        if season is None:
            raise Http404("No Season Found")

        form = forms.ProductForm(
            request.POST, request.FILES, instance=models.Product(season=season)
        )

        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/")
    else:
        form = forms.ProductForm

    context = {"form": form}
    return render(request, "product_submissions.html", context)


@transaction.atomic
def product_page(request: WSGIRequest, id: int):
    product = get_object_or_404(models.Product.objects.select_related("season"), id=id)

    if request.method == "POST":
        form = forms.OrderForm(
            request.POST,
            instance=models.Order(product=product, open=True, season=product.season),
        )
        if form.is_valid():
            product.quantity_in_stock -= 1
            product.save()
            order = form.save()

            try:
                send_mail(
                    subject="Thank you for your order!",
                    message=render_to_string(
                        "order_confirm_email.txt",
                        {
                            "order": order,
                            "url": request.get_host(),
                            "product": product,
                            "contacts": product.season.contacts.split("\n"),
                        },
                        request,
                    ),
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[form.cleaned_data["email"]],
                    fail_silently=False,
                )

                return HttpResponseRedirect("/order-sent")
            except:
                form.add_error("email", ValidationError("Failed email send."))
                order.delete()
    else:
        form = forms.OrderForm()

    images = models.ProductImage.objects.filter(product=product)
    context = {"product": product, "images": images, "form": form}
    return render(request, "product.html", context)


def order_sent_page(request: WSGIRequest):
    season = models.Season.objects.filter().last()
    return render(request, "ordersent.html", {"season": season})


@transaction.atomic
def filters(request: WSGIRequest, id: str, size: str, sort: str, search: str):
    str_val_2_404(size, options=[x[0] for x in models.PRODUCT_SIZE_OPTIONS] + ["none"])
    str_val_2_404(sort, options=["random", "price-high-to-low", "price-low-to-high"])
    str_val_2_404(id, max_length=models.Filter._meta.get_field("user_id").max_length)

    search = search[1:]
    season = models.Season.objects.last()
    data_saver = models.Filter()
    data_saver.season = season
    data_saver.size = size
    data_saver.sort = sort
    data_saver.search = search
    data_saver.user_id = id
    data_saver.save()

    return HttpResponse("Data Submitted")


@transaction.atomic
def product_view(request: WSGIRequest, id: str, product: int):
    str_val_2_404(id, max_length=models.Filter._meta.get_field("user_id").max_length)
    viewed_product = get_object_or_404(
        models.Product.objects.select_related("season"), id=product
    )

    data_saver = models.ProductView()
    data_saver.user_id = id
    data_saver.product = viewed_product
    data_saver.season = viewed_product.season
    data_saver.save()

    return HttpResponse("Data Submitted")


@login_required
@transaction.atomic
def delete_season(request: WSGIRequest, seasonID):
    season = get_object_or_404(models.Season, id=seasonID)
    season.delete()
    return HttpResponseRedirect("/manage")


@login_required
@transaction.atomic
def close_order(request: WSGIRequest, orderID):
    order = get_object_or_404(models.Order, id=orderID)
    order.open = False
    order.save()
    return HttpResponseRedirect("/manage")


@login_required
@transaction.atomic
def pull_data(request: WSGIRequest, seasonID):
    season = get_object_or_404(models.Season, id=seasonID)

    filters = models.Filter.objects.filter(season=season)
    product_views = models.ProductView.objects.select_related("product").filter(
        season=season
    )
    products = models.Product.objects.filter(season=season)
    orders = models.Order.objects.select_related("product").filter(season=season)

    with BytesIO() as output:
        workbook = xlsx.Workbook(
            output, ["Filters", "ProductViews", "Products", "Orders"]
        )

        workbook.write_sheet(
            "Filters",
            ["user_id", "size", "sort", "search"],
            filters,
        )
        workbook.write_sheet(
            "ProductViews",
            ["user_id", "product"],
            product_views,
        )
        workbook.write_sheet(
            "Products",
            ["group_members", "name", "size", "production_cost", "description"],
            products,
        )
        workbook.write_sheet(
            "Orders",
            [
                "user_id",
                "product",
                "name",
                "email",
                "phone_number",
                "student_deliverer",
                "donation",
            ],
            orders,
        )

        workbook.close()

        output.seek(0)

        response = HttpResponse(output.read())
        response["Content-Type"] = "application/vnd.ms-excel"
        response["Content-Disposition"] = f"attachment; filename=BEAPlantsData.xlsx"

        output.close()
        return response
