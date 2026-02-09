from random import random

from django.conf import settings
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from . import forms, models


########## UTILS ##########
def str_val_2_404(
    string, max_length=None, min_length=None, options=None, char_options=None
):
    def ERR(e: str):
        return Http404(f"STRING VALIDATION FAILED: '{string}' {e}.")

    if max_length and len(string) > max_length:
        raise ERR(f"exceeds max length: {max_length}")

    if min_length and len(string) < min_length:
        raise ERR(f"under min length: {min_length}")

    if options and string not in options:
        raise ERR(f"not in options: {options}")

    if char_options:
        for letter in string:
            if letter not in char_options:
                raise ERR(
                    f"character '{letter}' not found in char_options: {char_options}"
                )


########## VIEWS ##########
def landing_page(request: WSGIRequest):
    try:
        season = models.Season.objects.filter().last()
        products = models.Product.objects.select_related("season").filter(season=season)
        products = list(sorted(products, key=lambda _: random()))
    except ObjectDoesNotExist:
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

            url = request.get_host()
            send_mail(
                subject=f"We received your {url} order!",
                message=render_to_string(
                    "order_confirm_email.txt",
                    {
                        "order": order,
                        "url": url,
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


@login_required
@transaction.atomic
def delete_season(_request: WSGIRequest, seasonID):
    season = get_object_or_404(models.Season, id=seasonID)
    season.delete()
    return HttpResponseRedirect("/manage")


@login_required
@transaction.atomic
def close_order(_request: WSGIRequest, orderID):
    order = get_object_or_404(models.Order, id=orderID)
    order.open = False
    order.save()
    return HttpResponseRedirect("/manage")
