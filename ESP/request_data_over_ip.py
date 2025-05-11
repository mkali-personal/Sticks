import socket
import re
import os
import datetime


def extract_index(file_name):
    match = re.search(r'file_(\d+)\.bin$', file_name)
    return int(match.group(1)) if match else -1


def request_and_merge_files(file_names, output_file_name, esp32_ip, esp32_port):
    try:
        # Sort file names in descending order based on the index
        file_names.sort(key=extract_index, reverse=True)

        # Create the output directory based on the current date
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        output_dir = os.path.join("data", date_str)
        os.makedirs(output_dir, exist_ok=True)

        # Define the full output file path
        output_file_path = os.path.join(output_dir, f"{output_file_name}.bin")

        with open(output_file_path, "wb") as out_f:
            for file_name in file_names:
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((esp32_ip, esp32_port))
                    client_socket.sendall(file_name.encode())

                    response = client_socket.recv(2).decode()
                    if response != "OK":
                        print(f"Error: {file_name} not found on ESP32")
                        continue

                    while chunk := client_socket.recv(1024):
                        out_f.write(chunk)

                    print(f"File {file_name} downloaded and merged")
                except Exception as e:
                    print(f"Error downloading {file_name}: {e}")
                finally:
                    client_socket.close()

        return output_file_path

    except Exception as e:
        print(f"General error: {e}")


if __name__ == "__main__":
    # Example file names to request
    file_list = [f"file_{i}.bin" for i in range(5)]  # Adjust the range as needed
    request_and_merge_files(file_list, "merged_output")
