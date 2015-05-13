#Gov Dashboard

This Dashboard is designed to be a companion tool to data.pr.gov

## Stack

* Python 3.4.x
* Django 1.7
* PostgreSQL

## Dependencies
For a list of dependencies take a look at the requirements.txt in the project.

## data.pr.gov account
You will need an account to be able to used this dashboard. Once you've created your account, you will need to create an app token. Go to your home page, and at the bottom you will see "Administrar" or "Manage". Click here and then click "Create New Application" or "Crear nueva aplicación". Fill in the blanks and generate your app token and secret token.

In the Dashboard, your app token will be CLIENT_ID and your secret token will be CLIENT_SECRET. These can go in a .env file or a local_settings.py file. Also include the following in your .env or local_settings:

* AUTHORIZE_URL=https://data.pr.gov/oauth/authorize
* TOKEN_URL=https://data.pr.gov/oauth/access_token

These all will have to be set as enviromental variables when deploying to Heroku.
