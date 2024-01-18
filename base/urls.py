from . import views
from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("manage", views.manage_page, name="manage_page"),
    path(
        "product-submissions",
        views.product_submissions_page,
        name="product_submissions_page",
    ),
    path("p/<int:id>", views.product_page, name="product_page"),
    path("order-sent", views.order_sent_page, name="order_sent_page"),
    path("filter/<str:id>/<str:size>/<str:sort>/<str:search>", views.filters),
    path("product-view/<str:id>/<int:product>", views.product_view),
    path("delete-season/<int:seasonID>", views.delete_season),
    path("close-order/<int:orderID>", views.close_order),
    path("pull-data/<int:seasonID>", views.pull_data),
] + [
    path("login", LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout", LogoutView.as_view(template_name="auth/form.html"), name="logout"),
    path(
        "password_reset",
        PasswordResetView.as_view(template_name="auth/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done",
        PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>",
        PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done",
        PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
