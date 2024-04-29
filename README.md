# charging-station
TTM4115 Charging Station system for EVs


# backend
to init do

```
pipenv install
```

in charging-backend

Then do
```
pipenv run python manage.py migrate
```

then to fill database with stock data, do:

```pipenv run python manage.py fill```
then 
```pipenv run python manage.py runserver```