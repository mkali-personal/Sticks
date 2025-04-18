#include "FS.h"
#include "SPIFFS.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }

  Serial.println("SPIFFS Initialized successfully.");

  listFiles(SPIFFS, "/");
  deleteFile("/flag.txt");
  deleteFile("/data.bin");
}

void loop() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');  // Read a whole line
        command.trim();  // Remove spaces/newlines

        if (command.length() > 0) {
            deleteFile(command.c_str());  // Convert String to const char*
        }
    }
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


void deleteFile(const char *path) {
  if (SPIFFS.exists(path)) {
    if (SPIFFS.remove(path)) {
      Serial.print("Successfully deleted ");
      Serial.println(path);
    } else {
      Serial.print("Failed to delete ");
      Serial.println(path);
    }
  } else {
    Serial.print("File does not exist: ");
    Serial.println(path);
  }
}
