from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^products/$',
        views.ProductList.as_view(),
        name='product-list'
    ),
    url(
        r'^products/(?P<product_id>[0-9]+)/$',
        views.ProductDetail.as_view(),
        name='product-detail'
    ),
    url(
        r'^products/(?P<product_id>[0-9]+)/reviews/$',
        views.ReviewList.as_view(),
        name='review-list'
    ),
    url(
        r'^products/(?P<product_id>[0-9]+)/reviews/(?P<review_id>[0-9]+)/$',
        views.ReviewDetail.as_view(),
        name='review-detail'
    ),
]
