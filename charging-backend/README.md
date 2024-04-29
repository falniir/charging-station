# Backend setup

## Getting started

First get a virtual environment set up for python. 
Run the following command

```bash
python -m venv <virtual-environment-name>
```

Then install the following:

```bash
# Django
pip install django
# paho mqtt version 1.6.1
pip install paho-mqtt==1.6.1
```

Then to run the server just run the following:

```bash
python manage.py runserver
```

You will now have a mqtt client connected to a specific broker and topic. To find this broker and topic you can check the settings.py file in the app folder. 
As the time this readme was written the broker and folder was:
MQTT_SERVER = 'test.mosquitto.org'
MQTT_TOPIC_INPUT = 'ttm4115/rats'