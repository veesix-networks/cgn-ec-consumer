NFWARE_SYSLOG_REGEX_PATTERNS = [
    {
        "regex": r"(?P<event>[AD]) VRF (?P<vrf_id>\d+) INT (?P<src_ip>\d+\.\d+\.\d+\.\d+) EXT (?P<x_ip>\d+\.\d+\.\d+\.\d+)$",
        "handler": "parse_address_mapping",
    },
    {
        "regex": r"(?P<event>[AD]) VRF (?P<vrf_id>\d+) (?P<protocol>\d+) INT (?P<src_ip>\d+\.\d+\.\d+\.\d+):(?P<src_port>\d+) EXT (?P<x_ip>\d+\.\d+\.\d+\.\d+):(?P<x_port>\d+)$",
        "handler": "parse_port_mapping",
    },
    {
        "regex": r"(?P<event>[AD]) VRF (?P<vrf_id>\d+) (?P<protocol>\d+) INT (?P<src_ip>\d+\.\d+\.\d+\.\d+):(?P<src_port>\d+) EXT (?P<x_ip>\d+\.\d+\.\d+\.\d+):(?P<x_port>\d+) DST (?P<dst_ip>\d+\.\d+\.\d+\.\d+):(?P<dst_port>\d+) DIR (?P<direction>OUT|IN)$",
        "handler": "parse_session_mapping",
    },
    {
        "regex": r"(?P<event>[AD]) VRF (?P<vrf_id>\d+) INT (?P<src_ip>\d+\.\d+\.\d+\.\d+) EXT (?P<x_ip>\d+\.\d+\.\d+\.\d+):(?P<start_port>\d+)-(?P<end_port>\d+)$",
        "handler": "parse_port_block_mapping",
    },
]
