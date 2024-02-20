/*
  Displays dashboards served from a local server (dashboard_server)
  - Runs the setup() method whenever woken from sleep mode
  - Every refreshTime seconds, display will: wake up, download new images, display the currentPage
  - When the Wake button is pressed, will increment currentPage to rotate through screens

  Arduino setup instructions: https://github.com/SolderedElectronics/Inkplate-Arduino-library
*/

// Next 3 lines are a precaution, you can ignore those, and the example would also work without them
#if !defined(ARDUINO_INKPLATE10) && !defined(ARDUINO_INKPLATE10V2)
#error "Wrong board selection for this example, please select e-radionica Inkplate10 or Soldered Inkplate10 in the boards menu."
#endif

#include <Inkplate.h>


// Constants
const char* ssid = "CHANGEME";
const char* password = "CHANGEME";

const char* dashboardServerUrl = "CHANGEME";    // Most likely IP address of local server
const int dashboardServerPort = 10465;          // Exposed port defined in docker-compose.yml
const int numScreens = 2;
const unsigned long refreshTime_usec = 3600 * 1000000;   // 1 hour

// Initiate Inkplate object
Inkplate display(INKPLATE_3BIT);
SdFile file;

// Store int in rtc data, to remain persistent during deep sleep
RTC_DATA_ATTR int currentPage = 1;


bool wakeSdCard() {
  if (!display.sdCardInit()) {
    // If SD card init not success, display error on screen
    display.println("SD Card error!");
    return false;
  }
  return true;
}


/**
 * Download image from server; assumes all images located at /page<num>
 */
void downloadImage(int pageNum) {
  String url = String("http://") + dashboardServerUrl + ":" + dashboardServerPort + "/page" + pageNum;
  String filename = "page" + String(pageNum) + ".bmp";
  Serial.println("Downloading image from: " + url);

  int32_t  img_len = 1024*1024;   // Overridden with correct length in downloadFile
  uint8_t* img_buf = display.downloadFile(url.c_str(), &img_len);

  if (file.open(filename.c_str(), (O_RDWR | O_CREAT | O_TRUNC))) {
    // Write the downloaded file to SD
    Serial.println("Writing " + String(img_len) + " bytes to SD card at " + filename);
    file.write(img_buf, img_len);
    file.close();
  } else {
    display.println("Error while creating file: " + filename);
  }
}


/**
 * Load image by pageNum and display on screen
 */
void displayImage(int pageNum) {
  String filename = "page" + String(pageNum) + ".bmp";
  Serial.println("Displaying image from " + filename);

  if (!display.drawImage(filename, 0, 0, 1)) {
    display.println("Error opening image " + filename);
  }
}

/**
 * Connect to WiFi, download & save all screens from server
 */
void updateSavedImages() {
  display.connectWiFi(ssid, password, WIFI_TIMEOUT, true);
  for (int i = 1; i <= numScreens; i++) {
    downloadImage(i);
  }
  displayImage(currentPage);
  display.disconnect();
}


/**
 * Run whenever ESP boots up, when the wake button is pressed, or after refreshTime seconds
 */
void setup()
{
  Serial.begin(9600);
  display.begin();

  if (wakeSdCard()) {
    // Decide what to do based on if we woke from timer or button
    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
    if (wakeup_reason == ESP_SLEEP_WAKEUP_EXT0) {
      // Wake button; rotate to the next screen (1-indexed) on button press
      currentPage = (currentPage % numScreens) + 1;
      Serial.println("Updating to page " + String(currentPage));
      displayImage(currentPage);
    } else {
      updateSavedImages();
    }
  }

  // Update the screen with the buffered image
  display.display();

  // Go to sleep for refreshTime_usec seconds
  esp_sleep_enable_timer_wakeup(refreshTime_usec);

  // Enable wakeup from deep sleep on gpio 36 (wake button)
  esp_sleep_enable_ext0_wakeup(GPIO_NUM_36, LOW);

  // Go to sleep until next wake
  display.sdCardSleep();
  esp_deep_sleep_start();
}

void loop()
{
  // Never here! If you use deep sleep, the whole program should be in setup() because the board restarts each
  // time. loop() must be empty!
}
