# Inkdash Desk Assistant

Designed for [Inkplate 10](https://soldered.com/product/soldered-inkplate-10-9-7-e-paper-board-with-enclosure-copy/).
Show your current day at a glance and toggle to additional screens; currently just the front page of 
the NY Times.

## Quickstart
1. Get an Inkplate 10 above
2. Set up your Arduino IDE & burn the new program to your Inkplate.
   - Set up your Inkplate from [the official docs](https://inkplate.readthedocs.io/en/latest/get-started.html#arduino)
   - Copy [inkdash_display.ino](inkdash_display/inkdash_display.ino) into a new Arduino sketchbook
   - Fill in every value where you see `CHANGEME`
   - Upload to Inkplate
3. Set up your local environment with your own API keys.
   - Copy `.env-TEMPLATE` to a new file called `.env`
   - Follow the [setup steps](#set-up-inkdash-homescreen) below to set up your custom operations.
4. (optional) Make any changes you need and push changes upstream to your own repo.
   - Test thoroughly yourself locally
     - Run the server locally with `run_server.sh`
       - From the root directory, run `ln -s ../static app/static` if missing a local `app/static` 
         directory
     - After, build with `docker_build.sh`, verify it works in-container with `docker_run.sh`
   - Push changes upstream to Docker Hub with `docker_push.sh`
5. Deploy the Docker build to your server
   - These are written for my particular use case on a Synology NAS.
   - Make sure you have the latest version of your Image from Docker (may have to search it in the 
     Registry & download again)
   - In File Station, create folders `docker/inkdash`, `inkdash/static`, & `inkdash/static/render`;
     set permissions to be accessible from everyone
   - Container Manager > Project > Create
     - Project Name: `inkdash-server`
     - Path: `/volume1/docker/inkdash`
     - Souce: "Create docker-compose.yml"
     - Copy the contents of [docker-compose.yml](docker-compose.yml) into this box. Comment out the
       `env_file:` block and uncomment the `environment:` one; copy over all env vars from `.env`
       to this list.


## Set up Inkdash Homescreen

To use the main homescreen page, you need the following services set up.

### Google Calendar

To integrate Google Calendar with your application using the `gcsa` library, follow these steps to 
set up the Google Calendar API:
1. Create a Google Cloud Project
   - Visit the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
2. Enable the Google Calendar API
   - Navigate to **APIs & Services > Dashboard**.
   - Click **"+ ENABLE APIS AND SERVICES"**.
   - Search for "Google Calendar API" and click **Enable**.
3. Create Credentials
   - Go to **APIs & Services > Credentials**.
   - Click **"Create Credentials"** and select **"OAuth client ID"**.
   - For the application type, select **"Desktop app"**.
   - Enter a name for your OAuth client ID and click **Create**.
4. Download Credentials
   - After creating your OAuth client ID, download the credentials by clicking the download (JSON) 
     button next to your OAuth 2.0 Client IDs.
   - Rename this file to `gcal_credentials.json` and place it in your environment's `static` folder
     (defined in `docker-compose.yml`)
5. Generate Token
   - On the first run of your application, the `gcsa` library will prompt you to authenticate via a
     URL.
   - Open the URL in your browser, log in with your Google account, and grant the requested 
     permissions.
   - This process will generate a token that the `gcsa` library will automatically save to 
     `gcal_token.pickle` in the same static directory.
   - **Note**: The token only needs to be generated once and will be reused by your application. If 
     it expires or you change the scopes, you might need to regenerate it.
6. Define which calendars you want to display on your Inkdash.
   - These are most likely the email address of the calendar. If you have multiple calendars to
     display, separate them by a comma.
   - Obviously you need to have access to each calendar you define.

### Todoist

Get your Todoist API token (Settings > Integrations > Developer). Copy this value into `.env` or 
`docker-compose.yml` under the `TODOIST_API_KEY` env var.

### Open Weather Map

Create an account, and get an OpenWeather API token [here](https://home.openweathermap.org/api_keys).
You will need to sign up for the One Call API service [here](https://home.openweathermap.org/subscriptions).
This is technically paid, but only charges after 1000 daily requests and you will rarely use more
than 1/hour. Copy this API Token into `.env` or `docker-compose.yml` under the `OWM_API_KEY` env var.


## Steps to add new screen

1. Increment max number of screens in `inkdash_display.ino` (`numScreens`)
2. Create a new Python package for your screen with a class that extends [DashboardScreen](app/dashboard_screens/dashboard_base.py).
   At a minimum this needs to implement `process_image`; this method is expected to write a BMP 
   image to `self.filename`.
   - See [newspaper.py](app/dashboard_screens/newspaper/newspaper.py) for the easiest example 
     (downloads a PDF online, converts it to a BMP).
   - See [homescreen.py](app/dashboard_screens/homescreen/homescreen.py) for an advanced example
     (generates a full HTML document, screenshots it with Selenium and saves as a BMP)
3. In [routes.py](app/routes.py), add new routes for your screen.
   - Needs `/page<num>` to return a BMP file
   - Needs `/page<num>_render` to generate a new BMP file to `static/render/page<num>.bmp`
   - Add the rendering method to `rendering_task`


## Docker Operations

The following operations are designed around [my Docker image](https://hub.docker.com/repository/docker/kevincrane/inkplate-dashboard-server/general).
You can change them as needed to push to your own repo.

- `docker_build.sh` - locally build the Docker container
- `docker_push.sh` - push an updated version of the Docker container to Docker Hub
- `docker_run.sh` - locally run this Docker instance so you can test that it works
- `run_server.sh` - locally start up the Flask server (w/o Docker); accessible at http://127.0.0.1:10465


## Acknowledgements

Thanks to [MagInkDash](https://github.com/speedyg0nz/MagInkDash) for the heavy inspiration.
