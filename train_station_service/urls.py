from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/train-station/",
        include("train_station.urls", namespace="train-station")
    ),
]
