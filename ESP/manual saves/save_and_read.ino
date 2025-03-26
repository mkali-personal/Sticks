#include "SPIFFS.h"

// Pin definitions
#define BUTTON_PIN 0   // Built-in BOOT button (GPIO 0)
#define LED_PIN 2      // Built-in LED (GPIO 2)
#define MQ9_PIN 34
#define MQ135_PIN 35

// Struct to store data
struct SensorData {
  unsigned long index;
  unsigned long timestamp;  // Timestamp in milliseconds
  int mq9_value;            // MQ9 sensor reading
  int mq135_value;          // MQ135 sensor reading
};

int measurementCount = 0;  // Counter for measurements

// Function to check if the button is pressed
bool buttonPressed() {
  return digitalRead(BUTTON_PIN) == LOW;  // Active LOW button
}

// Function to print data from /data.bin
void printDataFromFile() {
  File file = SPIFFS.open("/data.bin", "r");
  if (!file) {
    Serial.println("Failed to open file for reading");
    return;
  }

  size_t fileSize = file.size();
  Serial.print("File size: ");
  Serial.print(fileSize);
  Serial.println(" bytes");

  Serial.println("Logged data:");
  Serial.print("Index,Timestamp,MQ9,MQ135\n");
  while (file.available()) {
    SensorData data;
    file.read((uint8_t*)&data, sizeof(SensorData));
    Serial.print(data.index);
    Serial.print(",");
    Serial.print(data.timestamp);
    Serial.print(",");
    Serial.print(data.mq9_value);
    Serial.print(",");
    Serial.println(data.mq135_value);
  }

  file.close();
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // Enable internal pull-up resistor
  pinMode(LED_PIN, OUTPUT);           // Set LED pin as output
  delay(2000);

  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }
  Serial.println("SPIFFS Initialized.");

  // Check if flag.txt exists
  if (SPIFFS.exists("/flag.txt")) {
    Serial.println("Flag file exists. Only printing data.");
    printDataFromFile();
    while (true); // Halt the program
  }

  Serial.println("Flag file not found. Press the BOOT button to start measurements...");

  // Wait for button press before proceeding
  while (!buttonPressed()) {
    delay(50);
  }

    // Create flag.txt to mark completion
    File flagFile = SPIFFS.open("/flag.txt", "w");
    if (!flagFile) {
      Serial.println("Failed to create flag file");
    } else {
      flagFile.println("done");
      flagFile.close();
    }
  
  Serial.println("Button pressed! Performing measurements...");

  // Clear the file if it exists (prepare for new data)
  File file = SPIFFS.open("/data.bin", "w");
  if (!file) {
    Serial.println("Failed to open file for clearing");
    return;
  }
  file.close();
}

void loop() {
  if (measurementCount < 43200) {
    int mq9_value = analogRead(MQ9_PIN);
    int mq135_value = analogRead(MQ135_PIN);
    
    SensorData data;
    data.index = measurementCount;
    data.timestamp = millis();
    data.mq9_value = mq9_value;
    data.mq135_value = mq135_value;

    Serial.print(data.mq9_value);
    Serial.print(",");
    Serial.println(data.mq135_value);

    File file = SPIFFS.open("/data.bin", "a");
    if (!file) {
      Serial.println("Failed to open file for appending");
      return;
    }

    file.write((uint8_t*)&data, sizeof(SensorData));
    file.close();

    // Blink the built-in LED for 0.1 seconds
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);

    measurementCount++;
    delay(900);
  } else {
    Serial.println("All measurements completed. Reading results...");
    printDataFromFile();

    while (true); // Halt the program
  }
}
