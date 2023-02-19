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
        date_iso = this_day.strftime('%Y-%m-%d')
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

    use_coeffs = False
    personal_coeffs = {}
    res_use_coeffs = db_get_use_coeffs_bool(user_id)
    if res_use_coeffs[1][0]:
        use_coeffs = True
        personal_coeffs = get_and_validate_coefficients(user_id)
    else:
        personal_coeffs = make_ones_for_coefficients()
    # print(personal_coeffs)

    this_days_food_raw = db_get_food_from_diary(user_id, date_iso)
    print(this_days_food_raw)
    this_days_food_prepped = []

    for item in this_days_food_raw:
        # print(item)
        this_days_food_prepped.append([item[0], item[1], item[2], round(item[3] * personal_coeffs[item[4]]), item[5]])
    # print(this_days_food_prepped)

    _, _, _, _, _, _, _, _, _, _, target_kcals_avg = stats_prep(user_id, use_coeffs)

    date_offset = -1 + days_delta_int
    this_days_target_kcals = 0
    if date_offset > -1:
        date_offset = 0
    else:
        this_days_target_kcals = target_kcals_avg[date_offset]

    weight_res = db_get_one_weight(user_id, date_iso)
    if weight_res[0] == 'success':
        this_days_weight = weight_res[1][0]
    else:
        this_days_weight = None

    all_foods = db_get_all_food_names(user_id)
    # print(all_foods)
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
    print(result)

    return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                        content_type='application/json; charset=utf-8')


def add_food_to_diary(request):
    if request.method == 'POST':
        user_id = request.user.profile.user_id
        data = json.loads(request.body)
        if user_id:
            result = db_add_new_diary_entry(user_id, data['date_iso'], data['food_id'], data['food_weight'])
            # logger.debug(f'{user_id = }, {data = }, {result = }')
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
            # logger.debug(f'{user_id = }, {data = }, {result = }')
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
            # logger.debug(f'{user_id = }, {data = }, {result = }')
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

    human_dates, helth_good_short, helth_ok_short, helth_bad_short, helth_good_long, helth_ok_long, helth_bad_long, eaten, weights, avg_weights, target_kcals_avg = stats_prep(
        user_id, use_coeffs)

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

    for i in range(len(human_dates)):
        prepped_helth_good_short.append({'x': human_dates[i], 'y': helth_good_short[i]})
        prepped_helth_ok_short.append({'x': human_dates[i], 'y': helth_ok_short[i]})
        prepped_helth_bad_short.append({'x': human_dates[i], 'y': helth_bad_short[i]})

        prepped_helth_good_long.append({'x': human_dates[i], 'y': helth_good_long[i]})
        prepped_helth_ok_long.append({'x': human_dates[i], 'y': helth_ok_long[i]})
        prepped_helth_bad_long.append({'x': human_dates[i], 'y': helth_bad_long[i]})

        prepped_normal_weights.append({'x': human_dates[i], 'y': weights[i]})
        prepped_average_weights.append({'x': human_dates[i], 'y': avg_weights[i]})

        prepped_eaten_kcals.append({'x': human_dates[i], 'y': eaten[i]})
        prepped_target_kcals.append({'x': human_dates[i], 'y': target_kcals_avg[i]})

    # logger.debug(f'{user_id = }')
    return render(request, 'main/stats.html', {'data': {
        'helth_chart_short': {'good': prepped_helth_good_short, 'ok': prepped_helth_ok_short, 'bad': prepped_helth_bad_short},
        'helth_chart_long': {'good': prepped_helth_good_long, 'ok': prepped_helth_ok_long, 'bad': prepped_helth_bad_long},
        'weights_chart': {'normal': prepped_normal_weights, 'average': prepped_average_weights},
        'kcals_chart': {'eaten': prepped_eaten_kcals, 'target': prepped_target_kcals},
    }})


def stats_calc(user_id):
    # dates = []
    human_dates = []
    weights = []
    avg_weights = []
    eaten = []
    target_kcals = []

    results_weights = db_get_users_weights_all(user_id)

    for row in results_weights[1]:
        # dates.append(row[0])
        human_dates.append(row[0].strftime("%d %b %Y"))
        weights.append(float(row[1]))
        # print(row)

    # print(len(dates))
    # print(dates)
    # print(len(weights))

    for i in human_dates:
        eaten.append(0)

    # print(len(human_dates))
    # print(len(eaten))

    sum_kcals_and_weight = db_get_everyday_sum_kcals_from_diary(user_id)[1]

    # print(len(sum_kcals_and_weight))
    # for i, row in enumerate(eaten):
    #     print(i, row)
    # for i, row in enumerate(sum_kcals_and_weight):
    #     print(i, row)

    for i, row in enumerate(sum_kcals_and_weight):
        try:
            eaten[i] = int(row[1])
        except Exception as exc:
            logger.exception(exc)

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


### NEW STATS FNs #############################################################

def diary_entries_prep(diary_entries_raw):
    diary_entries_prepped = []
    days_list = []
    this_days_date = str(diary_entries_raw[0][0])
    days_list.append(this_days_date)
    this_days_food = []
    for i, item in enumerate(diary_entries_raw):
        if this_days_date == str(item[0]):
            this_days_food.append((item[1], item[2]))
        else:
            diary_entries_prepped.append(this_days_food)
            this_days_food = [(item[1], item[2])]
            this_days_date = str(item[0])
            days_list.append(this_days_date)
        if i == len(diary_entries_raw)-1:
            diary_entries_prepped.append(this_days_food)
    return diary_entries_prepped


def weights_prep(weights_raw):
    weights_prepped = []
    for item in weights_raw:
        weights_prepped.append(float(item[1]))
    return weights_prepped


def human_dates_prep(weights_raw):
    weights_prepped = []
    for item in weights_raw:
        weights_prepped.append(item[0].strftime("%d %b %Y"))
    return weights_prepped


def catalogue_prep(catalogue):
    catalogue_prepped = {}
    for item in catalogue:
        # print(item)
        catalogue_prepped[item[0]] = item[1]
    return catalogue_prepped


def helth_prep(input_list, coeffs):
    helth_dict = {}
    for row in input_list:
        # print(row)
        if row['date'].strftime('%Y-%m-%d') not in helth_dict.keys():
            helth_dict[row['date'].strftime('%Y-%m-%d')] = {'good': 0, 'ok': 0, 'bad': 0, 'sum': 0}
        kcals_to_add = row['food_weight'] / 100 * row['kcals'] * coeffs[row['catalogue_id']]
        helth_key = row['helth']
        if helth_key == 'unknown' or helth_key == 'unset':
            helth_key = 'ok'
        helth_dict[row['date'].strftime('%Y-%m-%d')][helth_key] += kcals_to_add
        helth_dict[row['date'].strftime('%Y-%m-%d')]['sum'] += kcals_to_add

    helth_good, helth_ok, helth_bad = [], [], []
    for value in helth_dict.values():
        factor = 100 / value['sum']
        good = round(value['good'] * factor)
        bad = round(value['bad'] * factor)
        ok = 100 - good - bad
        helth_good.append(good)
        helth_ok.append(ok)
        helth_bad.append(bad)

    avg_days = 7
    # helth_good_avg = average_list(helth_good, avg_days, round_bool=True, round_places=0)
    # helth_ok_avg = average_list(helth_ok, avg_days, round_bool=True, round_places=0)
    # helth_bad_avg = average_list(helth_bad, avg_days, round_bool=True, round_places=0)
    helth_good_avg_short = average_list(helth_good, avg_days)
    helth_ok_avg_short = average_list(helth_ok, avg_days)
    helth_bad_avg_short = average_list(helth_bad, avg_days)

    avg_days = 28
    helth_good_avg_long = average_list(helth_good, avg_days)
    helth_ok_avg_long = average_list(helth_ok, avg_days)
    helth_bad_avg_long = average_list(helth_bad, avg_days)

    # return helth_good, helth_ok, helth_bad
    return helth_good_avg_short, helth_ok_avg_short, helth_bad_avg_short, helth_good_avg_long, helth_ok_avg_long, helth_bad_avg_long


def daily_sum_kcals_count(diary_entries_prepped, catalogue_prepped, personal_coeffs):
    daily_sum_kcals = []
    for i, day in enumerate(diary_entries_prepped):
        daily_sum_kcals.append(0)
        for food in day:
            daily_sum_kcals[i] += catalogue_prepped[food[0]] * personal_coeffs[food[0]] * food[1] / 100
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


def target_kcals_prep(kcals, weights, n):
    res = []
    for i in range(n-1, len(kcals)):
        res.append((sum(kcals[i-n+1:i+1]) - ((weights[i] - weights[i-n+1]) * 7700)) / n)
    return res


def list_len_offset(input_list, target_len):
    offset = target_len - len(input_list)
    res = [None for _ in range(offset)] + input_list
    return res


def stats_prep(user_id, coeffs=True):
    diary_entries_raw = db_get_all_diary_entries(user_id)[1]
    diary_entries_prepped = diary_entries_prep(diary_entries_raw)
    weights_raw = db_get_users_weights_all(user_id)[1]
    weights_prepped = weights_prep(weights_raw)
    human_dates = human_dates_prep(weights_raw)

    catalogue_raw = db_get_all_catalogue_entries()[1]
    catalogue_prepped = catalogue_prep(catalogue_raw)
    personal_coeffs = {}
    if coeffs:
        personal_coeffs = get_and_validate_coefficients(user_id)
    else:
        personal_coeffs = make_ones_for_coefficients()

    results_food_and_helth = db_get_users_diary_entries_and_helth_values(user_id)[1]
    helth_good_avg_short, helth_ok_avg_short, helth_bad_avg_short, helth_good_avg_long, helth_ok_avg_long, helth_bad_avg_long = helth_prep(
        results_food_and_helth, personal_coeffs)

    daily_sum_kcals = daily_sum_kcals_count(diary_entries_prepped, catalogue_prepped, personal_coeffs)
    daily_sum_kcals = [round(x) for x in daily_sum_kcals]
    if len(daily_sum_kcals) > len(weights_prepped):
        diff = len(daily_sum_kcals) - len(weights_prepped)
        daily_sum_kcals = daily_sum_kcals[:-diff]
    if len(daily_sum_kcals) < len(weights_prepped):
        diff = len(weights_prepped) - len(daily_sum_kcals)
        print(diff)
        for _ in range(diff):
            daily_sum_kcals.append(0)
    avg_days = 7
    # print(daily_sum_kcals)
    daily_sum_kcals_avg = average_list(daily_sum_kcals, avg_days, round_bool=True, round_places=0)
    # print(daily_sum_kcals_avg)
    weights_prepped_avg = average_list(weights_prepped, avg_days, True, 1)
    norm_days = 30
    target_kcals = target_kcals_prep(daily_sum_kcals_avg, weights_prepped_avg, norm_days)
    target_kcals_avg = average_list(target_kcals, norm_days, True, 0)
    weights_prepped_avg = list_len_offset(weights_prepped_avg, len(human_dates))
    target_kcals_avg = list_len_offset(target_kcals_avg, len(human_dates))
    # print(len(human_dates), len(weights_prepped), len(weights_prepped_avg), len(daily_sum_kcals), len(target_kcals_avg))
    return human_dates, helth_good_avg_short, helth_ok_avg_short, helth_bad_avg_short, helth_good_avg_long, helth_ok_avg_long, helth_bad_avg_long, daily_sum_kcals, weights_prepped, weights_prepped_avg, target_kcals_avg


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
    # print(data)
    result = db_set_all_options(user_id, data['height'], data['use_coeffs'])
    # print(result)
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
    # print(type(catalogue_ids))

    users_coeffs = {}
    try:
        users_coeffs = json.loads(res_coeffs[1][0])
        users_coeffs = {int(key): value for key, value in users_coeffs.items()}
        users_coeffs_ids = set(sorted([x for x in users_coeffs.keys()]))
        # print(len(catalogue_ids), len(users_coeffs_ids))
        # print(catalogue_ids, users_coeffs_ids)

        if len(catalogue_ids) > len(users_coeffs_ids):
            diff = catalogue_ids - users_coeffs_ids
            # print(diff)
            for key in diff:
                users_coeffs[key] = 1.0
            # print(len(catalogue_ids), len(users_coeffs.keys()))
            users_coeffs_str = json.dumps(users_coeffs)
            db_set_users_coefficients(user_id, users_coeffs_str)

        if len(users_coeffs_ids) > len(catalogue_ids):
            diff = users_coeffs_ids - catalogue_ids
            # print(diff)
            for key in diff:
                del users_coeffs[key]
            # print(len(catalogue_ids), len(users_coeffs.keys()))
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
    # logger.debug(f'')
    return render(request, 'main/noprofile.html')


##### BACKUP FUNCTIONS ########################################################


def backup():
    yesterday = datetime.today().date() - timedelta(days=1)
    date_iso = yesterday.strftime("%Y-%m-%d")
    # logger.debug(f'executed')
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
        # logger.debug(f'created')
