import random
import socket
from time import sleep

from test_a10_thunder_cef import _generate_port_mapping_event, _generate_port_block_event, _event_to_syslog

def _get_a10_cef_test_messages():
    messages = []

    for _ in range(20):
        data = random.choice([_generate_port_mapping_event(), _generate_port_block_event()])
        messages.append(_event_to_syslog(data))

    return messages

# Function to send a syslog message to a server via UDP
def send_syslog_message(message, syslog_server_ip, syslog_server_port=514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (syslog_server_ip, syslog_server_port))
    sock.close()


# Main function to generate and send syslog messages
def main():
    syslog_server_ip = "localhost"  # Replace with the IP of your syslog server
    syslog_server_port = 1514  # Default UDP port for syslog

    header = "<135> May  7 00:00:00.00 cgn0.thn2/cgn-demo CEF:"

    for message in _get_a10_cef_test_messages():
        print(f"Sending messages: {header}{message}")
        send_syslog_message(f"{header}{message}", syslog_server_ip, syslog_server_port)
        sleep(0.1)


if __name__ == "__main__":
    main()
