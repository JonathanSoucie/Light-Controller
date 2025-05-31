#include <WiFi.h>
#include <HTTPClient.h>

// Define button pins
const int button1Pin = 13; // Button 1 for "morning"
const int button2Pin = 12; // Button 2 for "evening"
const int button3Pin = 14; // Button 3 for "night"
const int button4Pin = 27; // Button 4 for "off"

// Wi-Fi credentials
const char* ssid = "BELL720";         // Your Wi-Fi SSID
const char* password = "traphouse811"; // Your Wi-Fi Password

// Server URL
const char* serverUrl = "http://192.168.2.30:5000/trigger"; // Update with your Flask server's IP

void setup() {
    Serial.begin(115200);

    // Initialize buttons
    pinMode(button1Pin, INPUT_PULLUP);
    pinMode(button2Pin, INPUT_PULLUP);
    pinMode(button3Pin, INPUT_PULLUP);
    pinMode(button4Pin, INPUT_PULLUP);

    // Connect to Wi-Fi
    connectWiFi();
}

void loop() {
    static unsigned long lastPressTime = 0; // To keep track of debounce timing
    const unsigned long debounceDelay = 200; // Delay in milliseconds

    if ((digitalRead(button1Pin) == LOW) && (millis() - lastPressTime > debounceDelay)) {
        sendRequest("morning");
        lastPressTime = millis();
    }
    if ((digitalRead(button2Pin) == LOW) && (millis() - lastPressTime > debounceDelay)) {
        sendRequest("evening");
        lastPressTime = millis();
    }
    if ((digitalRead(button3Pin) == LOW) && (millis() - lastPressTime > debounceDelay)) {
        sendRequest("night");
        lastPressTime = millis();
    }
    if ((digitalRead(button4Pin) == LOW) && (millis() - lastPressTime > debounceDelay)) {
        sendRequest("off");
        lastPressTime = millis();
    }
}

void connectWiFi() {
    Serial.print("Connecting to Wi-Fi");
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }

    Serial.println("\nConnected to Wi-Fi");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}

void sendRequest(const String& preset) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverUrl); // Specify the URL

        // Send the request
        http.addHeader("Content-Type", "application/json");
        int httpResponseCode = http.POST("{\"preset\":\"" + preset + "\"}");

        // Check response
        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println("Response: " + response);
        } else {
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
        }

        http.end(); // Free resources
    } else {
        Serial.println("Wi-Fi not connected");
    }
}
