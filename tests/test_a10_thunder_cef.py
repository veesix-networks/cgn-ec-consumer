import random
from cgn_ec_consumer.handlers.a10 import A10ThunderSyslogHandler
import datetime
from cgn_ec_models.enums import NATEventTypeEnum, NATEventEnum, NATProtocolEnum

# Function to generate a random IP address
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

def test_a10_thunder_cef():
    a10 = A10ThunderSyslogHandler()

    for _ in range(100):
        data = random.choice([_generate_port_mapping_event(), _generate_port_block_event()])

        input = {'version': '1',
                'type': 'generic',
                'timestamp': datetime.datetime.now(),
                'message': _event_to_syslog(data),
                'ip': '10.10.10.10',
                'host': 'cgn0.thn2/cgn-demo'}

        metric = a10.parse_message(input)

        __event_type__, __event__ = a10._cef_event_map(f"CGN {data['_event_type']}")

        assert metric['type'] ==  __event_type__
        assert metric['event'] == __event__
        assert metric['vrf_name'] == "cgn-demo"
        assert metric['protocol'] == NATProtocolEnum.from_string(data['proto'])
        assert metric['src_ip'] == data['src']
        assert metric['x_ip'] == data['sourceTranslatedAddress']

        if __event_type__ == NATEventEnum.PORT_MAPPING:
            assert int(metric['src_port']) == data['spt']
            assert int(metric['x_port']) == data['sourceTranslatedPort']
        else:
            assert int(metric['start_port']) == data['sourceTranslatedPort']
            assert int(metric['end_port']) == data['cn3']
