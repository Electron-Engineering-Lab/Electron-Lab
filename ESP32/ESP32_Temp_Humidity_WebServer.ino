#include <WiFi.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"
#include "DHT.h"

// 1. Wi-Fi Credentials
#define WLAN_SSID       "Your Wifi name"
#define WLAN_PASS       "Your wifi password"

// 2. Adafruit IO Account Details (from Step 1)
#define AIO_SERVER      "io.adafruit.com"
#define AIO_SERVERPORT  1883
#define AIO_USERNAME    "     "// your account name
#define AIO_KEY         "     " //  AIO key

// 3. DHT Sensor Configuration
#define DHTPIN 4         // Digital Pin GPIO4
#define DHTTYPE DHT22    // DHT 22 (AM2302)
DHT dht(DHTPIN, DHTTYPE);

// Setup ESP32 WiFi client
WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_SERVERPORT, AIO_USERNAME, AIO_KEY);

// Setup feeds for temperature and humidity
// Note: The path is IO_USERNAME/feeds/feed_name
Adafruit_MQTT_Publish temperature = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/temperature");
Adafruit_MQTT_Publish humidity = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/humidity");

void MQTT_connect();

void setup() {
  Serial.begin(115200);
  delay(10);
  dht.begin();

  Serial.println(F("ESP32 Adafruit IO Temperature Logger"));

  // Connect to Wi-Fi
  Serial.print("Connecting to ");
  Serial.println(WLAN_SSID);
  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  // Ensure the connection to the MQTT server is alive
  MQTT_connect();

  // Read temperature and humidity every 10 seconds (Adafruit IO free tier limit: 30 data points per minute)
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  if (isnan(t) || isnan(h)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  Serial.print(F("\nSending temperature val: "));
  Serial.print(t);
  Serial.print(F("... "));
  if (!temperature.publish(t)) {
    Serial.println(F("Failed"));
  } else {
    Serial.println(F("OK!"));
  }

  Serial.print(F("Sending humidity val:    "));
  Serial.print(h);
  Serial.print(F("... "));
  if (!humidity.publish(h)) {
    Serial.println(F("Failed"));
  } else {
    Serial.println(F("OK!"));
  }

  // Wait 10 seconds before publishing again
  delay(10000);
}

// Function to connect and reconnect to MQTT server
void MQTT_connect() {
  int8_t ret;

  if (mqtt.connected()) {
    return;
  }

  Serial.print("Connecting to MQTT... ");
  uint8_t retries = 3;
  while ((ret = mqtt.connect()) != 0) { 
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println("Retrying MQTT connection in 5 seconds...");
    mqtt.disconnect();
    delay(5000); 
    retries--;
    if (retries == 0) {
      while (1); // hang and wait for reset
    }
  }
  Serial.println("MQTT Connected!");
}