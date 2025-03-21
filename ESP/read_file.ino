#include "FS.h"
#include "SPIFFS.h"

// Struct to store data
struct SensorData {
  unsigned long timestamp;  // Timestamp in milliseconds
  int mq9_value;            // MQ9 sensor reading
  int mq135_value;          // MQ135 sensor reading
};


void setup() {
  Serial.begin(115200);  // Initialize serial communication
  // // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }
}

void loop() {
    if (Serial.available()) {
        char command = Serial.read();
        if (command == 's') {  // If 's' is received, stop the loop
            while (true); // Halt the program
        }
    }

    // // Open the file to read its size and contents
    File file = SPIFFS.open("/data.bin", "r");
    if (!file) {
      Serial.println("Failed to open file for reading");
      return;
    }

    // // Get the file size and print it
    size_t fileSize = file.size();
    Serial.print("File size: ");
    Serial.print(fileSize);
    Serial.println(" bytes");

    // // Read and print all the triplets (time, MQ9, MQ135) from the file
    Serial.println("Logged data:");
    while (file.available()) {
      SensorData data;
      file.read((uint8_t*)&data, sizeof(SensorData));  // Read one triplet
      Serial.print("Timestamp: ");
      Serial.print(data.timestamp);
      Serial.print(", MQ9: ");
      Serial.print(data.mq9_value);
      Serial.print(", MQ135: ");
      Serial.println(data.mq135_value);
    }

    // file.close();  // Close the file after reading

    // Optionally, add a delay to avoid constant loop after reading
    delay (10000); // Halt the program
    
    // If you want to reset the measurement count and continue, uncomment the following line
    // measurementCount = 0;
  }