from django.shortcuts import render
from .models import *


def home(request):
    return render(request, 'main/index.html')


def weight(request):
    user_id = request.user.profile.user_id
    # print('user_id:', user_id)
    if user_id:
        results = db_get_last_weights(user_id)
        for i in results:
            print(i)
        return render(request, 'main/weight.html', {'data': results})
    return render(request, 'main/weight.html')


def diary(request):
    user_id = request.user.profile.user_id
    print('user_id:', user_id)
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
        # for i in today_food:
        #     print(i)
        return render(request, 'main/diary.html', {'data': [today_food, target_kcals]})
    return render(request, 'main/diary.html')

# def test_view(request):
#     results = test()
#     for i in results:
#         print(i)
#     return render(request, 'main/test.html', {'form': results})
