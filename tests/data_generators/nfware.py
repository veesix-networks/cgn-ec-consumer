from tests import generate_test_data as randomize_data

def generate_syslog_session_mappings(sessions: int = 100) -> list[dict]:
    syslog_messages = []

    for _ in range(0, sessions):
        syslog_message = (
            f"test {randomize_data.random_nfware_event()} VRF 0 {randomize_data.random_protocol()} INT {randomize_data.random_src_ip()}:{randomize_data.random_src_port()} "
            f"EXT {randomize_data.random_x_ip()}:{randomize_data.random_x_port()} DST {randomize_data.random_dst_ip()}:{randomize_data.random_dst_port()} DIR {randomize_data.random_nfware_direction()}"
        )

        json_body = {
            "message": syslog_message,
            "ip": "127.0.0.1",
            "timestamp": randomize_data.random_timestamp_past_month()
        }
        syslog_messages.append(json_body)
    return syslog_messages

def generate_syslog_address_mappings(sessions: int = 100) -> list[dict]:
    syslog_messages = []

    for _ in range(0, sessions):
        syslog_message = (
            f"test {randomize_data.random_nfware_event()} VRF 0 INT {randomize_data.random_src_ip()} EXT {randomize_data.random_x_ip()}"
        )

        json_body = {
            "message": syslog_message,
            "ip": "127.0.0.1",
            "timestamp": randomize_data.random_timestamp_past_month()
        }
        syslog_messages.append(json_body)
    return syslog_messages

def generate_syslog_port_mappings(sessions: int = 100) -> list[dict]:
    syslog_messages = []

    for _ in range(0, sessions):
        syslog_message = (
            f"test {randomize_data.random_nfware_event()} VRF 0 {randomize_data.random_protocol()} INT {randomize_data.random_src_ip()}:{randomize_data.random_src_port()} "
            f"EXT {randomize_data.random_x_ip()}:{randomize_data.random_x_port()}"
        )

        json_body = {
            "message": syslog_message,
            "ip": "127.0.0.1",
            "timestamp": randomize_data.random_timestamp_past_month()
        }
        syslog_messages.append(json_body)
    return syslog_messages

def generate_syslog_port_block_mappings(sessions: int = 100) -> list[dict]:
    syslog_messages = []

    for _ in range(0, sessions):
        syslog_message = (
            f"test {randomize_data.random_nfware_event()} VRF 0 INT {randomize_data.random_src_ip()} "
            f"EXT {randomize_data.random_x_ip()}:{randomize_data.random_x_port()}-{randomize_data.random_x_port()}"
        )

        json_body = {
            "message": syslog_message,
            "ip": "127.0.0.1",
            "timestamp": randomize_data.random_timestamp_past_month()
        }
        syslog_messages.append(json_body)
    return syslog_messages