SIXWIND_SYSLOG_REGEX_PATTERS = [
    {
        "regex": r"^fp-cgnat\[\d+\]: (?P<event>NEW CONN|DESTROY CONN): fwd proto (?P<protocol>\d+) (?P<src_ip>\d+\.\d+\.\d+\.\d+):(?P<src_port>\d+) -> (?P<x_ip>\d+\.\d+\.\d+\.\d+):(?P<x_port>\d+), back proto \d+ \d+\.\d+\.\d+\.\d+:\d+ --> (?P<dst_ip>\d+\.\d+\.\d+\.\d+):(?P<dst_port>\d+)$",
        "handler": "parse_session_mapping",
    },
    {
        "regex": r"^(?P<event>[A|D]) VRF (?P<vrf_id>\d+) INT (?P<src_ip>\d+\.\d+\.\d+\.\d+) EXT (?P<x_ip>\d+\.\d+\.\d+\.\d+):(?P<start_port>\d+)-(?P<end_port>\d+)$",
        "handler": "parse_port_mapping",
    },
]
