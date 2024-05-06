import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from app.mqtt import client as mqtt_client

# RESERVE MAINTANENCE START
# Added csrf exemption since we will only use localy run brokers for the demo
# TODO change into proper csrf handling
@csrf_exempt
def publish_message(request):
    request_data = json.loads(request.body)
    msg = request_data['msg']
    rc, mid = -1, -1
    if ((msg == 'RESERVE') or (msg == 'MAINTANENCE') or(msg == 'START')):
        rc, mid = mqtt_client.publish(settings.MQTT_TOPIC, request_data['msg'])
    else:
        something = 'else'    
    return JsonResponse({'code': rc, 'mid': mid})