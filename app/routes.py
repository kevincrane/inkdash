import logging

from flask import send_file, redirect

from app import app
from app.dashboard_screens.homescreen.homescreen import HomeScreen
from app.dashboard_screens.newspaper.newspaper import NewspaperScreen


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/page1')
def page1_homescreen():
    return send_file(f'{app.static_folder}/render/page1.bmp', mimetype='image/bmp')


@app.route('/page1_render')
def page1_homescreen_render():
    homescreen = HomeScreen(app=app, static_directory=app.static_folder, filename='render/page1.bmp')
    homescreen.process_image(delete_interim_html=True)
    return redirect('/page1')
    # return send_file(f'{app.static_folder}/render/page1.bmp', mimetype='image/bmp')


@app.route('/page2')
def page2_newspaper():
    return send_file(f'{app.static_folder}/render/page2.bmp', mimetype='image/bmp')


@app.route('/page2_render')
def page2_newspaper_render():
    newspaper = NewspaperScreen(app=app, static_directory=app.static_folder, filename='render/page2.bmp')
    newspaper.process_image()
    return redirect('/page2')


def rendering_task():
    """ This method runs at the top of each hour, configured in __init__.py
    """
    logging.info('Running page rendering jobs...')
    with app.app_context():
        try:
            logging.info('Rendering page1 (homescreen)...')
            page1_homescreen_render()
            logging.info('Page1 rendering completed successfully')
        except Exception as e:
            logging.error(f'Failed to render page1: {e}', exc_info=True)

        try:
            logging.info('Rendering page2 (newspaper)...')
            page2_newspaper_render()
            logging.info('Page2 rendering completed successfully')
        except Exception as e:
            logging.error(f'Failed to render page2: {e}', exc_info=True)

    logging.info('Page rendering jobs completed')
