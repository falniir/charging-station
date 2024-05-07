# charging-station
TTM4115 Charging Station system for EVs

# frontend
```
yarn install
yarn run dev
```


# backend
to init do

```
pipenv install
```

in charging-backend

Then do
```
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
```
may need to delete database
then to fill database with stock data, do:

```pipenv run python manage.py fill```
then 
```pipenv run python manage.py runserver```

# MQTT client

After the backend server is up and running, the mqtt client should also have subscribed to a specified broker and topic. 
To find this broker and topic you can check the [charging-backend/app/settings.py](https://github.com/falniir/charging-station/blob/main/charging-backend/app/settings.py). 
At the time this readme was written the broker and topic was:
```
MQTT_SERVER = 'test.mosquitto.org'
MQTT_TOPIC_INPUT = 'ttm4115/rats'
```
