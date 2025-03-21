#include "FS.h"
#include "SPIFFS.h"

void setup() {
  Serial.begin(115200);

  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }

  Serial.println("SPIFFS Initialized successfully.");
  
  // List all files in SPIFFS
  listFiles(SPIFFS, "/");
}

void loop() {
  // Your regular loop code goes here
}

void listFiles(fs::FS &fs, const char * dirname) {
  Serial.println("Listing files:");
  
  // Open the root directory
  File root = fs.open(dirname);
  if (!root) {
    Serial.println("Failed to open directory");
    return;
  }

  // Ensure it's a directory
  if (!root.isDirectory()) {
    Serial.println("Not a directory");
    return;
  }

  // Read and print files in the directory
  File file = root.openNextFile();
  if (!file) {
    Serial.println("No files found in the directory.");
  } else {
    while (file) {
      Serial.print("FILE: ");
      Serial.print(file.name());
      Serial.print(" SIZE: ");
      Serial.println(file.size());
      file = root.openNextFile();
    }
  }
}
