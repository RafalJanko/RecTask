from django.conf.urls import url
from django.urls import path
from . import views
from Books.views import OneBookView

urlpatterns = [
    url(r'^add/book/$', views.add_book, name='add_book'),
    url(r'^import/book/$', views.google_import, name='import_book'),
    path('books/<int:pk>/', OneBookView.as_view(), name='book-details'),
]
