from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_image),
    path("add/", views.add_thumbnail),
    path("rank/", views.rankings),
    path("", views.index)
]