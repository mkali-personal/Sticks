import machine
import time
import os
import struct

# Pin definitions
BUTTON_PIN = 0  # Built-in BOOT button (GPIO 0)
LED_PIN = 2  # Built-in LED (GPIO 2)
MQ9_PIN = 34
MQ135_PIN = 35

# Configure pins
button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin(LED_PIN, machine.Pin.OUT)
mq9_adc = machine.ADC(machine.Pin(MQ9_PIN))
mq135_adc = machine.ADC(machine.Pin(MQ135_PIN))

# Configure ADC resolution (0-4095)
mq9_adc.atten(machine.ADC.ATTN_11DB)
mq135_adc.atten(machine.ADC.ATTN_11DB)

# Variables for button debouncing and pause/resume
last_button_time = 0
button_debounce_ms = 300  # Debounce time in milliseconds
paused = False


# Function to check if the button is pressed (with debouncing)
def button_pressed():
    global last_button_time
    current_time = time.ticks_ms()

    if button.value() == 0 and time.ticks_diff(current_time, last_button_time) > button_debounce_ms:
        last_button_time = current_time
        return True
    return False


# Function to print data from /data.bin
def print_data_from_file():
    try:
        with open('/data.bin', 'rb') as file:
            file_size = os.stat('/data.bin')[6]
            print("File size:", file_size, "bytes")
            print("Logged data:")
            print("Index,Timestamp,MQ9,MQ135")

            while True:
                data = file.read(16)  # 4 bytes per value, 4 values
                if not data or len(data) < 16:
                    break

                index, timestamp, mq9_value, mq135_value = struct.unpack('IIII', data)
                print(f"{index},{timestamp},{mq9_value},{mq135_value}")

    except OSError as e:
        print("Failed to open file for reading:", e)


# Initialize file system
try:
    os.stat('/')  # Check if file system is mounted
except:
    import esp

    esp.osdebug(None)  # Turn off vendor debugging messages
    try:
        os.VfsFat.mkfs(machine.flash)  # Format the flash
    except:
        pass  # Already formatted

print("File system initialized.")

# Check if flag.txt exists
try:
    os.stat('/flag.txt')
    print("Flag file exists. Only printing data.")
    print_data_from_file()
    while True:  # Halt the program
        time.sleep(1)
except:
    print("Flag file not found. Press the BOOT button to start measurements...")

# Wait for button press before proceeding
while not button_pressed():
    time.sleep(0.05)

print("Button pressed! Performing measurements...")
print("Press button again to pause/resume measurements.")

# Create or clear the data file
with open('/data.bin', 'wb') as file:
    pass  # Just create an empty file

# Create flag.txt to mark completion
with open('/flag.txt', 'w') as flag_file:
    flag_file.write('done')

# Main program
measurement_count = 0
start_time = time.ticks_ms()
pause_pattern = [1, 0, 1, 0, 1, 0]  # LED blink pattern for pause mode

while measurement_count < 43200:
    # Check for button press to toggle pause/resume
    print(paused)
    if button_pressed():
        paused = not paused
        if paused:
            print("Measurements PAUSED. Press button again to resume.")
            # Show pause status with distinctive LED pattern
            for _ in range(5):  # Repeat pattern 5 times
                for p in pause_pattern:
                    led.value(p)
                    time.sleep(0.1)
        else:
            print("Measurements RESUMED.")
            led.value(1)  # Solid LED for a moment
            time.sleep(0.5)
            led.value(0)

    # If paused, just blink LED in a pattern and check button
    if paused:
        # Show distinctive pause pattern
        for p in pause_pattern:
            led.value(p)
            time.sleep(0.1)
            # Check for button press during blink pattern
            if button_pressed():
                paused = False
                print("Measurements RESUMED.")
                break
        continue  # Skip measurement while paused

    # Normal measurement code
    mq9_value = mq9_adc.read()
    mq135_value = mq135_adc.read()

    timestamp = time.ticks_ms() - start_time

    print(f"{mq9_value},{mq135_value}")

    # Pack data in binary format: 4 unsigned integers (16 bytes total)
    data = struct.pack('IIII', measurement_count, timestamp, mq9_value, mq135_value)

    # Append to file
    try:
        with open('/data.bin', 'ab') as file:
            file.write(data)
    except OSError as e:
        print("Failed to open file for appending:", e)

    # Blink the built-in LED for 0.1 seconds
    led.value(1)
    time.sleep(0.1)
    led.value(0)

    measurement_count += 1
    time.sleep(0.9)

print("All measurements completed. Reading results...")
print_data_from_file()

while True:  # Halt the program
    time.sleep(1)
