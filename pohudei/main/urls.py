from django.views.generic import RedirectView
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('weight/', views.weight, name='weight'),

    path('', RedirectView.as_view(url='home/')),
    # path('test/', views.test_view, name='test'),
]
