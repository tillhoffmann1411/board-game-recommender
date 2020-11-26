from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

# Create your views here.


@csrf_exempt
def qustionaireApi(request, id=0):
    if request.method == 'GET':
        return JsonResponse({'response': 'Test 123'})
