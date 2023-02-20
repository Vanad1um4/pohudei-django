from datetime import datetime, timedelta
from .models import *
import os.path
import json
import redis


### REDIS LOGIC ###############################################################

redis_instance = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
redis_instance.expire('a', 12 * 60 * 60)


def redis_set(key, value):
    try:
        redis_instance.set(key, value)
        return 'ok'
    except:
        return 'err'


def redis_get(key):
    try:
        value = redis_instance.get(key)
        return value
    except:
        return 'err'


def check_cache_for_todays_target_kcals(user_id, dates, coeffs):
    cached_target_kcals = redis_get(f'{user_id}-{dates["this_day_iso"]}')

    if not cached_target_kcals:
        _, _, _, _, target_kcals_avg, _ = stats_calc(user_id, coeffs)
        this_days_target_kcals = target_kcals_avg.get(dates['this_day'], 0)

        if this_days_target_kcals > 0:
            redis_set(f'{user_id}-{dates["this_day_iso"]}', this_days_target_kcals)
    else:
        this_days_target_kcals = cached_target_kcals

    return this_days_target_kcals


### DIARY LOGIC ###############################################################

def dates_prep_for_diary_view(date_iso: None | str) -> dict:
    dates = {}
    if date_iso == None:
        this_day = datetime.today().date()
        date_iso = this_day.strftime('%Y-%m-%d')
    else:
        this_day = datetime.fromisoformat(date_iso).date()

    dates['this_day'] = this_day
    dates['this_day_iso'] = this_day.strftime('%Y-%m-%d')
    dates['this_day_human'] = this_day.strftime('%d %b')
    prev_day = this_day - timedelta(days=1)
    dates['prev_day_iso'] = prev_day.strftime('%Y-%m-%d')
    dates['prev_day_human'] = prev_day.strftime('%d %b')
    next_day = this_day + timedelta(days=1)
    dates['next_day_iso'] = next_day.strftime('%Y-%m-%d')
    dates['next_day_human'] = next_day.strftime('%d %b')

    return dates


def make_ones_for_coefficients():
    res_catalogue_ids = db_get_catalogue_ids()
    catalogue_ids = set(sorted([x[0] for x in res_catalogue_ids[1]]))
    return {key: 1 for key in catalogue_ids}


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


def prep_food_for_diary_view(user_id, date_iso, coeffs):
    this_days_food_raw = db_get_food_from_diary(user_id, date_iso)
    this_days_food_prepped = []

    for item in this_days_food_raw:
        this_days_food_prepped.append([item[0], item[1], item[2], round(item[3] * coeffs[item[4]]), item[5]])

    return this_days_food_prepped


def prep_one_weight_for_fiary_view(user_id: int, date_iso: str) -> float | None:
    weight_res = db_get_one_weight(user_id, date_iso)

    if weight_res[0] == 'success':
        this_days_weight = weight_res[1][0]
    else:
        this_days_weight = None

    return this_days_weight


### STATS LOGIC ###############################################################

def dates_list_prep(first_date):
    human_dates = {}
    today = datetime.today().date()
    day_to_add = first_date
    while day_to_add <= today:
        human_dates[day_to_add] = None
        day_to_add = day_to_add + timedelta(days=1)
    return human_dates


def weights_prep(weights_raw, all_dates):
    weights_prepped = dict(all_dates)
    for item in weights_raw:
        weights_prepped[item[0]] = float(item[1])
    return weights_prepped


def diary_entries_prep(diary_entries_raw, all_dates):
    diary_entries_prepped = dict(all_dates)
    for row in diary_entries_raw:
        # print(row)
        if diary_entries_prepped[row[0]] == None:
            diary_entries_prepped[row[0]] = []
        diary_entries_prepped[row[0]].append((row[1], row[2]))

    return diary_entries_prepped


def catalogue_prep(catalogue):
    catalogue_prepped = {}
    for item in catalogue:
        catalogue_prepped[item[0]] = item[1]
    return catalogue_prepped


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


def target_kcals_prep(kcals, weights, n):
    kcals_keys = list(kcals.keys())
    kcals_values = list(kcals.values())
    weights_values = list(weights.values())

    list_averaged = []
    for i in range(n-1, len(kcals_values)):
        list_averaged.append((sum(kcals_values[i-n+1:i+1]) - ((weights_values[i] - weights_values[i-n+1]) * 7700)) / n)

    kcals_keys = kcals_keys[len(kcals_keys)-len(list_averaged):]
    return {k: v for k, v in zip(kcals_keys, list_averaged)}


def stats_calc(user_id, personal_coeffs):
    first_date = db_get_users_first_date(user_id)[1]
    all_dates = dates_list_prep(first_date)

    weights_raw = db_get_users_weights_all(user_id)[1]
    weights_prepped = weights_prep(weights_raw, all_dates)

    diary_entries_raw = db_get_all_diary_entries(user_id)[1]
    diary_entries_prepped = diary_entries_prep(diary_entries_raw, all_dates)

    catalogue_raw = db_get_all_catalogue_entries()[1]
    catalogue_prepped = catalogue_prep(catalogue_raw)

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


def stats_prep(all_dates_dict, eaten, weights, avg_weights, target_kcals_avg, helth):
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

    main_stats_data = {
        'helth_chart_short': {'good': prepped_helth_good_short, 'ok': prepped_helth_ok_short, 'bad': prepped_helth_bad_short},
        'helth_chart_long': {'good': prepped_helth_good_long, 'ok': prepped_helth_ok_long, 'bad': prepped_helth_bad_long},
        'weights_chart': {'normal': prepped_normal_weights, 'average': prepped_average_weights},
        'kcals_chart': {'eaten': prepped_eaten_kcals, 'target': prepped_target_kcals},
    }

    return main_stats_data

### OTHER LOGIC ###############################################################


def get_coefficients(user_id):
    personal_coeffs = {}
    res_use_coeffs = db_get_use_coeffs_bool(user_id)
    if res_use_coeffs[1][0]:
        personal_coeffs = get_and_validate_coefficients(user_id)
    else:
        personal_coeffs = make_ones_for_coefficients()

    return personal_coeffs


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
