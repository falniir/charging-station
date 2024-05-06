import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.mqtt import client as mqtt_client

# Added csrf exemption since we will only use localy run brokers for the demo
# TODO change into proper csrf handling
@csrf_exempt
def publish_message(request):
    request_data = json.loads(request.body)
    rc, mid = mqtt_client.publish(request_data['topic'], request_data['msg'])
    return JsonResponse({'code': rc, 'mid': mid})