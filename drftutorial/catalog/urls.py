from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^products/$', views.ProductList.as_view()),
]
