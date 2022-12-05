from django.views.generic import RedirectView
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('weight/', views.weight, name='weight'),
    path('diary/', views.diary, name='diary'),
    path('stats/', views.home, name='stats'),

    path('add_food_to_diary/', views.add_food_to_diary, name='add_food_to_diary'),

    path('', RedirectView.as_view(url='home/')),
    # path('test/', views.test_view, name='test'),
]
