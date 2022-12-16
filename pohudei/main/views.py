# TODO: standartize time throughout app
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


def weight(request):
    backup()
    if request.user.is_authenticated:
        user_id = request.user.profile.user_id
        weights_to_pull = request.user.profile.weights_to_pull
        if user_id:
            results = db_get_last_weights(user_id, weights_to_pull)
            logger.debug(f'{user_id = }, {weights_to_pull = }, {results = }')
            return render(request, 'main/weight.html', {'data': results[1]})
        return redirect('home')
    return redirect('login')


def add_new_weight(request):
    if request.user.is_authenticated:
        user_id = request.user.profile.user_id
        if user_id:
            data = json.loads(request.body)
            result = db_add_new_weight(user_id, data['date'], data['weight'])
            logger.debug(f'{user_id = }, {data = }, {result = }')
            if result[0] == 'success':
                return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
            elif result[0] == 'duplication':
                return HttpResponse(json.dumps({'result': 'duplication'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
        else:
            return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                                content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


def update_weight(request):
    if request.user.is_authenticated:
        user_id = request.user.profile.user_id
        if user_id:
            data = json.loads(request.body)
            result = db_update_weight(user_id, data['weight_id'], data['weight'])
            logger.debug(f'{user_id = }, {data = }, {result = }')
            if result[0] == 'success':
                return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
        else:
            return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                                content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


def delete_weight(request):
    if request.user.is_authenticated:
        user_id = request.user.profile.user_id
        if user_id:
            data = json.loads(request.body)
            result = db_delete_weight(user_id, data['weight_id'])
            logger.debug(f'{user_id = }, {data = }, {result = }')
            if result[0] == 'success':
                return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                                    content_type='application/json; charset=utf-8')
        else:
            return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                                content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


### DIARY FNs #################################################################


# TODO: Optimise this sh*t
def diary(request):
    if request.user.is_authenticated:
        user_id = request.user.profile.user_id
        if user_id:
            eaten = []
            weights = []
            sum_kcals_and_weight = db_get_everyday_sum_kcals_from_diary(user_id)
            for row in sum_kcals_and_weight:
                eaten.append(float(row[1]))
                weights.append(float(row[2]))

            avg_weights = []
            target_kcals = []
            target_kcals.append(0)
            for i, _ in enumerate(sum_kcals_and_weight):
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

            if len(target_kcals) <= 60:
                target_kcals = list(list_averaged(target_kcals, 3, True, 0))

            if len(target_kcals) > 60:
                target_kcals = list(list_averaged(target_kcals, 14, True, 0))

            try:
                todays_target_kcals = target_kcals[-2]
            except:
                todays_target_kcals = 0

            today_food = db_get_today_food_from_diary(user_id)
            all_foods = db_get_food_names()

            logger.debug(f'{user_id = }, {today_food = }, {todays_target_kcals = }')
            return render(request, 'main/diary.html', {'data': [today_food, todays_target_kcals, all_foods]})
        return redirect('home')
    return redirect('login')


def add_food_to_diary(request):
    if request.method == 'POST':
        user_id = request.user.profile.user_id
        data = json.loads(request.body)
        if user_id:
            today = datetime.today()
            today_str = today.strftime("%Y-%m-%d")
            # yesterday = datetime.today() - timedelta(days=1)  # TODO: make food addition for different dates

            result = db_add_new_diary_entry(user_id, today_str, data['food_id'], data['food_weight'])
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

    # results = db_get_basic_stats(user_id)
    # dates = []
    # weights = []
    # for i in results[1]:
    #     dates.append(i[0])
    #     weights.append(i[1])

    human_dates = []
    eaten = []
    weights = []
    sum_kcals_and_weight = db_get_everyday_sum_kcals_from_diary(user_id)
    for row in sum_kcals_and_weight:
        human_dates.append(row[0].strftime("%d %b %Y"))
        eaten.append(int(row[1]))
        weights.append(float(row[2]))

    avg_weights = []
    target_kcals = []
    target_kcals.append(0)
    for i, row in enumerate(sum_kcals_and_weight):
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
        # if i < len(sum_kcals_and_weight)-1:
        # if len(sum_kcals_and_weight) <= 40 and i > 10 or len(sum_kcals_and_weight) > 40 and i > 30:
        tmp_target_kcals = round((tmp_eaten_sum - ((avg_weights[i] - avg_weights[k]) * 7700)) / num_of_days)
        target_kcals.append(tmp_target_kcals)
        # else:
        #     target_kcals.append(None)

    # print(len(human_dates))
    # print(len(weights))
    # print(len(avg_weights))
    # print(len(eaten))
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


def list_averaged(init_list, avg_range, round_bool, round_places=0):
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


### OPTIONS FNs ###############################################################

def options(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        user_id = request.user.profile.user_id
    except:
        return redirect('noprofile')

    results = db_get_options(user_id)
    logger.debug(f'{user_id = }, {results = }')
    return render(request, 'main/options.html', {'data': results[1]})


def set_weights_to_pull(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    try:
        user_id = request.user.profile.user_id
    except:
        return redirect('noprofile')

    data = json.loads(request.body)
    results = db_set_weights_to_pull(user_id, data['weights_to_pull'])
    # print(results)
    logger.debug(f'{user_id = }, {data = }, {results = }')
    if results[0] == 'success':
        return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


##### NO PROFILE FNs ##########################################################


def noprofile(request):
    logger.debug(f'')
    return render(request, 'main/noprofile.html')


##### BACKUP FUNCTIONS ########################################################


def backup():
    yesterday = datetime.today() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    logger.debug(f'executed')
    if not os.path.isfile(f'data_backup/{date_str}.txt'):
        db_result = db_backup(date_str)[1]
        result_list = []
        for i in db_result:
            row = {}
            row['diary_id'] = i['diary_id']
            row['users_id'] = i['users_id']
            row['date'] = i['date'].strftime("%Y-%m-%d")
            row['catalogue_id'] = i['catalogue_id']
            row['food_weight'] = i['food_weight']
            row['name'] = i['name']
            row['kcals'] = i['kcals']
            row['calc_kcals'] = int(i['calc_kcals'])
            result_list.append(row)
        with open(f'data_backup/{date_str}.txt', 'w', encoding='utf-8') as f:
            json.dump(result_list, f, ensure_ascii=False, indent=4)
        logger.debug(f'created')


# def test(request):
#     user_id = request.user.profile.user_id
#     data = json.loads(request.body)
#     # dataTmp = data['text'].strip().split('\n')
#     dataTmp = data['food'].strip().split('\n')
#     dataList = []

    # print(dataTmp)
    # print(dataList)

    # for i in dataTmp:
    #     date, weight = i.split('\t')
    #     date = datetime.strptime(date, '%d.%m.%Y').date().strftime("%Y-%m-%d")
    #     weight = weight.replace(',', '.')
    #     weight = float(weight)
    #     dataList.append([date, weight])

    # for j in dataList:
    #     result = db_add_new_weight(user_id, j[0], j[1])
    #     print(result)

    # for i in dataTmp:
    #     date, kcals = i.split('\t')
    #     date = datetime.strptime(date, '%d.%m.%Y').date().strftime("%Y-%m-%d")
    #     kcals = float(kcals)
    #     dataList.append([date, kcals])

    # for j in dataList:
    #     result = db_add_new_diary_entry(user_id, j[0], 188, j[1])
    #     print(result)

    # for k in dataTmp:
    #     date, weight, id = k.split('\t')
    #     date = datetime.strptime(date, '%d.%m.%Y').date().strftime("%Y-%m-%d")
    #     id = int(id)
    #     weight = int(weight)
    #     dataList.append([date, id, weight])
    #
    # for k in dataList:
    #     result = db_add_new_diary_entry(user_id, k[0], k[1], k[2])
    #     print(result)
    #
    # return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
    #                     content_type='application/json; charset=utf-8')
