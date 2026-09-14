from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from functools import reduce
from math import gcd


AUTO_PCC_PREFIX = "AUTO-PCC"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class ISP:
    name: str
    bandwidth_mbps: Decimal
    interface: str
    gateway: str
    routing_table: str
    connection_mark: str
    routing_mark: str


@dataclass(frozen=True)
class ISPPlan:
    isp: ISP
    exact_percentage: Decimal
    bucket_count: int
    buckets: tuple[int, ...]
    pcc_percentage: Decimal


@dataclass(frozen=True)
class PCCPlan:
    isps: tuple[ISP, ...]
    target_ratio: tuple[int, ...]
    bucket_ratio: tuple[int, ...]
    total_buckets: int
    exact: bool
    plans: tuple[ISPPlan, ...]


# ============================================================
# HELPERS
# ============================================================

def to_decimal(
    value: int | float | str | Decimal,
) -> Decimal:
    return Decimal(str(value))


def decimal_to_fraction(
    value: Decimal,
) -> Fraction:
    return Fraction(value)


# ============================================================
# RATIO
# ============================================================

def simplify_ratio(
    values: list[Decimal],
) -> list[int]:
    fractions = [
        decimal_to_fraction(value)
        for value in values
    ]

    denominator_lcm = 1

    for fraction in fractions:
        denominator_lcm = (
            denominator_lcm
            * fraction.denominator
            // gcd(
                denominator_lcm,
                fraction.denominator,
            )
        )

    integer_values = [
        fraction.numerator
        * (
            denominator_lcm
            // fraction.denominator
        )
        for fraction in fractions
    ]

    common_divisor = reduce(
        gcd,
        integer_values,
    )

    return [
        value // common_divisor
        for value in integer_values
    ]


# ============================================================
# APPROXIMATE BUCKET ALLOCATION
# ============================================================

def largest_remainder_allocation(
    values: list[int],
    total_buckets: int,
) -> list[int]:

    total = sum(values)

    exact = [
        Decimal(value)
        / Decimal(total)
        * Decimal(total_buckets)
        for value in values
    ]

    buckets = [
        int(value)
        for value in exact
    ]

    remaining = (
        total_buckets
        - sum(buckets)
    )

    remainders = [
        value - int(value)
        for value in exact
    ]

    order = sorted(
        range(len(values)),
        key=lambda index: remainders[index],
        reverse=True,
    )

    for index in order[:remaining]:
        buckets[index] += 1

    return buckets


def choose_bucket_ratio(
    target_ratio: list[int],
    max_buckets: int,
) -> tuple[list[int], bool]:

    exact_total = sum(target_ratio)

    if exact_total <= max_buckets:
        return target_ratio, True

    return (
        largest_remainder_allocation(
            values=target_ratio,
            total_buckets=max_buckets,
        ),
        False,
    )


# ============================================================
# CREATE PCC PLAN
# ============================================================

def create_pcc_plan(
    isps: list[ISP],
    max_buckets: int = 50,
) -> PCCPlan:

    if len(isps) < 2:
        raise ValueError(
            "At least 2 ISPs are required."
        )

    if max_buckets < len(isps):
        raise ValueError(
            "max_buckets must be at least "
            "the number of ISPs."
        )

    names = [
        isp.name.lower()
        for isp in isps
    ]

    if len(names) != len(set(names)):
        raise ValueError(
            "ISP names must be unique."
        )

    for isp in isps:
        if isp.bandwidth_mbps <= 0:
            raise ValueError(
                f"{isp.name}: bandwidth must "
                "be greater than zero."
            )

    bandwidths = [
        isp.bandwidth_mbps
        for isp in isps
    ]

    target_ratio = simplify_ratio(
        bandwidths
    )

    bucket_ratio, exact = choose_bucket_ratio(
        target_ratio=target_ratio,
        max_buckets=max_buckets,
    )

    total_buckets = sum(bucket_ratio)

    total_bandwidth = sum(bandwidths)

    plans = []

    bucket_start = 0

    for index, isp in enumerate(isps):

        bucket_count = bucket_ratio[index]

        buckets = tuple(
            range(
                bucket_start,
                bucket_start + bucket_count,
            )
        )

        exact_percentage = (
            isp.bandwidth_mbps
            / total_bandwidth
            * Decimal("100")
        )

        pcc_percentage = (
            Decimal(bucket_count)
            / Decimal(total_buckets)
            * Decimal("100")
        )

        plans.append(
            ISPPlan(
                isp=isp,
                exact_percentage=exact_percentage,
                bucket_count=bucket_count,
                buckets=buckets,
                pcc_percentage=pcc_percentage,
            )
        )

        bucket_start += bucket_count

    return PCCPlan(
        isps=tuple(isps),
        target_ratio=tuple(target_ratio),
        bucket_ratio=tuple(bucket_ratio),
        total_buckets=total_buckets,
        exact=exact,
        plans=tuple(plans),
    )


# ============================================================
# PCC CLASSIFIER
# ============================================================

def pcc_classifier(
    total_buckets: int,
    bucket: int,
    classifier: str = "both-addresses-and-ports",
) -> str:

    if bucket < 0 or bucket >= total_buckets:
        raise ValueError(
            f"Invalid PCC bucket: {bucket}"
        )

    return (
        f"{classifier}:"
        f"{total_buckets}/"
        f"{bucket}"
    )


# ============================================================
# PCC CONNECTION MARK RULES
# ============================================================

def generate_connection_mark_rules(
    plan: PCCPlan,
    interface_list: str = "LAN",
    classifier: str = "both-addresses-and-ports",
) -> list[str]:

    rules = []

    for isp_plan in plan.plans:

        isp = isp_plan.isp

        for bucket in isp_plan.buckets:

            classifier_value = pcc_classifier(
                total_buckets=plan.total_buckets,
                bucket=bucket,
                classifier=classifier,
            )

            rules.append(
                "add "
                "chain=prerouting "
                f"in-interface-list={interface_list} "
                "connection-state=new "
                "connection-mark=no-mark "
                "dst-address-type=!local "
                f"per-connection-classifier={classifier_value} "
                "action=mark-connection "
                f"new-connection-mark={isp.connection_mark} "
                "passthrough=yes "
                f'comment="{AUTO_PCC_PREFIX} '
                f'CONNECTION {isp.name}"'
            )

    return rules


# ============================================================
# ROUTING MARK RULES
# ============================================================

def generate_routing_mark_rules(
    plan: PCCPlan,
    interface_list: str = "LAN",
) -> list[str]:

    rules = []

    for isp_plan in plan.plans:

        isp = isp_plan.isp

        rules.append(
            "add "
            "chain=prerouting "
            f"in-interface-list={interface_list} "
            f"connection-mark={isp.connection_mark} "
            "dst-address-type=!local "
            "action=mark-routing "
            f"new-routing-mark={isp.routing_mark} "
            "passthrough=no "
            f'comment="{AUTO_PCC_PREFIX} '
            f'ROUTE {isp.name}"'
        )

    return rules


# ============================================================
# INBOUND CONNECTION MARKING
# ============================================================

def generate_inbound_connection_rules(
    plan: PCCPlan,
) -> list[str]:

    rules = []

    for isp_plan in plan.plans:

        isp = isp_plan.isp

        rules.append(
            "add "
            "chain=prerouting "
            f"in-interface={isp.interface} "
            "connection-state=new "
            "connection-mark=no-mark "
            "action=mark-connection "
            f"new-connection-mark={isp.connection_mark} "
            "passthrough=yes "
            f'comment="{AUTO_PCC_PREFIX} '
            f'INBOUND {isp.name}"'
        )

    return rules


# ============================================================
# INBOUND REPLY ROUTING
# ============================================================

def generate_inbound_reply_rules(
    plan: PCCPlan,
    wan_interface_list: str = "WAN",
) -> list[str]:

    rules = []

    for isp_plan in plan.plans:

        isp = isp_plan.isp

        rules.append(
            "add "
            "chain=prerouting "
            f"in-interface-list={wan_interface_list} "
            f"connection-mark={isp.connection_mark} "
            "action=mark-routing "
            f"new-routing-mark={isp.routing_mark} "
            "passthrough=no "
            f'comment="{AUTO_PCC_PREFIX} '
            f'INBOUND-ROUTE {isp.name}"'
        )

    return rules


# ============================================================
# ROUTER GENERATED TRAFFIC
# ============================================================

def generate_output_rules(
    plan: PCCPlan,
) -> list[str]:

    rules = []

    for isp_plan in plan.plans:

        isp = isp_plan.isp

        rules.append(
            "add "
            "chain=output "
            f"connection-mark={isp.connection_mark} "
            "action=mark-routing "
            f"new-routing-mark={isp.routing_mark} "
            "passthrough=no "
            f'comment="{AUTO_PCC_PREFIX} '
            f'OUTPUT {isp.name}"'
        )

    return rules


# ============================================================
# ROUTING TABLES
# ============================================================

def generate_routing_table_commands(
    plan: PCCPlan,
) -> list[str]:

    commands = [
        "/routing table"
    ]

    for isp_plan in plan.plans:

        isp = isp_plan.isp

        commands.append(
            f':if ([:len [find name="{isp.routing_table}"]] = 0) do={{ '
            f'add fib name="{isp.routing_table}" '
            f'}}'
        )

    return commands


# ============================================================
# ROUTES
# ============================================================

def generate_route_commands(
    plan: PCCPlan,
) -> list[str]:

    commands = [
        "/ip route"
    ]

    for isp_plan in plan.plans:

        isp = isp_plan.isp

        commands.append(
            "add "
            "dst-address=0.0.0.0/0 "
            f"gateway={isp.gateway} "
            f"routing-table={isp.routing_table} "
            "distance=1 "
            "check-gateway=ping "
            f'comment="{AUTO_PCC_PREFIX} '
            f'ROUTE-WAN {isp.name}"'
        )

    return commands


# ============================================================
# CLEANUP
# ============================================================

def generate_cleanup_commands() -> list[str]:

    return [
        "# Remove ONLY rules generated by this tool",
        "# Existing mangle rules are untouched.",
        "",
        "/ip firewall mangle",
        f'remove [find comment~"{AUTO_PCC_PREFIX}"]',
    ]


# ============================================================
# FULL UPDATE SCRIPT
# ============================================================

def generate_update_script(
    plan: PCCPlan,
    interface_list: str = "LAN",
    wan_interface_list: str = "WAN",
    classifier: str = "both-addresses-and-ports",
) -> str:

    sections = []

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    sections.append(
        "# ============================================================\n"
        "# AUTO-GENERATED MIKROTIK PCC CONFIGURATION\n"
        "# ============================================================\n"
        "# This script manages ONLY AUTO-PCC rules.\n"
        "# Existing manual rules are not removed.\n"
        "# ============================================================"
    )

    # --------------------------------------------------------
    # CLEAN OLD PCC RULES
    # --------------------------------------------------------

    sections.extend(
        generate_cleanup_commands()
    )

    # --------------------------------------------------------
    # PCC CONNECTION MARKING
    # --------------------------------------------------------

    sections.append(
        "\n# ============================================================\n"
        "# PCC CONNECTION MARKING\n"
        "# ============================================================\n"
        "/ip firewall mangle"
    )

    sections.extend(
        generate_connection_mark_rules(
            plan=plan,
            interface_list=interface_list,
            classifier=classifier,
        )
    )

    # --------------------------------------------------------
    # ROUTING MARKING
    # --------------------------------------------------------

    sections.append(
        "\n# ============================================================\n"
        "# POLICY ROUTING MARKING\n"
        "# ============================================================\n"
        "/ip firewall mangle"
    )

    sections.extend(
        generate_routing_mark_rules(
            plan=plan,
            interface_list=interface_list,
        )
    )

    # --------------------------------------------------------
    # INBOUND CONNECTIONS
    # --------------------------------------------------------

    sections.append(
        "\n# ============================================================\n"
        "# INBOUND WAN CONNECTION MARKING\n"
        "# ============================================================\n"
        "/ip firewall mangle"
    )

    sections.extend(
        generate_inbound_connection_rules(
            plan=plan,
        )
    )

    # --------------------------------------------------------
    # INBOUND REPLIES
    # --------------------------------------------------------

    sections.append(
        "\n# ============================================================\n"
        "# INBOUND REPLY ROUTING\n"
        "# ============================================================\n"
        "/ip firewall mangle"
    )

    sections.extend(
        generate_inbound_reply_rules(
            plan=plan,
            wan_interface_list=wan_interface_list,
        )
    )

    # --------------------------------------------------------
    # ROUTER GENERATED TRAFFIC
    # --------------------------------------------------------

    sections.append(
        "\n# ============================================================\n"
        "# ROUTER GENERATED TRAFFIC\n"
        "# ============================================================\n"
        "/ip firewall mangle"
    )

    sections.extend(
        generate_output_rules(
            plan=plan,
        )
    )

    # --------------------------------------------------------
    # ROUTING TABLES
    # --------------------------------------------------------

    sections.append(
        "\n# ============================================================\n"
        "# ROUTING TABLES\n"
        "# ============================================================"
    )

    sections.extend(
        generate_routing_table_commands(
            plan=plan,
        )
    )

    # --------------------------------------------------------
    # ROUTES
    # --------------------------------------------------------

    sections.append(
        "\n# ============================================================\n"
        "# WAN POLICY ROUTES\n"
        "# ============================================================\n"
        "/ip route"
    )

    sections.extend(
        generate_route_commands(
            plan=plan,
        )
    )

    return "\n".join(sections)


# ============================================================
# REPORT
# ============================================================

def print_report(
    plan: PCCPlan,
) -> None:

    print()
    print("=" * 75)
    print("PCC BANDWIDTH PLAN")
    print("=" * 75)

    print()

    print("Bandwidth:")

    for isp in plan.isps:
        print(
            f"  {isp.name}: "
            f"{isp.bandwidth_mbps} Mbps"
        )

    print()

    print("Exact mathematical ratio:")

    print(
        "  "
        + " : ".join(
            str(value)
            for value in plan.target_ratio
        )
    )

    print("Selected PCC bucket ratio:")

    print(
        "  "
        + " : ".join(
            str(value)
            for value in plan.bucket_ratio
        )
    )

    print()

    print(
        f"Total buckets: {plan.total_buckets}"
    )

    print(
        "Exact ratio: "
        + (
            "YES"
            if plan.exact
            else "NO - APPROXIMATION"
        )
    )

    print()

    print("-" * 75)

    for isp_plan in plan.plans:

        isp = isp_plan.isp

        print(isp.name)

        print(
            f"  Bandwidth:       "
            f"{isp.bandwidth_mbps} Mbps"
        )

        print(
            f"  Actual share:    "
            f"{isp_plan.exact_percentage:.2f}%"
        )

        print(
            f"  PCC share:       "
            f"{isp_plan.pcc_percentage:.2f}%"
        )

        print(
            f"  Bucket count:    "
            f"{isp_plan.bucket_count}"
        )

        print(
            f"  Buckets:         "
            f"{list(isp_plan.buckets)}"
        )

        print(
            f"  Connection mark: "
            f"{isp.connection_mark}"
        )

        print(
            f"  Routing mark:    "
            f"{isp.routing_mark}"
        )

        print()

    print("=" * 75)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # ========================================================
    # ISP CONFIGURATION
    #
    # CHANGE ONLY bandwidth_mbps WHEN BANDWIDTH CHANGES
    # ========================================================

    isps = [
        ISP(
            name="ISP1",
            bandwidth_mbps=Decimal("100"),
            interface="eth1-WAN-ISP1",
            gateway="202.5.56.158",
            routing_table="to_ISP1",
            connection_mark="ISP1_CM",
            routing_mark="to_ISP1",
        ),

        ISP(
            name="ISP2",
            bandwidth_mbps=Decimal("30"),
            interface="eth2-WAN-ISP2",
            gateway="103.12.200.1",
            routing_table="to_ISP2",
            connection_mark="ISP2_CM",
            routing_mark="to_ISP2",
        ),
    ]

    # ========================================================
    # CREATE PLAN
    # ========================================================

    plan = create_pcc_plan(
        isps=isps,
        max_buckets=50,
    )

    # ========================================================
    # PRINT CALCULATION
    # ========================================================

    print_report(plan)

    # ========================================================
    # GENERATE ROUTEROS SCRIPT
    # ========================================================

    script = generate_update_script(
        plan=plan,
        interface_list="LAN",
        wan_interface_list="WAN",
        classifier="both-addresses-and-ports",
    )

    print()
    print("=" * 75)
    print("ROUTEROS SCRIPT")
    print("=" * 75)
    print()
    print(script)

    # ========================================================
    # SAVE FILE
    # ========================================================

    with open(
        "pcc-update.rsc",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(script)

    print()
    print("Generated: pcc-update.rsc")