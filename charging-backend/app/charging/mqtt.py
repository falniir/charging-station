from django.conf import settings
import paho.mqtt.client as mqtt
from app.charging.models import get_mock_chargingsession, Charger, get_mock_user

def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        mqtt_client.subscribe(settings.MQTT_TOPIC)
    else:
        print("Bad connection. Code:", rc)


def on_message(mqtt_client, userdata, msg):
    msg_string = msg.payload.decode("utf-8")
    if (msg_string == 'START'):
        charging_session = get_mock_chargingsession()
        if charging_session:
            charging_session.set_connected()
    elif (msg.payload.decode("utf-8") == 'MAINTANENCE'):
        # Mock
        Charger.objects.first().set_broken()
    #elif (msg.payload.decode("utf-8") == 'STOP'):

    elif (msg_string.replace('.', '').isnumeric()):
        charging_session = get_mock_chargingsession()
        if charging_session:
            charging_session.update_percent(float(msg.payload.decode("utf-8")))
    print(msg_string.isnumeric(), msg_string)
    print(
        f'Received message on topic: {msg.topic} with payload: {msg.payload}')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
client.connect(
    host=settings.MQTT_SERVER,
    port=settings.MQTT_PORT,
    keepalive=settings.MQTT_KEEPALIVE
)
