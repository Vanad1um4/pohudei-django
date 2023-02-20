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

    _, _, _, _, target_kcals_avg, _ = stats_calc(user_id, personal_coeffs)

    this_days_target_kcals = target_kcals_avg.get(dates['this_day'], 0)

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
        return HttpResponse(json.dumps({'result': 'failure, not POST'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(json.dumps({'result': 'failure, no user_id'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')

    data = json.loads(request.body)

    result = db_update_weight_from_diary(user_id, data['date'], data['weight'])

    if result[0] == 'success':
        return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


def add_food_to_diary(request):
    if request.method == 'POST':
        user_id = request.user.profile.user_id
        data = json.loads(request.body)
        if user_id:
            result = db_add_new_diary_entry(user_id, data['date_iso'], data['food_id'], data['food_weight'])
            if result == 'success':
                return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
            else:
                return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
        else:
            return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                                content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


def update_diary_entry(request):
    if request.method == 'POST':
        user_id = request.user.profile.user_id
        data = json.loads(request.body)
        diary_id = data['diary_id']
        new_food_weight = data['new_weight']
        if user_id:
            result = db_update_diary_entry(user_id, diary_id, new_food_weight)
            if result == 'success':
                return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
            else:
                return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
        else:
            return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                                content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


def delete_diary_entry(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = request.user.profile.user_id
        diary_id = data['diary_id']
        if user_id:
            result = db_del_diary_entry(user_id, diary_id)
            if result == 'success':
                return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
            else:
                return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
        else:
            return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                                content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


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


def add_food_to_catalogue(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'result': 'failure, not POST'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(json.dumps({'result': 'failure, no user_id'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')

    data = json.loads(request.body)

    if request.user.is_staff:
        result = db_add_new_food_to_catalogue(user_id, data['food_name'], data['food_kcals'], admin=True)
    else:
        result = db_add_new_food_to_catalogue(user_id, data['food_name'], data['food_kcals'])

    if result[0] == 'success':
        return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    elif result[0] == 'duplication':
        return HttpResponse(json.dumps({'result': 'duplication'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


def update_food_in_catalogue(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'result': 'failure, not POST'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(json.dumps({'result': 'failure, no user_id'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')

    data = json.loads(request.body)

    if request.user.is_staff:
        result = db_update_food_in_catalogue(
            user_id, data['food_id'], data['food_name'], data['food_kcals'], admin=True)
    else:
        result = db_update_food_in_catalogue(user_id, data['food_id'], data['food_name'], data['food_kcals'])

    if result[0] == 'success':
        return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    elif result[0] == 'duplication':
        return HttpResponse(json.dumps({'result': 'duplication'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


def delete_food_from_catalogue(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'result': 'failure, not POST'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(json.dumps({'result': 'failure, no user_id'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')

    data = json.loads(request.body)

    result = db_delete_food_from_catalogue(data['food_id'])

    if result[0] == 'success':
        return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    if result[0] == 'in use':
        return HttpResponse(json.dumps({'result': 'in use'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


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
        return HttpResponse(json.dumps({'result': 'failure, not POST'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_id = request.user.profile.user_id
    except:
        return HttpResponse(json.dumps({'result': 'failure, no user_id'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')

    data = json.loads(request.body)
    result = db_set_all_options(user_id, data['height'], data['use_coeffs'])
    if result[0] == 'success':
        return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


##### NO PROFILE FNs ##########################################################


def noprofile(request):
    return render(request, 'main/noprofile.html')
