from django.views.generic import RedirectView
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.diary, name='home'),
    path('weight/', views.weight, name='weight'),
    path('diary/', views.diary, name='diary'),
    path('diary/<date_iso>/', views.diary),
    path('stats/', views.stats, name='stats'),
    path('options/', views.options, name='options'),
    path('noprofile/', views.noprofile, name='noprofile'),

    path('add_new_weight/', views.add_new_weight),
    path('update_weight/', views.update_weight),
    path('delete_weight/', views.delete_weight),

    path('update_weight_new/', views.update_weight_new),

    path('add_food_to_diary/', views.add_food_to_diary),
    path('update_diary_entry/', views.update_diary_entry),
    path('delete_diary_entry/', views.delete_diary_entry),

    path('set_weights_to_pull/', views.set_weights_to_pull),

    # path('test/', views.test),

    path('', RedirectView.as_view(url='home/')),
]
