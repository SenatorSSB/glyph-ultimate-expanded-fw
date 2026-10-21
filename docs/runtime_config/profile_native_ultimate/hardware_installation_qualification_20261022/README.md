# Exact candidate installation and qualification gate

[Owner decision packet](INSTALL_PACKET.md) and [machine limits](INSTALL_PACKET.json)
are unexecuted and require explicit owner approval. The [finite independent
ACK](independent_ack/REPORT.md) verifies exact candidate/original-state/identity,
attempt bounds, same-user context, preserved failures and exclusions. It grants
no device action or acceptance.

The [route adapter](route_packet.py.txt) and [offline safety checks](route_packet_safety.py.txt)
are prepared for a later separately approved native-testing stage. This packet
excludes their execution and all Config/profile writes. No firmware rebuild or
native source integration occurred.
