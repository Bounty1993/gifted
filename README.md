[![Build Status](https://travis-ci.org/Bounty1993/gifted.svg?branch=master)](https://travis-ci.org/Bounty1993/gifted)
[![Coverage Status](https://coveralls.io/repos/github/Bounty1993/gifted/badge.svg?branch=master)](https://coveralls.io/github/Bounty1993/gifted?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Gifted is a website where people can organize money collections for friends or strangers. 
Users can declare that they want to support the idea. 
If all money is collected, the collection is closed. 
Additionally users can use forum to comment different ideas

###Technology Stack:
* Python: 3.7x
* Django Web Framework: 2.2
* Redis
* Postgresql
* Channels
* Celery
* Twitter Bootstrap 4


###Installation

Gifted uses Redis and Postgresql so the best way to get it running is to use Docker.
Below you can find instruction.
```
$ mkdir gifted
$ cd gifted
$ git clone https://github.com/Bounty1993/gifted.git
$ cd gifted
```
Use Docker to build image and run containers:
```
$ docker-compose build
$ docker-compose run web python manage.py migrate --noinput
$ docker-compose up
```
Now it should work. Check it out:
```
http://localhost:8000/
```
###OAuth
Gifted can use OAuth. If you want to use it you have to provide API token for Facebook. Everything is done. Just add token in admin site. Need to know more? Check it out [django-allauth Facebook](https://django-allauth.readthedocs.io/en/latest/providers.html#facebook)