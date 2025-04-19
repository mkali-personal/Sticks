import uos

try:
    uos.mkdir("data")
    print("Directory 'data' created.")
except OSError as e:
    print(f"Could not create directory: {e}")