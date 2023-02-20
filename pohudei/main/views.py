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

    dates = {}
    if date_iso == None:
        this_day = datetime.today().date()
        date_iso = this_day.strftime('%Y-%m-%d')
    else:
        this_day = datetime.fromisoformat(date_iso).date()

    dates['this_day_iso'] = this_day.strftime('%Y-%m-%d')
    dates['this_day_human'] = this_day.strftime('%d %b')
    prev_day = this_day - timedelta(days=1)
    dates['prev_day_iso'] = prev_day.strftime('%Y-%m-%d')
    dates['prev_day_human'] = prev_day.strftime('%d %b')
    next_day = this_day + timedelta(days=1)
    dates['next_day_iso'] = next_day.strftime('%Y-%m-%d')
    dates['next_day_human'] = next_day.strftime('%d %b')

    use_coeffs = False
    personal_coeffs = {}
    res_use_coeffs = db_get_use_coeffs_bool(user_id)
    if res_use_coeffs[1][0]:
        use_coeffs = True
        personal_coeffs = get_and_validate_coefficients(user_id)
    else:
        personal_coeffs = make_ones_for_coefficients()

    this_days_food_raw = db_get_food_from_diary(user_id, date_iso)
    this_days_food_prepped = []

    for item in this_days_food_raw:
        this_days_food_prepped.append([item[0], item[1], item[2], round(item[3] * personal_coeffs[item[4]]), item[5]])

    _, _, _, _, target_kcals_avg, _ = stats_prep(user_id, use_coeffs)

    this_days_target_kcals = target_kcals_avg.get(this_day, 0)

    weight_res = db_get_one_weight(user_id, date_iso)
    if weight_res[0] == 'success':
        this_days_weight = weight_res[1][0]
    else:
        this_days_weight = None

    all_foods = db_get_all_food_names(user_id)
    height = db_get_height(user_id)

    return render(request, 'main/diary.html', {'data': {
        'dates': dates, 'this_days_food': this_days_food_prepped, 'this_days_target_kcals': this_days_target_kcals, 'this_days_weight': this_days_weight, 'height': height[1][0], 'all_foods': all_foods
    }})


def update_weight(request):
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

    return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
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

    use_coeffs = False
    res_use_coeffs = db_get_use_coeffs_bool(user_id)
    if res_use_coeffs[1][0]:
        use_coeffs = True

    all_dates_dict, eaten, weights, avg_weights, target_kcals_avg, helth = stats_prep(user_id, use_coeffs)

    prepped_helth_good_short = []
    prepped_helth_ok_short = []
    prepped_helth_bad_short = []
    prepped_helth_good_long = []
    prepped_helth_ok_long = []
    prepped_helth_bad_long = []
    prepped_normal_weights = []
    prepped_average_weights = []
    prepped_eaten_kcals = []
    prepped_target_kcals = []

    for date in list(all_dates_dict.keys()):
        prepped_helth_good_short.append({'x': date.strftime('%d %b %Y'), 'y': helth['short']['good'].get(date, None)})
        prepped_helth_ok_short.append({'x': date.strftime('%d %b %Y'), 'y': helth['short']['ok'].get(date, None)})
        prepped_helth_bad_short.append({'x': date.strftime('%d %b %Y'), 'y': helth['short']['bad'].get(date, None)})

        prepped_helth_good_long.append({'x': date.strftime('%d %b %Y'), 'y': helth['long']['good'].get(date, None)})
        prepped_helth_ok_long.append({'x': date.strftime('%d %b %Y'), 'y': helth['long']['ok'].get(date, None)})
        prepped_helth_bad_long.append({'x': date.strftime('%d %b %Y'), 'y': helth['long']['bad'].get(date, None)})

        prepped_normal_weights.append({'x': date.strftime('%d %b %Y'), 'y': weights.get(date, None)})
        prepped_average_weights.append({'x': date.strftime('%d %b %Y'), 'y': avg_weights.get(date, None)})

        prepped_eaten_kcals.append({'x': date.strftime('%d %b %Y'), 'y': eaten.get(date, None)})
        prepped_target_kcals.append({'x': date.strftime('%d %b %Y'), 'y': target_kcals_avg.get(date, None)})

    return render(request, 'main/stats.html', {'data': {
        'helth_chart_short': {'good': prepped_helth_good_short, 'ok': prepped_helth_ok_short, 'bad': prepped_helth_bad_short},
        'helth_chart_long': {'good': prepped_helth_good_long, 'ok': prepped_helth_ok_long, 'bad': prepped_helth_bad_long},
        'weights_chart': {'normal': prepped_normal_weights, 'average': prepped_average_weights},
        'kcals_chart': {'eaten': prepped_eaten_kcals, 'target': prepped_target_kcals},
    }})


def stats_calc(user_id):
    human_dates = []
    weights = []
    avg_weights = []
    eaten = []
    target_kcals = []

    results_weights = db_get_users_weights_all(user_id)

    for row in results_weights[1]:
        human_dates.append(row[0].strftime("%d %b %Y"))
        weights.append(float(row[1]))

    for i in human_dates:
        eaten.append(0)

    sum_kcals_and_weight = db_get_everyday_sum_kcals_from_diary(user_id)[1]

    for i, row in enumerate(sum_kcals_and_weight):
        try:
            eaten[i] = int(row[1])
        except Exception as exc:
            logger.exception(exc)

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


### NEW STATS FNs #############################################################

def diary_entries_prep(diary_entries_raw, all_dates):
    diary_entries_prepped = dict(all_dates)
    for row in diary_entries_raw:
        # print(row)
        if diary_entries_prepped[row[0]] == None:
            diary_entries_prepped[row[0]] = []
        diary_entries_prepped[row[0]].append((row[1], row[2]))

    return diary_entries_prepped


def weights_prep(weights_raw, all_dates):
    weights_prepped = dict(all_dates)
    for item in weights_raw:
        weights_prepped[item[0]] = float(item[1])
    return weights_prepped


def dates_list_prep(first_date):
    human_dates = {}
    today = datetime.today().date()
    day_to_add = first_date
    while day_to_add <= today:
        human_dates[day_to_add] = None
        day_to_add = day_to_add + timedelta(days=1)
    return human_dates


def catalogue_prep(catalogue):
    catalogue_prepped = {}
    for item in catalogue:
        catalogue_prepped[item[0]] = item[1]
    return catalogue_prepped


def helth_prep(input_list, coeffs):
    helth_dict = {}
    for row in input_list:
        if row['date'] not in helth_dict.keys():
            helth_dict[row['date']] = {'good': 0, 'ok': 0, 'bad': 0, 'sum': 0}
        kcals_to_add = row['food_weight'] / 100 * row['kcals'] * coeffs[row['catalogue_id']]
        helth_key = row['helth']
        if helth_key == 'unknown' or helth_key == 'unset':
            helth_key = 'ok'
        helth_dict[row['date']][helth_key] += kcals_to_add
        helth_dict[row['date']]['sum'] += kcals_to_add

    helth_dict_keys = list(helth_dict.keys())

    helth_good, helth_ok, helth_bad = [], [], []
    for value in helth_dict.values():
        factor = 100 / value['sum']
        good = round(value['good'] * factor)
        bad = round(value['bad'] * factor)
        ok = 100 - good - bad
        helth_good.append(good)
        helth_ok.append(ok)
        helth_bad.append(bad)

    # avg_days = 1
    # helth_good_avg = average_list(helth_good, avg_days, round_bool=True, round_places=0)
    # helth_ok_avg = average_list(helth_ok, avg_days, round_bool=True, round_places=0)
    # helth_bad_avg = average_list(helth_bad, avg_days, round_bool=True, round_places=0)

    avg_days = 7
    helth_good_avg_long = average_list(helth_good, avg_days)
    helth_ok_avg_long = average_list(helth_ok, avg_days)
    helth_bad_avg_long = average_list(helth_bad, avg_days)

    result_dict = {'short': {'good': {}, 'ok': {}, 'bad': {}}, 'long': {'good': {}, 'ok': {}, 'bad': {}}}
    for i, key in enumerate(helth_dict_keys):
        result_dict['short']['good'][key] = helth_good[i]
        result_dict['short']['ok'][key] = helth_ok[i]
        result_dict['short']['bad'][key] = helth_bad[i]
        result_dict['long']['good'][key] = helth_good_avg_long[i]
        result_dict['long']['ok'][key] = helth_ok_avg_long[i]
        result_dict['long']['bad'][key] = helth_bad_avg_long[i]

    return result_dict


def daily_sum_kcals_count(diary_entries_prepped, catalogue_prepped, personal_coeffs, all_dates):
    daily_sum_kcals = dict(all_dates)
    for key, value in diary_entries_prepped.items():

        if daily_sum_kcals[key] == None:
            daily_sum_kcals[key] = 0

        if value != None:
            for food in value:
                daily_sum_kcals[key] += catalogue_prepped[food[0]] * personal_coeffs[food[0]] * food[1] / 100

    return daily_sum_kcals


def average_list(input_list, avg_range, round_bool=False, round_places=0):
    res = []

    # Не уменьшает итоговый список, считает среднее из доступного кол-ва чисел, если оных меньше avg_range
    for i in range(1, len(input_list)+1):
        j = 0 if i - avg_range <= 0 else i - avg_range
        if round_bool and round_places > 0:
            res.append(round(sum(input_list[j:i]) / (i - j), round_places))
        elif round_bool and round_places == 0:
            res.append(int(sum(input_list[j:i]) / (i - j)))
        else:
            res.append(sum(input_list[j:i]) / (i - j))

    # Уменьшает итоговый список на avg_range-1, зато считает среднее из подсписков длиной == avg_range
    # for i in range(avg_range-1, len(input_list)):
    #     if round_bool and round_places > 0:
    #         res.append(round(sum(input_list[i-avg_range+1:i+1]) / avg_range, round_places))
    #     elif round_bool and round_places == 0:
    #         res.append(int(sum(input_list[i-avg_range+1:i+1]) / avg_range))
    #     else:
    #         res.append(sum(input_list[i-avg_range+1:i+1]) / avg_range)

    return res


def average_dict(input_dict, avg_range, round_bool=False, round_places=0):
    input_dict_keys = list(input_dict.keys())
    input_dict_values = list(input_dict.values())

    list_averaged = []
    for i in range(1, len(input_dict_values)+1):
        j = 0 if i - avg_range <= 0 else i - avg_range
        if round_bool and round_places > 0:
            list_averaged.append(round(sum(input_dict_values[j:i]) / (i - j), round_places))
        elif round_bool and round_places == 0:
            list_averaged.append(int(sum(input_dict_values[j:i]) / (i - j)))
        else:
            list_averaged.append(sum(input_dict_values[j:i]) / (i - j))

    return {k: v for k, v in zip(input_dict_keys, list_averaged)}


def target_kcals_prep(kcals, weights, n):
    kcals_keys = list(kcals.keys())
    kcals_values = list(kcals.values())
    weights_values = list(weights.values())

    list_averaged = []
    for i in range(n-1, len(kcals_values)):
        list_averaged.append((sum(kcals_values[i-n+1:i+1]) - ((weights_values[i] - weights_values[i-n+1]) * 7700)) / n)

    kcals_keys = kcals_keys[len(kcals_keys)-len(list_averaged):]
    return {k: v for k, v in zip(kcals_keys, list_averaged)}


def list_len_offset(input_list, target_len):
    offset = target_len - len(input_list)
    res = [None for _ in range(offset)] + input_list
    return res


def stats_prep(user_id, coeffs=True):
    first_date = db_get_users_first_date(user_id)[1]
    all_dates = dates_list_prep(first_date)

    weights_raw = db_get_users_weights_all(user_id)[1]
    weights_prepped = weights_prep(weights_raw, all_dates)

    diary_entries_raw = db_get_all_diary_entries(user_id)[1]
    diary_entries_prepped = diary_entries_prep(diary_entries_raw, all_dates)

    catalogue_raw = db_get_all_catalogue_entries()[1]
    catalogue_prepped = catalogue_prep(catalogue_raw)
    personal_coeffs = {}
    if coeffs:
        personal_coeffs = get_and_validate_coefficients(user_id)
    else:
        personal_coeffs = make_ones_for_coefficients()

    results_food_and_helth = db_get_users_diary_entries_and_helth_values(user_id)[1]
    helth_dict = helth_prep(results_food_and_helth, personal_coeffs)

    daily_sum_kcals = daily_sum_kcals_count(diary_entries_prepped, catalogue_prepped, personal_coeffs, all_dates)

    avg_days = 7
    daily_sum_kcals_avg = average_dict(daily_sum_kcals, avg_days, round_bool=True, round_places=0)
    weights_prepped_avg = average_dict(weights_prepped, avg_days, round_bool=True, round_places=1)

    norm_days = 30
    target_kcals = target_kcals_prep(daily_sum_kcals_avg, weights_prepped_avg, norm_days)
    target_kcals_avg = average_dict(target_kcals, norm_days, round_bool=True, round_places=0)

    return all_dates, daily_sum_kcals, weights_prepped, weights_prepped_avg, target_kcals_avg, helth_dict


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


##### PERSONAL COEFFICIENTS ###################################################

def get_and_validate_coefficients(user_id: int) -> dict:
    res_catalogue_ids = db_get_catalogue_ids()
    res_coeffs = db_get_users_coefficients(user_id)

    catalogue_ids = set(sorted([x[0] for x in res_catalogue_ids[1]]))

    users_coeffs = {}
    try:
        users_coeffs = json.loads(res_coeffs[1][0])
        users_coeffs = {int(key): value for key, value in users_coeffs.items()}
        users_coeffs_ids = set(sorted([x for x in users_coeffs.keys()]))

        if len(catalogue_ids) > len(users_coeffs_ids):
            diff = catalogue_ids - users_coeffs_ids
            for key in diff:
                users_coeffs[key] = 1.0
            users_coeffs_str = json.dumps(users_coeffs)
            db_set_users_coefficients(user_id, users_coeffs_str)

        if len(users_coeffs_ids) > len(catalogue_ids):
            diff = users_coeffs_ids - catalogue_ids
            for key in diff:
                del users_coeffs[key]
            users_coeffs_str = json.dumps(users_coeffs)
            db_set_users_coefficients(user_id, users_coeffs_str)

    except:
        users_coeffs = {key: 1.0 for key in catalogue_ids}
        users_coeffs_str = json.dumps(users_coeffs)
        db_set_users_coefficients(user_id, users_coeffs_str)

    return users_coeffs


def make_ones_for_coefficients():
    res_catalogue_ids = db_get_catalogue_ids()
    catalogue_ids = set(sorted([x[0] for x in res_catalogue_ids[1]]))
    return {key: 1 for key in catalogue_ids}


##### NO PROFILE FNs ##########################################################


def noprofile(request):
    return render(request, 'main/noprofile.html')


##### BACKUP FUNCTIONS ########################################################


def backup():
    yesterday = datetime.today().date() - timedelta(days=1)
    date_iso = yesterday.strftime("%Y-%m-%d")
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
        with open(f'data_backup/{date_iso}.txt', 'w', encoding='utf-8') as f:
            json.dump(result_list, f, ensure_ascii=False, indent=4)
