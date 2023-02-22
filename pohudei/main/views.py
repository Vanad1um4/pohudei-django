# TODO: improve logging

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import *
from .logic import *
from .log import *
import locale
import json

locale.setlocale(locale.LC_ALL, "ru_RU.utf8")

logger = get_logger()  # pyright: ignore


def home(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('login')


### DIARY FNs #################################################################

def diary(request, date_iso=None):
    backup()
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_id = request.user.profile.user_id
    except:
        return redirect('noprofile')

    dates = dates_prep_for_diary_view(date_iso)

    personal_coeffs = get_coefficients(user_id)

    this_days_food_prepped = prep_food_for_diary_view(user_id, dates['this_day_iso'], personal_coeffs)

    this_days_target_kcals = check_cache_for_todays_target_kcals(user_id, dates, personal_coeffs)

    this_days_weight = prep_one_weight_for_fiary_view(user_id, dates['this_day_iso'])

    all_foods = db_get_all_food_names(user_id)[1]

    height = db_get_height(user_id)[1]

    return render(request, 'main/diary.html', {'data': {
        'dates': dates,
        'this_days_food': this_days_food_prepped,
        'this_days_target_kcals': this_days_target_kcals,
        'this_days_weight': this_days_weight,
        'height': height[0],
        'all_foods': all_foods
    }})


def update_weight_ajax(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(status=401)

    data = json.loads(request.body)
    result = db_update_weight_from_diary(user_id, data['date'], data['weight'])

    if result[0] == 'success':
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)


def add_food_to_diary_ajax(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(status=401)

    data = json.loads(request.body)
    result = db_add_new_diary_entry(user_id, data['date_iso'], data['food_id'], data['food_weight'])

    if result[0] == 'success':
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)


def update_diary_entry_ajax(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(status=401)

    data = json.loads(request.body)
    result = db_update_diary_entry(user_id, data['diary_id'], data['new_weight'])

    if result[0] == 'success':
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)


def delete_diary_entry_ajax(request):
    if request.method != 'DELETE':
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(status=401)

    data = json.loads(request.body)
    result = db_del_diary_entry(user_id, data['diary_id'])

    if result[0] == 'success':
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)


### STATS FNs #################################################################

def stats(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        user_id = request.user.profile.user_id
    except:
        return redirect('noprofile')

    personal_coeffs = get_coefficients(user_id)

    all_dates_dict, eaten, weights, avg_weights, target_kcals_avg, helth = stats_calc(user_id, personal_coeffs)

    main_stats_data = stats_prep(all_dates_dict, eaten, weights, avg_weights, target_kcals_avg, helth)

    return render(request, 'main/stats.html', {'data': main_stats_data})


### CATALOGUE FNs #############################################################

def foods(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_id = request.user.profile.user_id
    except:
        return redirect('noprofile')

    if request.user.is_staff:
        foods = db_get_users_food_names(user_id, True)[1]
    else:
        foods = db_get_users_food_names(user_id)[1]
    return render(request, 'main/foods.html', {'data': {'foods': foods}})


def add_food_to_catalogue_ajax(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(status=401)

    data = json.loads(request.body)

    isAdmin = False
    if request.user.is_staff:
        isAdmin = True

    result = db_add_new_food_to_catalogue(user_id, data['food_name'], data['food_kcals'], admin=isAdmin)

    if result[0] == 'success':
        return HttpResponse(status=204)
    elif result[0] == 'duplication':
        return HttpResponse(status=409)
    else:
        return HttpResponse(status=400)


def update_food_in_catalogue_ajax(request):
    if request.method != 'PUT':
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(status=401)

    data = json.loads(request.body)

    isAdmin = False
    if request.user.is_staff:
        isAdmin = True

    result = db_update_food_in_catalogue(user_id, data['food_id'], data['food_name'], data['food_kcals'], admin=isAdmin)

    if result[0] == 'success':
        return HttpResponse(status=204)
    elif result[0] == 'duplication':
        return HttpResponse(status=409)
    else:
        return HttpResponse(status=400)


def delete_food_from_catalogue_ajax(request):
    if request.method != 'DELETE':
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(status=401)

    data = json.loads(request.body)

    result = db_delete_food_from_catalogue(data['food_id'])

    if result[0] == 'success':
        return HttpResponse(status=204)
    elif result[0] == 'in use':
        return HttpResponse(status=409)
    else:
        return HttpResponse(status=400)


##### OPTIONS FNs #############################################################


def options(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_id = request.user.profile.user_id
    except:
        return redirect('noprofile')

    results = db_get_all_options(user_id)
    return render(request, 'main/options.html', {'data': results[1]})


def set_options_ajax(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(status=401)

    data = json.loads(request.body)

    result = db_set_all_options(user_id, data['height'], data['use_coeffs'])

    if result[0] == 'success':
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)


##### NO PROFILE FNs ##########################################################


def noprofile(request):
    return render(request, 'main/noprofile.html')
