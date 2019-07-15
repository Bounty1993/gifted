[![Build Status](https://travis-ci.org/Bounty1993/gifted.svg?branch=master)](https://travis-ci.org/Bounty1993/gifted)
[![Coverage Status](https://coveralls.io/repos/github/Bounty1993/gifted/badge.svg?branch=master)](https://coveralls.io/github/Bounty1993/gifted?branch=master)

Celem My Blog jest stworzenie platformy gdzie użytkownicy mogą organizować zbiórki na prezenty dla znajomych i rodziny.

Użyte technologie:
* Python: 3.7x
* Django Web Framework: 2.2
* Twitter Bootstrap 4
* jQuery 3

###Virtaul environment
```
$ mkdir gifted
$ git clone https://github.com/Bounty1993/gifted.git
$ cd gifted
```
Instalacja virtual environment:
```
$ pip intall virtualenv
$ virtualenv venv
$ source venv/bin/activate
```
Następnie należy zainstalować biblioteki Django oraz Pythona:
```
$ pip install -r requirements.txt
```
Uruchomienie strony:

```
$ python manage.py runserver
```
Adres strony:
```
https://localhost:8000/rooms/
```
