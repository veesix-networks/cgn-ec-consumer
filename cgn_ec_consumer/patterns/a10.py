A10_VTHUNDER_SYSLOG_REGEX_PATTERNS = [
    {
        "regex": r"NAT-(?P<protocol>\w+)-(?P<event>\w+): (?P<src_ip>\d+.\d+.\d+.\d+):(?P<src_port>\d+)<-->(?P<x_ip>\d+.\d+.\d+.\d+):(?P<x_port>\d+) to \d+.\d+.\d+.\d+:\d+$",
        "handler": "parse_port_mapping",
    },
    {
        "regex": r"NAT-(?P<protocol>\w+)-(?P<event>\w+): (?P<src_ip>\d+.\d+.\d+.\d+):(?P<src_port>\d+)<->(?P<dst_ip>\d+.\d+.\d+.\d+):(?P<dst_port>\d+),(?P<x_ip>\d+.\d+.\d+.\d+):(?P<x_port>\d+)<-->\d+.\d+.\d+.\d+:\d+$",
        "handler": "parse_session_mapping",
    },
]
