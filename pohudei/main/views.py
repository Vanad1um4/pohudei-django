from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import *
import json


def home(request):
    if request.user.is_authenticated:
        # return render(request, 'main/index.html')
        return redirect('diary')
    return redirect('login')


def weight(request):
    if request.user.is_authenticated:
        user_id = request.user.profile.user_id
        # print('user_id:', user_id)
        if user_id:
            results = db_get_last_weights(user_id)
            for i in results:
                print(i)
            return render(request, 'main/weight.html', {'data': results})
        return redirect('home')
    return redirect('login')


def diary(request):
    if request.user.is_authenticated:
        user_id = request.user.profile.user_id
        # print('user_id:', user_id)
        if user_id:
            sum_kcals_and_weight = db_get_everyday_sum_kcals_from_diary(user_id)
            # for i in sum_kcals_and_weight:
            #     print(i)
            init_avg = 7
            table_length = len(sum_kcals_and_weight)
            if table_length < 30:
                init_avg = round(table_length / 4)
            if init_avg == 0:
                init_avg = 1
            start_weight = 0
            for i in sum_kcals_and_weight[:init_avg]:
                start_weight += i[2]
            start_weight = start_weight / init_avg
            # print('start_weight:', start_weight)
            # print()
            end_weight = 0
            for i in sum_kcals_and_weight[-init_avg:]:
                end_weight += i[2]
            end_weight = end_weight / init_avg
            # print('end_weight:', end_weight)
            # print()
            all_eaten = 0
            for i in sum_kcals_and_weight:
                all_eaten += int(i[1])
            # print('all_eaten:', all_eaten)
            # print()
            weight_delta = end_weight - start_weight
            # print('weight_delta:', weight_delta)
            # print()
            target_kcals = round((all_eaten - (weight_delta * 7700)) / table_length)
            # print('target_kcals:', target_kcals)
            # print()
            today_food = db_get_today_food_from_diary(user_id)
            all_foods = db_get_food_names()
            # print(all_foods)
            for i in today_food:
                print(i)
            return render(request, 'main/diary.html', {'data': [today_food, target_kcals, all_foods]})
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
            today_str = today.strftime("%Y-%m-%d")  # 07-07-2021
            # yesterday = datetime.today() - timedelta(days=1)  # TODO: make food addition for different dates

            result = db_add_new_diary_entry(user_id, today_str, data['food_id'], data['food_weight'])
            # print(result)
            # return redirect('diary')
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
        # print('user_id:', user_id)
        if user_id:
            # print('user_id:', user_id)
            # print('diary_id:', diary_id)

            # today = datetime.today()
            # today_str = today.strftime("%Y-%m-%d")  # 07-07-2021
            # yesterday = datetime.today() - timedelta(days=1)  # TODO: make food addition for different dates

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

# def test_view(request):
#     results = test()
#     for i in results:
#         print(i)
#     return render(request, 'main/test.html', {'form': results})
