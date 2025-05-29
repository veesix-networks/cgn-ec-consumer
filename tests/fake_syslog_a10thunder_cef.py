from cgn_ec_consumer.handlers.a10_cef import A10ThunderCEFSyslogHandler

test_data = """
2025-05-02T11:34:56.87+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 106|Nat Port Batch Pool Allocated|5|proto=UDP src=100.65.140.73 sourceTranslatedAddress=99.99.99.12 sourceTranslatedPort=22016 cn3=22271 cn3Label=Last Nat Port
2025-05-02T11:35:00.62+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 100|Nat Port Allocated|5|proto=ICMP src=100.65.161.0 spt=48856 sourceTranslatedAddress=99.99.99.13 sourceTranslatedPort=48856 dst=8.8.8.8 dpt=0
2025-05-02T11:35:00.62+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 101|Nat Port Freed|5|proto=ICMP src=100.65.150.5 spt=37892 sourceTranslatedAddress=99.99.99.8 sourceTranslatedPort=37892
2025-05-02T11:35:00.72+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 101|Nat Port Freed|5|proto=ICMP src=100.65.154.17 spt=3637 sourceTranslatedAddress=99.99.99.15 sourceTranslatedPort=3637
2025-05-02T11:35:00.72+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 100|Nat Port Allocated|5|proto=ICMP src=100.65.154.17 spt=3638 sourceTranslatedAddress=99.99.99.15 sourceTranslatedPort=3638 dst=1.1.1.1 dpt=0
2025-05-02T11:35:00.72+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 101|Nat Port Freed|5|proto=ICMP src=100.65.154.17 spt=3638 sourceTranslatedAddress=99.99.99.15 sourceTranslatedPort=3638
2025-05-02T11:35:00.78+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 100|Nat Port Allocated|5|proto=ICMP src=100.65.189.8 spt=56026 sourceTranslatedAddress=99.99.99.12 sourceTranslatedPort=56026 dst=8.8.8.8 dpt=0
2025-05-02T11:34:58.71+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 100|Nat Port Allocated|5|proto=ICMP src=100.65.161.188 spt=44035 sourceTranslatedAddress=99.99.99.9 sourceTranslatedPort=44035 dst=8.8.4.4 dpt=0
2025-05-02T11:35:00.87+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 107|Nat Port Batch Pool Freed|5|proto=UDP src=100.65.140.73 sourceTranslatedAddress=99.99.99.12 sourceTranslatedPort=22016 cn3=22271 cn3Label=Last Nat Port
2025-05-02T11:34:59.11+00:00 10.254.254.57 cgn0.thn2/cgn-demo  CEF:0|A10|CFW|6.0.0-P1|CGN 100|Nat Port Allocated|5|proto=ICMP src=100.65.250.67 spt=735 sourceTranslatedAddress=99.99.99.9 sourceTranslatedPort=20209 dst=8.8.4.4 dpt=0
"""

handler = A10ThunderCEFSyslogHandler()

for line in test_data.splitlines():
    if not line:
        continue

    handler.parse_message(
        {
            "message": line,
            "timestamp": "2025-05-02T11:35:00.87+00:00 10.254.254.57",
            "ip": "127.0.0.1",
            "host": "cgn0.thn2/cgn-demo",
        }
    )
