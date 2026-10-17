#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>
#include <ArduinoJson.h>
#include "DHT.h"

// 1. Wi-Fi Credentials
const char* ssid = "your wifi name";
const char* password = "wifi password";

// 2. Telegram Bot Token & Chat ID
#define BOTtoken "  "   // Provided by BotFather
#define CHAT_ID "  "     // Provided by @userinfobot

// 3. DHT Sensor Configuration
#define DHTPIN 4         // Digital Pin GPIO4
#define DHTTYPE DHT22    // DHT 22 (AM2302)

DHT dht(DHTPIN, DHTTYPE);

WiFiClientSecure client;
UniversalTelegramBot bot(BOTtoken, client);

// Time tracking for checking messages without blocking execution
int botRequestDelay = 1000; // Check for new messages every 1 second
unsigned long lastTimeBotRan;

// Function to handle incoming commands from Telegram
void handleNewMessages(int numNewMessages) {
  for (int i = 0; i < numNewMessages; i++) {
    String chat_id = String(bot.messages[i].chat_id);
    
    // Security Check: Only respond to YOUR Chat ID
    if (chat_id != CHAT_ID) {
      bot.sendMessage(chat_id, "Unauthorized user", "");
      continue;
    }
    
    String text = bot.messages[i].text;
    Serial.println("Received message: " + text);

    if (text == "/start") {
      String welcome = "Welcome to ESP32 Room Monitor!\n\n";
      welcome += "Use the command below to get live data:\n";
      welcome += "/temp : Check current temperature & humidity\n";
      bot.sendMessage(chat_id, welcome, "");
    }

    if (text == "/temp" || text == "/status") {
      float t = dht.readTemperature();
      float h = dht.readHumidity();

      if (isnan(t) || isnan(h)) {
        bot.sendMessage(chat_id, "Failed to read from DHT sensor!", "");
      } else {
        String message = "Room Conditions:\n";
        message += "Temperature: " + String(t, 1) + " C\n";
        message += "Humidity: " + String(h, 1) + " %";
        bot.sendMessage(chat_id, message, "");
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Connect to Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  client.setInsecure(); // Skip SSL Certificate verification for Telegram

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi Connected!");

  // Send startup message to Telegram
  bot.sendMessage(CHAT_ID, "ESP32 is online and connected to Wi-Fi!", "");
}

void loop() {
  if (millis() > lastTimeBotRan + botRequestDelay) {
    int numNewMessages = bot.getUpdates(bot.last_message_received + 1);

    while(numNewMessages) {
      handleNewMessages(numNewMessages);
      numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    }
    lastTimeBotRan = millis();
  }
}