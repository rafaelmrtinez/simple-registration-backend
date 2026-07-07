from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.UserProfile.as_view(), name="user-profile"),
    path("profiles/", views.UserProfile.as_view(), name="user-profile-list"),
]
