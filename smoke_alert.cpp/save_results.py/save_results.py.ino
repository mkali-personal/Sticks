#include "SPIFFS.h"

#define MQ9_PIN 34      // Change to your actual GPIO pin
#define MQ135_PIN 35    // Change to your actual GPIO pin

void setup() {
    Serial.begin(115200);

    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("SPIFFS Mount Failed");
        return;
    }

    Serial.println("SPIFFS Initialized. Logging sensor data...");
}

void loop() {
    // Read sensor values
    int mq9_value = analogRead(MQ9_PIN);
    int mq135_value = analogRead(MQ135_PIN);

    // Debug output
    Serial.print("MQ9 Value: ");
    Serial.print(mq9_value);
    Serial.print(", MQ135 Value: ");
    Serial.println(mq135_value);

    // Open the file in append mode
    File file = SPIFFS.open("/data.txt", "a");
    if (!file) {
        Serial.println("Failed to open file for appending");
        return;
    }

    // Write data with timestamp (optional)
    file.print(millis());
    file.print(", MQ9: ");
    file.print(mq9_value);
    file.print(", MQ135: ");
    file.println(mq135_value);
    
    file.close();
    Serial.println("Data logged.");

    delay(1000);  // Wait before next reading
}
