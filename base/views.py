import email
from io import BytesIO
from math import prod
from operator import mod
from random import random

from django.conf import settings
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.fields import return_None
from django.forms import ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from . import forms, models, xlsx


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
        for letter in string:
            if letter not in char_options:
                raise f"{ERR(string)} character '{letter}' not found in char_options: {char_options}"


########## VIEWS ##########
def landing_page(request: WSGIRequest):
    try:
        season = models.Season.objects.filter().last()
        products = models.Product.objects.select_related("season").filter(season=season)
        products = list(sorted(products, key=lambda _: random()))
    except:
        season = None
        products = None

    context = {
        "products": products,
        "season": season,
        "hero_info": settings.HOMEPAGE_INFO,
        "full_footer": True,
    }

    return render(request, "home.html", context)


@login_required
@transaction.atomic
def manage_page(request: WSGIRequest):
    if request.method == "POST":
        if "season_id" not in request.POST:
            raise Http404("Season Not Identifiable")

        if request.POST["season_id"] == "-1":
            instance = models.Season(add_key=models.Season.generate_key())
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
        form_family = forms.ProductFormFamily(request.POST, request.FILES, "v")
        if form_family.is_valid():
            form_family.save()
            return HttpResponseRedirect("/")
        else:
            var_forms = form_family.variation_forms
            form = form_family.product_form
    else:
        form = forms.ProductForm(instance=models.Product())
        var_forms = None

    context = {
        "form": form,
        "var_form_template": forms.ProductVariationForm(prefix="v%"),
        "var_forms": var_forms,
    }
    return render(request, "product_submissions.html", context)


@transaction.atomic
def product_page(request: WSGIRequest, id: int):
    product = get_object_or_404(models.Product.objects.select_related("season"), id=id)
    variations = {}
    for variation in models.ProductVariation.objects.filter(product=product):
        variations[variation] = models.ProductImage.objects.filter(variation=variation)

    if request.method == "POST":
        form = forms.OrderForm(
            request.POST, instance=models.Order(open=True, season=product.season)
        )

        if form.is_valid():
            form.cleaned_data["product"].quantity_in_stock -= 1
            form.cleaned_data["product"].save()
            order = form.save()

            send_mail(
                subject="We received your BEAPlants order!",
                message=render_to_string(
                    "order_confirm_email.txt",
                    {
                        "order": order,
                        "url": request.get_host(),
                        "contact_info": product.season.contacts,
                    },
                ),
                from_email=EMAIL_HOST_USER,
                recipient_list=[order.email, EMAIL_HOST_USER],
                fail_silently=False,
            )

            return HttpResponseRedirect("/order-sent")

    else:
        form = forms.OrderForm

    context = {"product": product, "variations": variations, "form": form}
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
    products = models.ProductVariation.objects.filter(season=season)
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
        response["Content-Disposition"] = "attachment; filename=BEAPlantsData.xlsx"

        output.close()
        return response
