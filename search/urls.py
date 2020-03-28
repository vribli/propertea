from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('favourites', views.favourites_view, name="favourites"),
]
