import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# Import envvars from .env
load_dotenv()

# Flask App
app.logger.setLevel(logging.INFO)
STATIC_PATH = os.path.join(app.root_path, app.static_folder)
TEMPLATE_PATH = os.path.join(app.root_path, app.template_folder)

# Runs asynchronous scheduled jobs
scheduler = APScheduler(scheduler=BackgroundScheduler())
scheduler.init_app(app)
scheduler.start()

# Import the routes now that we've configured our Flask app
from app import routes

# Configure asynchronous rendering jobs to run at :00 and :30 of each hour
# max_instances=3 allows a new job to start even if previous one is stuck,
# while preventing runaway job accumulation
scheduler.add_job(
    id='rendering_task',
    func=routes.rendering_task,
    trigger='cron',
    minute='00,30',
    max_instances=3,
    misfire_grace_time=600  # Allow up to 10 minutes late execution if scheduler was busy
)
# routes.rendering_task()   # TODO KEVIN: maybe re-enable this
