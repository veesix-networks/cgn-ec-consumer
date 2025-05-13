F5_BIGIP_SYSLOG_REGEX_PATTERNS = [
    {
        "regex": r"(\S+) (\d+.\d+.\d+.\d+)%(\d+):(\d+) (\d+) (\d+.\d+.\d+.\d+)%\d+:(\d+) (\d+.\d+.\d+.\d+) (\d+)$",
        "handler": "parse_session_mapping",
    }
]
