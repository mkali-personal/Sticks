#include "driver/ledc.h"
#include "SPIFFS.h"

// Define sensor pins
#define MQ9_PIN 34    // Example GPIO for MQ9 sensor (use the actual pin)
#define MQ135_PIN 35  // Example GPIO for MQ135 sensor (use the actual pin)

// Define speaker pin
#define SPEAKER_PIN 25  // GPIO pin connected to the speaker
#define LEDC_CHANNEL LEDC_CHANNEL_0
#define LEDC_TIMER   LEDC_TIMER_0
#define LEDC_MODE    LEDC_HIGH_SPEED_MODE
#define LEDC_FREQUENCY 880   // Frequency in Hertz
#define LEDC_DUTY_RES LEDC_TIMER_8_BIT // Set duty resolution to 8 bits

// Define volume level (0-255, where 255 is full volume)
int volume = 128;  // 50% volume

void setup() {
  // Initialize serial communication for debugging
  Serial.begin(115200);

  // Set up the speaker (PWM configuration)
  ledc_timer_config_t ledc_timer = {
      .speed_mode       = LEDC_MODE,
      .duty_resolution  = LEDC_DUTY_RES,
      .timer_num        = LEDC_TIMER,
      .freq_hz          = LEDC_FREQUENCY,
      .clk_cfg          = LEDC_AUTO_CLK
  };
  ledc_timer_config(&ledc_timer);

  ledc_channel_config_t ledc_channel = {
      .gpio_num       = SPEAKER_PIN,
      .speed_mode     = LEDC_MODE,
      .channel        = LEDC_CHANNEL,
      .intr_type      = LEDC_INTR_DISABLE,
      .timer_sel      = LEDC_TIMER,
      .duty           = 0,  // Initially no sound
      .hpoint         = 0
  };
  ledc_channel_config(&ledc_channel);

  // Initialize sensor pins (analog inputs)
  pinMode(MQ9_PIN, INPUT);
  pinMode(MQ135_PIN, INPUT);

    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("SPIFFS Mount Failed");
        return;
    }
    
    Serial.println("SPIFFS Initialized. Logging sensor data...");
}

void loop() {
  // Read sensor values (this might need to be adapted for your sensors)
  int mq9_value = analogRead(MQ9_PIN);
  int mq135_value = analogRead(MQ135_PIN);

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
    
    // file.close();
    // Serial.println("Data logged.");

  // If both sensors' readings are above 200, play sound for 3 seconds
  if (mq9_value > 200 && mq135_value > 200) {
    // playSound();
    delay(3000); // Play sound for 3 seconds
    // stopSound();
    Serial.println("Smoke anomally detected");
  }

  delay(1000); // Delay before next reading
}

void playSound() {
  // Generate a tone on the speaker (880Hz) with adjustable volume
  // ledcWrite(LEDC_CHANNEL, volume);  // Adjust volume (0-255)
    ledc_channel_config_t ledc_channel = {
      .gpio_num       = SPEAKER_PIN,
      .speed_mode     = LEDC_MODE,
      .channel        = LEDC_CHANNEL,
      .intr_type      = LEDC_INTR_DISABLE,
      .timer_sel      = LEDC_TIMER,
      .duty           = 5,  // Initially no sound
      .hpoint         = 0
  };
  ledc_channel_config(&ledc_channel);
}

void stopSound() {
  // Stop the tone by setting duty cycle to 0
    ledc_channel_config_t ledc_channel = {
      .gpio_num       = SPEAKER_PIN,
      .speed_mode     = LEDC_MODE,
      .channel        = LEDC_CHANNEL,
      .intr_type      = LEDC_INTR_DISABLE,
      .timer_sel      = LEDC_TIMER,
      .duty           = 0,  // Initially no sound
      .hpoint         = 0
  };
  ledc_channel_config(&ledc_channel);
}
