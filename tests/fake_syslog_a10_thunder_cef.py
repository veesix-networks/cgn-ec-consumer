import random
import socket
from time import sleep

def random_ip() -> str:
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

# Function to generate a random port number
def random_port() -> int:
    return random.randint(1024, 65000)  # Exclude well-known ports

def _generate_port_mapping_event():
    event_type = random.choice([100, 101])

    data = {
        "_event_type": event_type,
        "proto": random.choice(["TCP", "ICMP", "UDP"]),
        "src": random_ip(),
        "spt": random_port(),
        "sourceTranslatedAddress": random_ip(),
        "sourceTranslatedPort": random_port(),
    }

    return data

def _generate_port_block_event():
    event_type = random.choice([106, 107])

    start = random_port()
    data = {
        "_event_type": event_type,
        "proto": random.choice(["TCP", "ICMP", "UDP"]),
        "src": random_ip(),
        "sourceTranslatedAddress": random_ip(),
        "sourceTranslatedPort": start,
        "cn3": start + 255,
        "cn3Label": "Last Nat Port",
    }

    return data

def _get_message_name(num: int) -> str:
    match num:
        case 100:
            return 'Nat Port Allocated'
        case 101:
            return 'Nat Port Freed'
        case 106:
            return 'Nat Port Batch Pool Allocated'
        case 107:
            return 'Nat Port Batch Pool Freed'
        case _:
            return 'Unknown'

def _get_cef_header() -> str:
    return '0|A10|CFW|6.0.0-P1'

def _data_to_str(data: dict) -> str:
    return " ".join([f"{x[0]}={x[1]}" for x in data.items() if x[0][0] != '_'])

def _event_to_syslog(data):
    return f"{_get_cef_header()}|CGN {data['_event_type']}|{_get_message_name(data['_event_type'])}|5|{_data_to_str(data)}"

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

    header = "cgn0.thn2/cgn-demo CEF:"

    for message in _get_a10_cef_test_messages():
        print(f"Sending messages: {header}{message}")
        send_syslog_message(f"{header}{message}", syslog_server_ip, syslog_server_port)
        sleep(0.1)


if __name__ == "__main__":
    main()