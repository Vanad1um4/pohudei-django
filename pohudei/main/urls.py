from django.views.generic import RedirectView
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.diary, name='home'),
    path('weight/', views.weight, name='weight'),
    path('diary/', views.diary, name='diary'),
    path('stats/', views.diary, name='stats'),

    path('add_new_weight/', views.add_new_weight, name='add_new_weight'),
    path('update_weight/', views.update_weight, name='update_weight'),
    path('delete_weight/', views.delete_weight, name='delete_weight'),

    path('add_food_to_diary/', views.add_food_to_diary, name='add_food_to_diary'),
    path('update_diary_entry/', views.update_diary_entry, name='update_diary_entry'),
    path('delete_diary_entry/', views.delete_diary_entry, name='delete_diary_entry'),

    path('', RedirectView.as_view(url='home/')),
]
