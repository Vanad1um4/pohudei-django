from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import *
import json
import locale
locale.setlocale(locale.LC_ALL, "ru_RU.utf8")


def home(request):
    if request.user.is_authenticated:
        # return render(request, 'main/index.html')
        return redirect('home')
    return redirect('login')


### WEIGHT FNs ################################################################


def weight(request):
    if request.user.is_authenticated:
        user_id = request.user.profile.user_id
        weights_to_pull = request.user.profile.weights_to_pull
        # print('user_id:', user_id)
        if user_id:
            results = db_get_last_weights(user_id, weights_to_pull)
            # for i in results[1]:
            #     print(i)
            # if results[0] == 'success':
            return render(request, 'main/weight.html', {'data': results[1]})
        return redirect('home')
    return redirect('login')


def add_new_weight(request):
    if request.user.is_authenticated:
        user_id = request.user.profile.user_id
        if user_id:
            data = json.loads(request.body)
            result = db_add_new_weight(user_id, data['date'], data['weight'])
            # print(result)
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
            # print(data)
            result = db_update_weight(user_id, data['weight_id'], data['weight'])
            # print(result)
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
            # print(data)
            result = db_delete_weight(user_id, data['weight_id'])
            # print(result)
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
                tmp_target_kcals = round((tmp_eaten_sum - ((avg_weights[i] - avg_weights[k]) * 7700)) / num_of_days)
                target_kcals.append(tmp_target_kcals)

            todays_target_kcals = target_kcals[-1]
            today_food = db_get_today_food_from_diary(user_id)
            all_foods = db_get_food_names()
            return render(request, 'main/diary.html', {'data': [today_food, todays_target_kcals, all_foods]})
        return redirect('home')
    return redirect('login')


def add_food_to_diary(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = request.user.profile.user_id
        # print('user_id:', user_id)
        if user_id:
            # print('user_id:', user_id)
            # print('data:', data)

            today = datetime.today()
            today_str = today.strftime("%Y-%m-%d")
            # yesterday = datetime.today() - timedelta(days=1)  # TODO: make food addition for different dates

            result = db_add_new_diary_entry(user_id, today_str, data['food_id'], data['food_weight'])
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
        data = json.loads(request.body)
        user_id = request.user.profile.user_id
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
        print(row)
        human_dates.append(row[0].strftime("%d %b"))
        eaten.append(float(row[1]))
        weights.append(float(row[2]))

    avg_weights = []
    target_kcals = []
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
        tmp_target_kcals = round((tmp_eaten_sum - ((avg_weights[i] - avg_weights[k]) * 7700)) / num_of_days)
        target_kcals.append(tmp_target_kcals)

    prepped_normal_weights = []
    prepped_average_weights = []
    prepped_eaten_kcals = []
    prepped_target_kcals = []

    for i in range(len(human_dates)):
        prepped_normal_weights.append({'x': human_dates[i], 'y': weights[i]})
        prepped_average_weights.append({'x': human_dates[i], 'y': avg_weights[i]})

        prepped_eaten_kcals.append({'x': human_dates[i], 'y': eaten[i]})
        prepped_target_kcals.append({'x': human_dates[i], 'y': target_kcals[i]})
        # target_kcals_tmp = target_kcals[i]
        # if target_kcals_tmp > 3000:
        #     target_kcals_tmp = None
        # prepped_target_kcals.append({'x': human_dates[i], 'y': target_kcals_tmp})

    return render(request, 'main/stats.html', {'data': {
        'weights_chart': {'normal': prepped_normal_weights, 'average': prepped_average_weights},
        'kcals_chart': {'eaten': prepped_eaten_kcals, 'target': prepped_target_kcals}}})


### OPTIONS FNs ###############################################################

def options(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        user_id = request.user.profile.user_id
    except:
        return redirect('noprofile')

    results = db_get_options(user_id)
    print(results)
    # print(results[1][0][0])
    # if results[0] == 'success':
    return render(request, 'main/options.html', {'data': results[1]})
    # return render(request, 'main/options.html')


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
    if results[0] == 'success':
        return HttpResponse(json.dumps({'result': 'success'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')
    else:
        return HttpResponse(json.dumps({'result': 'failure'}),  # pyright: ignore
                            content_type='application/json; charset=utf-8')


### NO PROFILE FNs ############################################################


def noprofile(request):
    return render(request, 'main/noprofile.html')
