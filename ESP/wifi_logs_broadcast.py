import network
import uasyncio as asyncio
import usocket as socket

UDP_IP = "255.255.255.255"  # Broadcast address
UDP_PORT = 4210
DEBUG_LEVEL = 1  # 0 = Off, 1 = Normal, 2 = Verbose

async def udp_log(message, level=1):
    """Send logs over UDP using a raw datagram socket."""
    if level > DEBUG_LEVEL:
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast
        sock.sendto(f"ESP32: {message}\n".encode(), (UDP_IP, UDP_PORT))
        sock.close()
    except Exception as e:
        print("Logging error:", e)

# Example usage:
async def test_logging():
    await udp_log("ESP32 booted up.")
    await udp_log("Connecting to sensors...", 2)  # Verbose message
    await asyncio.sleep(1)  # Ensure messages send before ending

# Run the test logging function
asyncio.run(test_logging())
