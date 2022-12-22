# TODO: standartize time throughout app
# TODO: improve logging

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import *
from .log import *
import os.path
import locale
import json

locale.setlocale(locale.LC_ALL, "ru_RU.utf8")

logger = get_logger()  # pyright: ignore


def home(request):
    if request.user.is_authenticated:
        # return render(request, 'main/index.html')
        return redirect('home')
    return redirect('login')


### WEIGHT FNs ################################################################


# def weight(request):
#     backup()
#     if request.user.is_authenticated:
#         user_id = request.user.profile.user_id
#         weights_to_pull = request.user.profile.weights_to_pull
#         if user_id:
#             results = db_get_last_weights(user_id, weights_to_pull)
#             logger.debug(f'{user_id = }, {weights_to_pull = }, {results = }')
#             return render(request, 'main/weight.html', {'data': results[1]})
#         return redirect('home')
#     return redirect('login')


# def update_weight(request):
#     if request.user.is_authenticated:
#         user_id = request.user.profile.user_id
#         if user_id:
#             data = json.loads(request.body)
#             result = db_update_weight(user_id, data['weight_id'], data['weight'])
#             logger.debug(f'{user_id = }, {data = }, {result = }')
#             if result[0] == 'success':
#                 return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
#                                     content_type='application/json; charset=utf-8')
#         else:
#             return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
#                                 content_type='application/json; charset=utf-8')
#     else:
#         return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
#                             content_type='application/json; charset=utf-8')


# def delete_weight(request):
#     if request.user.is_authenticated:
#         user_id = request.user.profile.user_id
#         if user_id:
#             data = json.loads(request.body)
#             result = db_delete_weight(user_id, data['weight_id'])
#             logger.debug(f'{user_id = }, {data = }, {result = }')
#             if result[0] == 'success':
#                 return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
#                                     content_type='application/json; charset=utf-8')
#         else:
#             return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
#                                 content_type='application/json; charset=utf-8')
#     else:
#         return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
#                             content_type='application/json; charset=utf-8')


### DIARY FNs #################################################################

def diary(request, date_iso=None):
    backup()
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        user_id = request.user.profile.user_id
    except:
        return redirect('noprofile')

    dates = {}
    if date_iso == None:
        this_day = datetime.today().date()
        days_delta_int = 0
    else:
        this_day = datetime.fromisoformat(date_iso).date()
        date_delta = this_day - datetime.today().date()
        days_delta_int = date_delta.days
    dates['this_day_iso'] = this_day.strftime('%Y-%m-%d')
    dates['this_day_human'] = this_day.strftime('%d %b')
    prev_day = this_day - timedelta(days=1)
    dates['prev_day_iso'] = prev_day.strftime('%Y-%m-%d')
    dates['prev_day_human'] = prev_day.strftime('%d %b')
    next_day = this_day + timedelta(days=1)
    dates['next_day_iso'] = next_day.strftime('%Y-%m-%d')
    dates['next_day_human'] = next_day.strftime('%d %b')

    if date_iso == None:
        today = datetime.today()
        date_iso = today.strftime('%Y-%m-%d')

    this_days_food = db_get_food_from_diary(user_id, date_iso)

    _, _, _, _, target_kcals = stats_calc(user_id)
    if len(target_kcals) <= 60:
        target_kcals = list(list_averaged(target_kcals, 3, True, 0))
    if len(target_kcals) > 60:
        target_kcals = list(list_averaged(target_kcals, 14, True, 0))
    try:
        offset = -2 + days_delta_int
        this_days_target_kcals = target_kcals[offset]
    except:
        this_days_target_kcals = 0

    result = db_get_one_weight(user_id, date_iso)
    # print(result)
    if result[0] == 'success':
        this_days_weight = result[1][0][2]
    else:
        this_days_weight = None

    all_foods = db_get_all_food_names(user_id)

    logger.debug(f'{user_id = }, {this_days_food = }, {this_days_target_kcals = }')
    return render(request, 'main/diary.html', {'data': {
        'dates': dates, 'this_days_food': this_days_food, 'this_days_target_kcals': this_days_target_kcals, 'this_days_weight': this_days_weight, 'all_foods': all_foods
    }})
    # return render(request, 'main/diary.html', {'data': {
    #     'dates': dates, 'this_days_date': date_iso, 'this_days_food': this_days_food,
    #     'this_days_target_kcals': this_days_target_kcals, 'this_days_weight': this_days_weight, 'all_foods': all_foods
    # }})


def update_weight_new(request):
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
    print(result)

    return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                        content_type='application/json; charset=utf-8')


def add_food_to_diary(request):
    if request.method == 'POST':
        user_id = request.user.profile.user_id
        data = json.loads(request.body)
        if user_id:
            result = db_add_new_diary_entry(user_id, data['date_iso'], data['food_id'], data['food_weight'])
            logger.debug(f'{user_id = }, {data = }, {result = }')
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
            logger.debug(f'{user_id = }, {data = }, {result = }')
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
            logger.debug(f'{user_id = }, {data = }, {result = }')
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

    human_dates, eaten, weights, avg_weights, target_kcals = stats_calc(user_id)

    # print('===///===')
    # print(len(human_dates))
    # print(len(eaten))
    # print(len(weights))
    # print(len(avg_weights))
    # print(len(target_kcals))

    # print(human_dates)
    # print(weights)
    # print(avg_weights)
    # print(eaten)
    # print(target_kcals)

    if len(target_kcals) <= 60:
        target_kcals = list(list_averaged(target_kcals, 3, True, 0))
        for i, _ in enumerate(target_kcals):
            if i + 1 < len(target_kcals) / 2:
                target_kcals[i] = None

    if len(target_kcals) > 60:
        target_kcals = list(list_averaged(target_kcals, 14, True, 0))
        for i, _ in enumerate(target_kcals):
            if i < 30:
                target_kcals[i] = None

    # print(target_kcals)

    prepped_normal_weights = []
    prepped_average_weights = []
    prepped_eaten_kcals = []
    prepped_target_kcals = []

    for i in range(len(human_dates)):
        prepped_normal_weights.append({'x': human_dates[i], 'y': weights[i]})
        prepped_average_weights.append({'x': human_dates[i], 'y': avg_weights[i]})

        prepped_eaten_kcals.append({'x': human_dates[i], 'y': eaten[i]})
        prepped_target_kcals.append({'x': human_dates[i], 'y': target_kcals[i]})

    logger.debug(f'{user_id = }')
    return render(request, 'main/stats.html', {'data': {
        'weights_chart': {'normal': prepped_normal_weights, 'average': prepped_average_weights},
        'kcals_chart': {'eaten': prepped_eaten_kcals, 'target': prepped_target_kcals},
    }})


def stats_calc(user_id):
    dates = []
    human_dates = []
    weights = []
    avg_weights = []
    eaten = []
    target_kcals = []

    results = db_get_users_weights_all(user_id)

    for row in results[1]:
        dates.append(row[0])
        human_dates.append(row[0].strftime("%d %b %Y"))
        weights.append(float(row[1]))

    # print(len(dates))
    # print(len(weights))

    for i in human_dates:
        eaten.append(0)

    sum_kcals_and_weight = db_get_everyday_sum_kcals_from_diary(user_id)
    for i, row in enumerate(sum_kcals_and_weight):
        # eaten.append(int(row[1]))
        eaten[i] = int(row[1])

    # print('===///===')
    # print(len(human_dates))
    # print(len(eaten))
    # print(len(weights))

    target_kcals.append(0)
    for i, _ in enumerate(human_dates):
        j = 0
        if i - 6 > 0:
            j = i - 6
        tmp_weights_list = weights[j:i+1]
        tmp_weights_sum = sum(tmp_weights_list)
        tmp_avg_weight = round(tmp_weights_sum / len(tmp_weights_list), 2)
        avg_weights.append(tmp_avg_weight)

        k = 0
        if i - 30 > 0:
            k = i - 30
        tmp_eaten_list = eaten[k:i+1]
        tmp_eaten_sum = sum(tmp_eaten_list)

        num_of_days = i - k
        if num_of_days == 0:
            num_of_days = 1
        tmp_target_kcals = round((tmp_eaten_sum - ((avg_weights[i] - avg_weights[k]) * 7700)) / num_of_days)
        target_kcals.append(tmp_target_kcals)

    return human_dates, eaten, weights, avg_weights, target_kcals


def list_averaged(init_list, avg_range, round_bool=False, round_places=0):
    result_list = []
    for i, _ in enumerate(init_list):
        j = 0
        if i - avg_range+1 > 0:
            j = i - avg_range+1
        tmp_avg_list = init_list[j:i+1]
        # print(tmp_avg_list)
        tmp_avg_sum = sum(tmp_avg_list)
        if round_bool == True:
            tmp_result_value = round(tmp_avg_sum / len(tmp_avg_list), round_places)
            if round_places == 0:
                tmp_result_value = int(tmp_result_value)
        else:
            tmp_result_value = tmp_avg_sum / len(tmp_avg_list)
        result_list.append(tmp_result_value)
    return result_list


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
    print(result)

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


### OPTIONS FNs ###############################################################

# def options(request):
#     if not request.user.is_authenticated:
#         return redirect('login')
#
#     try:
#         user_id = request.user.profile.user_id
#     except:
#         return redirect('noprofile')
#
#     results = db_get_options(user_id)
#     logger.debug(f'{user_id = }, {results = }')
#     return render(request, 'main/options.html', {'data': results[1]})


# def set_weights_to_pull(request):
#     if not request.user.is_authenticated:
#         return redirect('login')
#
#     if request.method != 'POST':
#         return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
#                             content_type='application/json; charset=utf-8')
#     try:
#         user_id = request.user.profile.user_id
#     except:
#         return redirect('noprofile')
#
#     data = json.loads(request.body)
#     results = db_set_weights_to_pull(user_id, data['weights_to_pull'])
#     # print(results)
#     logger.debug(f'{user_id = }, {data = }, {results = }')
#     if results[0] == 'success':
#         return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
#                             content_type='application/json; charset=utf-8')
#     else:
#         return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
#                             content_type='application/json; charset=utf-8')


##### NO PROFILE FNs ##########################################################


def noprofile(request):
    logger.debug(f'')
    return render(request, 'main/noprofile.html')


##### BACKUP FUNCTIONS ########################################################


def backup():
    yesterday = datetime.today().date() - timedelta(days=1)
    date_iso = yesterday.strftime("%Y-%m-%d")
    logger.debug(f'executed')
    # if True:
    if not os.path.isfile(f'data_backup/{date_iso}.txt'):
        food, weights = db_backup(date_iso)[1]
        result_list = []
        for i in food:
            row = {}
            row['diary_id'] = i['diary_id']
            row['users_id'] = i['users_id']
            row['date'] = i['date'].strftime("%Y-%m-%d")
            row['catalogue_id'] = i['catalogue_id']
            row['food_weight'] = i['food_weight']
            row['food_id'] = i['id']
            row['name'] = i['name']
            row['kcals'] = i['kcals']
            row['calc_kcals'] = int(i['calc_kcals'])
            result_list.append(row)
        for i in weights:
            row = {}
            row['weight_id'] = i['id']
            row['users_id'] = i['users_id']
            row['date'] = i['date'].strftime("%Y-%m-%d")
            row['weight'] = float(i['weight'])
            result_list.append(row)
        # print(result_list)
        # with open(f'data_backup/{date_iso}-all.txt', 'w', encoding='utf-8') as f:
        with open(f'data_backup/{date_iso}.txt', 'w', encoding='utf-8') as f:
            json.dump(result_list, f, ensure_ascii=False, indent=4)
        logger.debug(f'created')
