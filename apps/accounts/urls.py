from django.urls import path

from .views import ChangePasswordView, LoginView, MeView, RefreshView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api-register"),
    path("login/", LoginView.as_view(), name="api-login"),
    path("refresh/", RefreshView.as_view(), name="api-refresh"),
    path("me/", MeView.as_view(), name="api-me"),
    path("password/", ChangePasswordView.as_view(), name="api-change-password"),
]
