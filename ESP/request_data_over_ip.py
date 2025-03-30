import socket

ESP32_IP = "10.100.102.45"  # Replace with your ESP32's IP
ESP32_PORT = 12345

def request_file(file_name, save_as):
    try:
        # Create TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ESP32_IP, ESP32_PORT))

        # Send file request
        client_socket.sendall(file_name.encode())

        # Wait for confirmation
        response = client_socket.recv(2).decode()
        if response != "OK":
            print("Error: File not found on ESP32")
            return

        # Receive file data
        with open(save_as, "wb") as f:
            while chunk := client_socket.recv(1024):
                f.write(chunk)

        print(f"File {file_name} downloaded as {save_as}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()

# Example usage
request_file("file_0.bin", "data/downloaded_file_0.bin")
