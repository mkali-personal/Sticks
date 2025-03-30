import socket
import re

ESP32_IP = "10.100.102.45"  # Replace with your ESP32's IP
ESP32_PORT = 12345

def extract_index(file_name):
    match = re.search(r'file_(\d+)\.bin$', file_name)
    return int(match.group(1)) if match else -1


def request_and_merge_files(file_names, output_file):
    try:
        # Sort file names in descending order based on the index
        file_names.sort(key=extract_index, reverse=True)

        with open(output_file, "wb") as out_f:
            for file_name in file_names:
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((ESP32_IP, ESP32_PORT))
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

    except Exception as e:
        print(f"General error: {e}")


# Example usage
file_list = [f"file_{i}.bin" for i in range(5)]
request_and_merge_files(file_list, "merged_output.bin")



