import os

folder_path = 'data'

for filename in os.listdir(folder_path):
    file_path = folder_path + '/' + filename  # No os.path.join
    try:
        os.remove(file_path)  # Only works if it's a file, not a directory
    except OSError:
        print(f"Could not delete {file_path}")