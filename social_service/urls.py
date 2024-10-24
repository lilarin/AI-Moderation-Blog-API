from django.contrib import admin
from django.urls import path
from social_service.api import api


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls)
]
