# **LG darts tournaments management system** #

This is the repository for the LG darts tournaments management system.

### The core features offered are: ###

1. Create dart sets
2. Create darts tournaments and games
   1. 501, Cricket and Baseball are supported
   2. Scoring types are Ranks or Points 
   3. Tournaments are Continual or for Determined number of games (to come...)
   4. Matching are pairs or all participants playing every games
3. View summary tables for your tournaments
4. Export summary tables for your tournaments in csv

### Installation Instructions ###

* Clone this repository into your server (this will make a local copy of the repository)
* Install the required packages from requirements.txt
* Create a database
* The configuration using variables kept in the local environment or a .env file should contain:
  * DJANGO_SECRET_KEY=''
  * DEV= \# (0 or 1 for False/True)
  * DEBUG= \# (0 or 1 for False/True)
  * \# Comma-separated list of domains when DEBUG=1:
  * ALLOWED_HOSTS='example.com,example.net'
  * DATABASE_ENGINE=''
  * DATABASE_HOST=''
  * DATABASE_USER=''
  * DATABASE_PASSWORD=''
  * DATABASE_NAME=''
  * DATABASE_PORT=''
  * STATIC_ROOT=''
  * MEDIA_ROOT=''
* Install the Game type fixtures by running:
  manage.py loaddata GameType.json

### Notes: ###
* You can only enter the final score/ranks for each game because the scoring system is not available yet
* No css styling (other than Bootstrap 5)