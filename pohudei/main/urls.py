from django.views.generic import RedirectView
from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.diary, name='home'),
    path('diary/', views.diary, name='diary'),
    path('diary/<date_iso>/', views.diary, name='diary'),
    path('stats/', views.stats, name='stats'),
    path('foods/', views.foods, name='foods'),
    path('options/', views.options, name='options'),

    path('update_weight/', views.update_weight),

    path('add_food_to_diary/', views.add_food_to_diary),
    path('update_diary_entry/', views.update_diary_entry),
    path('delete_diary_entry/', views.delete_diary_entry),

    path('add_food_to_catalogue/', views.add_food_to_catalogue),
    path('update_food_in_catalogue/', views.update_food_in_catalogue),
    path('delete_food_from_catalogue/', views.delete_food_from_catalogue),

    path('set_options/', views.set_options_ajax),

    path('noprofile/', views.noprofile, name='noprofile'),
    path('', RedirectView.as_view(url='home/')),
]
