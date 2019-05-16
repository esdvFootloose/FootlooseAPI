from flask import Flask, request, jsonify, abort
from flask_hookserver import Hooks
from flask.logging import default_handler
from werkzeug.contrib.fixers import ProxyFix
import json
from datetime import datetime
import logging
from logging.config import dictConfig
import os
from secrets import SECRET_KEY_FLASK, SECRET_KEY_GITHUB
import subprocess

if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.FileHandler',
    #        'stream': 'ext://flask.logging.wsgi_errors_stream',
            'filename' : 'app.log',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })


app = Flask(__name__)
app.secret_key = 'fRANKiSaWESOME'
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['GITHUB_WEBHOOKS_KEY'] = SECRET_KEY_GITHUB
app.config['VALIDATE_IP'] = False
app.config['VALIDATE_SIGNATURE'] = True

hooks = Hooks(app, url='/hooks/')

@app.route('/')
def index():
    return "welcome, you should know where to go"

@hooks.hook('ping')
def ping(data, delivery):
    app.logger.info(data['zen'])
    return 'Pong'

@hooks.hook('push')
def push(data, delivery):
    if data['repository']['name'] != 'FootlooseWebshop':
        abort(404)

    try:
        grepOut = subprocess.check_output(['sudo', '-u', 'www-data', 'git', 'pull'], cwd="/usr/share/nginx/html_webshop/")
    except subprocess.CalledProcessError as grepexc:
        return " git process: error code {} output: {}".format(grepexc.returncode, grepexc.output), 400

    try:
        grepOut = subprocess.check_output(['sudo', '-u', 'www-data', 'php', 'artisan', 'migrate'], cwd="/usr/share/nginx/html_webshop/")
    except subprocess.CalledProcessError as grepexc:
        return "aritsan: error code {} output: {}".format(grepexc.returncode, grepexc.output), 400

    return "Done"

