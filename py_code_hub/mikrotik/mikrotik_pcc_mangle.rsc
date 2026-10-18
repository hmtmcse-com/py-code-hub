# ============================================================
# AUTO-GENERATED MIKROTIK PCC MANGLE CONFIGURATION
# ============================================================
#
# RouterOS 7.x
#
# Generator manages ONLY rules beginning with:
#   AUTO-PCC
#
# ============================================================
# MANAGED
# ============================================================
#
#   WAN inbound connection marking
#   PCC connection classification
#   Connection mark -> routing mark
#   WAN inbound reply routing
#   Router output routing
#
# ============================================================
# NOT MANAGED
# ============================================================
#
#   Interface lists
#   Interface list membership
#   NET-INTERNAL bypass
#   NET-VPN bypass
#   Firewall
#   NAT
#   Routing tables
#   Static routes
#   Failover
#   WireGuard
#
# ============================================================
# REQUIRED ROUTING TABLES
# ============================================================
#
#   to_ISP1
#   to_ISP2
#
# ============================================================
# PCC MODEL
# ============================================================
#
# PCC interface list : PCC
# WAN interface list : WAN
#
# Bandwidth          : ISP1=100 Mbps + ISP2=30 Mbps
# Exact ratio        : 10:3
# PCC bucket ratio   : 10:3
# Total buckets      : 13
# Exact              : YES
#
# ============================================================
# ISP DISTRIBUTION
# ============================================================
#
# [ISP1]
#   Bandwidth       : 100 Mbps
#   Exact share     : 76.92%
#   PCC share       : 76.92%
#   Bucket count    : 10
#   Buckets         : (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
#   Connection mark : ISP1_CM
#   Routing table   : to_ISP1
#
# [ISP2]
#   Bandwidth       : 30 Mbps
#   Exact share     : 23.08%
#   PCC share       : 23.08%
#   Bucket count    : 3
#   Buckets         : (10, 11, 12)
#   Connection mark : ISP2_CM
#   Routing table   : to_ISP2
#
# ============================================================
# REQUIRED MANGLE ORDER
# ============================================================
#
# MANUAL RULES MUST BE ABOVE AUTO-PCC CLASSIFICATION:
#
#   1. NET-INTERNAL bypass
#   2. NET-VPN bypass
#
# AUTO-PCC:
#
#   3. WAN inbound connection marking
#   4. PCC connection classification
#   5. Connection mark -> routing mark
#   6. WAN inbound reply routing
#   7. Router output routing
#
# ============================================================

# ============================================================
# REQUIRED MANUAL PCC BYPASS RULES
# ============================================================
#
# These rules are intentionally NOT managed by this script.
#
# They MUST be above AUTO-PCC classification rules.
#
# Apply manually:
#
/ip firewall mangle
add chain=prerouting dst-address-list=NET-INTERNAL action=accept comment="MANUAL PCC BYPASS NET-INTERNAL"
add chain=prerouting dst-address-list=NET-VPN action=accept comment="MANUAL PCC BYPASS NET-VPN"
#
# ============================================================

# ============================================================
# AUTO-PCC CLEANUP
# ============================================================
#
# Removes ONLY AUTO-PCC generated rules.
# Manual mangle rules are not touched.
#
/ip firewall mangle
remove [find where comment~"^AUTO-PCC "]

# ============================================================
# AUTO-PCC WAN INBOUND CONNECTION MARKING
# ============================================================
#
# Marks NEW connections according to the WAN interface
# on which the connection arrived.
#
# Used for:
#   - Port forwarding
#   - Public services
#   - Inbound connections
#   - Symmetric replies
#
/ip firewall mangle
add chain=prerouting in-interface="eth1-WAN-ISP1" connection-state=new connection-mark=no-mark action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC INBOUND ISP1"
add chain=prerouting in-interface="eth2-WAN-ISP2" connection-state=new connection-mark=no-mark action=mark-connection new-connection-mark="ISP2_CM" passthrough=yes comment="AUTO-PCC INBOUND ISP2"

# ============================================================
# AUTO-PCC CONNECTION CLASSIFICATION
# ============================================================
#
# PCC interface list = PCC
#
# Only NEW and unmarked connections are classified.
# Existing connection marks are preserved.
#
# Manual NET-INTERNAL / NET-VPN bypass rules must be
# above these rules.
#
# Total PCC buckets = 13
#
/ip firewall mangle
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/0 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-0"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/1 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-1"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/2 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-2"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/3 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-3"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/4 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-4"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/5 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-5"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/6 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-6"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/7 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-7"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/8 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-8"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/9 action=mark-connection new-connection-mark="ISP1_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP1 BUCKET-9"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/10 action=mark-connection new-connection-mark="ISP2_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP2 BUCKET-10"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/11 action=mark-connection new-connection-mark="ISP2_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP2 BUCKET-11"
add chain=prerouting in-interface-list="PCC" connection-state=new connection-mark=no-mark dst-address-type=!local per-connection-classifier=both-addresses-and-ports:13/12 action=mark-connection new-connection-mark="ISP2_CM" passthrough=yes comment="AUTO-PCC CONNECTION ISP2 BUCKET-12"

# ============================================================
# AUTO-PCC CONNECTION MARK -> ROUTING MARK
# ============================================================
#
# PCC interface membership is NOT checked here.
#
# PCC membership is only used for NEW connection
# classification.
#
/ip firewall mangle
add chain=prerouting connection-mark="ISP1_CM" dst-address-type=!local action=mark-routing new-routing-mark="to_ISP1" passthrough=no comment="AUTO-PCC ROUTE ISP1"
add chain=prerouting connection-mark="ISP2_CM" dst-address-type=!local action=mark-routing new-routing-mark="to_ISP2" passthrough=no comment="AUTO-PCC ROUTE ISP2"

# ============================================================
# AUTO-PCC WAN INBOUND REPLY ROUTING
# ============================================================
#
# Keeps inbound connections on the WAN routing table
# from which the connection originally arrived.
#
/ip firewall mangle
add chain=prerouting in-interface-list="WAN" connection-mark="ISP1_CM" action=mark-routing new-routing-mark="to_ISP1" passthrough=no comment="AUTO-PCC INBOUND-ROUTE ISP1"
add chain=prerouting in-interface-list="WAN" connection-mark="ISP2_CM" action=mark-routing new-routing-mark="to_ISP2" passthrough=no comment="AUTO-PCC INBOUND-ROUTE ISP2"

# ============================================================
# AUTO-PCC ROUTER OUTPUT ROUTING
# ============================================================
#
# This does NOT classify router-originated NEW connections.
#
# It only routes already-marked connections.
#
/ip firewall mangle
add chain=output connection-mark="ISP1_CM" dst-address-type=!local action=mark-routing new-routing-mark="to_ISP1" passthrough=no comment="AUTO-PCC OUTPUT-ROUTE ISP1"
add chain=output connection-mark="ISP2_CM" dst-address-type=!local action=mark-routing new-routing-mark="to_ISP2" passthrough=no comment="AUTO-PCC OUTPUT-ROUTE ISP2"

# ============================================================
# END AUTO-PCC CONFIGURATION
# ============================================================
