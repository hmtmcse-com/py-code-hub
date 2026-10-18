from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from math import gcd
from pathlib import Path

# ============================================================
# SOHOZ CLOUD BFE - PRODUCTION PCC MANGLE GENERATOR
# ============================================================
#
# Router:
#   SC-BFE-MR1
#
# WAN:
#   ISP1 = 100 Mbps
#   ISP2 = 30 Mbps
#
# PCC:
#   100 : 30
#   = 10 : 3
#   = 13 buckets
#
# MANAGED:
#   - WAN inbound connection marking
#   - PCC connection classification
#   - Connection mark -> routing mark
#   - WAN inbound reply routing
#   - Router output routing for existing marked connections
#
# NOT MANAGED:
#   - Interface lists
#   - Interface list membership
#   - Manual PCC bypass rules
#   - Firewall
#   - NAT
#   - Routing tables
#   - Static routes
#   - Failover
#   - WireGuard
#
# ============================================================


# ============================================================
# GENERAL CONFIGURATION
# ============================================================

OUTPUT_FILE = Path("mikrotik_pcc_mangle.rsc")

PCC_INTERFACE_LIST = "PCC"
WAN_INTERFACE_LIST = "WAN"

AUTO_PREFIX = "AUTO-PCC"

PCC_METHOD = "both-addresses-and-ports"


# ============================================================
# ISP CONFIGURATION
# ============================================================

@dataclass(frozen=True)
class ISP:
    name: str
    bandwidth_mbps: Decimal
    interface: str
    connection_mark: str
    routing_table: str


ISPS = (
    ISP(
        name="ISP1",
        bandwidth_mbps=Decimal("100"),
        interface="eth1-WAN-ISP1",
        connection_mark="ISP1_CM",
        routing_table="to_ISP1",
    ),
    ISP(
        name="ISP2",
        bandwidth_mbps=Decimal("30"),
        interface="eth2-WAN-ISP2",
        connection_mark="ISP2_CM",
        routing_table="to_ISP2",
    ),
)


# ============================================================
# RATIO CALCULATION
# ============================================================

def simplify_ratio(values: list[int]) -> tuple[int, ...]:
    divisor = 0

    for value in values:
        divisor = gcd(divisor, value)

    if divisor == 0:
        raise ValueError("Bandwidth values cannot all be zero.")

    return tuple(value // divisor for value in values)


def bandwidth_ratio(isps: tuple[ISP, ...]) -> tuple[int, ...]:
    fractions = [
        Fraction(isp.bandwidth_mbps)
        for isp in isps
    ]

    common_denominator = 1

    for fraction in fractions:
        common_denominator = (
                common_denominator
                * fraction.denominator
                // gcd(
            common_denominator,
            fraction.denominator,
        )
        )

    integers = [
        fraction.numerator
        * (
                common_denominator
                // fraction.denominator
        )
        for fraction in fractions
    ]

    return simplify_ratio(integers)


def calculate_bucket_ratio(
        exact_ratio: tuple[int, ...],
        max_buckets: int,
) -> tuple[int, ...]:
    total = sum(exact_ratio)

    # Exact ratio fits.
    if total <= max_buckets:
        return exact_ratio

    # Approximate using largest remainder.
    shares = [
        Decimal(value) / Decimal(total)
        for value in exact_ratio
    ]

    base = [
        max(
            1,
            int(share * max_buckets),
        )
        for share in shares
    ]

    while sum(base) > max_buckets:

        index = min(
            range(len(base)),
            key=lambda i:
            shares[i] - Decimal(base[i]),
        )

        if base[index] > 1:
            base[index] -= 1
        else:
            break

    while sum(base) < max_buckets:
        index = max(
            range(len(base)),
            key=lambda i:
            shares[i] - Decimal(base[i]),
        )

        base[index] += 1

    return tuple(base)


def percentage(
        value: int,
        total: int,
) -> Decimal:
    return (
            Decimal(value)
            * Decimal("100")
            / Decimal(total)
    ).quantize(
        Decimal("0.01")
    )


# ============================================================
# PCC PLAN
# ============================================================

@dataclass(frozen=True)
class ISPPlan:
    isp: ISP
    exact_share: Decimal
    pcc_share: Decimal
    bucket_count: int
    buckets: tuple[int, ...]


@dataclass(frozen=True)
class PCCPlan:
    isps: tuple[ISP, ...]
    exact_ratio: tuple[int, ...]
    bucket_ratio: tuple[int, ...]
    total_buckets: int
    exact: bool
    plans: tuple[ISPPlan, ...]


def build_plan(
        isps: tuple[ISP, ...],
        max_buckets: int = 50,
) -> PCCPlan:
    if not isps:
        raise ValueError(
            "At least one ISP is required."
        )

    if any(
            isp.bandwidth_mbps <= 0
            for isp in isps
    ):
        raise ValueError(
            "ISP bandwidth must be greater than zero."
        )

    exact_ratio = bandwidth_ratio(isps)

    bucket_ratio = calculate_bucket_ratio(
        exact_ratio,
        max_buckets,
    )

    total_buckets = sum(bucket_ratio)

    exact = (
            exact_ratio == bucket_ratio
    )

    total_bandwidth = sum(
        isp.bandwidth_mbps
        for isp in isps
    )

    plans: list[ISPPlan] = []

    bucket_index = 0

    for isp, bucket_count in zip(
            isps,
            bucket_ratio,
    ):
        buckets = tuple(
            range(
                bucket_index,
                bucket_index + bucket_count,
            )
        )

        bucket_index += bucket_count

        exact_share = (
                isp.bandwidth_mbps
                * Decimal("100")
                / total_bandwidth
        ).quantize(
            Decimal("0.01")
        )

        pcc_share = percentage(
            bucket_count,
            total_buckets,
        )

        plans.append(
            ISPPlan(
                isp=isp,
                exact_share=exact_share,
                pcc_share=pcc_share,
                bucket_count=bucket_count,
                buckets=buckets,
            )
        )

    return PCCPlan(
        isps=isps,
        exact_ratio=exact_ratio,
        bucket_ratio=bucket_ratio,
        total_buckets=total_buckets,
        exact=exact,
        plans=tuple(plans),
    )


# ============================================================
# ROUTEROS STRING
# ============================================================

def ros(value: str) -> str:
    escaped = (
        value
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )

    return f'"{escaped}"'


# ============================================================
# HEADER
# ============================================================

def render_header(
        plan: PCCPlan,
) -> list[str]:
    bandwidth = " + ".join(
        f"{isp.name}={isp.bandwidth_mbps:g} Mbps"
        for isp in plan.isps
    )

    ratio = ":".join(
        str(value)
        for value in plan.exact_ratio
    )

    bucket_ratio = ":".join(
        str(value)
        for value in plan.bucket_ratio
    )

    lines = [
        "# ============================================================",
        "# AUTO-GENERATED MIKROTIK PCC MANGLE CONFIGURATION",
        "# ============================================================",
        "#",
        "# RouterOS 7.x",
        "#",
        "# Generator manages ONLY rules beginning with:",
        "#   AUTO-PCC",
        "#",
        "# ============================================================",
        "# MANAGED",
        "# ============================================================",
        "#",
        "#   WAN inbound connection marking",
        "#   PCC connection classification",
        "#   Connection mark -> routing mark",
        "#   WAN inbound reply routing",
        "#   Router output routing",
        "#",
        "# ============================================================",
        "# NOT MANAGED",
        "# ============================================================",
        "#",
        "#   Interface lists",
        "#   Interface list membership",
        "#   NET-INTERNAL bypass",
        "#   NET-VPN bypass",
        "#   Firewall",
        "#   NAT",
        "#   Routing tables",
        "#   Static routes",
        "#   Failover",
        "#   WireGuard",
        "#",
        "# ============================================================",
        "# REQUIRED ROUTING TABLES",
        "# ============================================================",
        "#",
    ]

    for isp in plan.isps:
        lines.append(
            f"#   {isp.routing_table}"
        )

    lines.extend(
        [
            "#",
            "# ============================================================",
            "# PCC MODEL",
            "# ============================================================",
            "#",
            f"# PCC interface list : {PCC_INTERFACE_LIST}",
            f"# WAN interface list : {WAN_INTERFACE_LIST}",
            "#",
            f"# Bandwidth          : {bandwidth}",
            f"# Exact ratio        : {ratio}",
            f"# PCC bucket ratio   : {bucket_ratio}",
            f"# Total buckets      : {plan.total_buckets}",
            (
                "# Exact              : "
                f"{'YES' if plan.exact else 'NO'}"
            ),
            "#",
            "# ============================================================",
            "# ISP DISTRIBUTION",
            "# ============================================================",
            "#",
        ]
    )

    for item in plan.plans:
        lines.extend(
            [
                f"# [{item.isp.name}]",
                (
                    "#   Bandwidth       : "
                    f"{item.isp.bandwidth_mbps:g} Mbps"
                ),
                (
                    "#   Exact share     : "
                    f"{item.exact_share}%"
                ),
                (
                    "#   PCC share       : "
                    f"{item.pcc_share}%"
                ),
                (
                    "#   Bucket count    : "
                    f"{item.bucket_count}"
                ),
                (
                    "#   Buckets         : "
                    f"{item.buckets}"
                ),
                (
                    "#   Connection mark : "
                    f"{item.isp.connection_mark}"
                ),
                (
                    "#   Routing table   : "
                    f"{item.isp.routing_table}"
                ),
                "#",
            ]
        )

    lines.extend(
        [
            "# ============================================================",
            "# REQUIRED MANGLE ORDER",
            "# ============================================================",
            "#",
            "# MANUAL RULES MUST BE ABOVE AUTO-PCC CLASSIFICATION:",
            "#",
            "#   1. NET-INTERNAL bypass",
            "#   2. NET-VPN bypass",
            "#",
            "# AUTO-PCC:",
            "#",
            "#   3. WAN inbound connection marking",
            "#   4. PCC connection classification",
            "#   5. Connection mark -> routing mark",
            "#   6. WAN inbound reply routing",
            "#   7. Router output routing",
            "#",
            "# ============================================================",
            "",
        ]
    )

    return lines


# ============================================================
# MANUAL BYPASS DOCUMENTATION
# ============================================================

def render_manual_bypass() -> list[str]:
    return [
        "# ============================================================",
        "# REQUIRED MANUAL PCC BYPASS RULES",
        "# ============================================================",
        "#",
        "# These rules are intentionally NOT managed by this script.",
        "#",
        "# They MUST be above AUTO-PCC classification rules.",
        "#",
        "# Apply manually:",
        "#",
        "/ip firewall mangle",
        (
            'add chain=prerouting '
            'dst-address-list=NET-INTERNAL '
            'action=accept '
            'comment="MANUAL PCC BYPASS NET-INTERNAL"'
        ),
        (
            'add chain=prerouting '
            'dst-address-list=NET-VPN '
            'action=accept '
            'comment="MANUAL PCC BYPASS NET-VPN"'
        ),
        "#",
        "# ============================================================",
        "",
    ]


# ============================================================
# CLEANUP
# ============================================================

def render_cleanup() -> list[str]:
    return [
        "# ============================================================",
        "# AUTO-PCC CLEANUP",
        "# ============================================================",
        "#",
        "# Removes ONLY AUTO-PCC generated rules.",
        "# Manual mangle rules are not touched.",
        "#",
        "/ip firewall mangle",
        'remove [find where comment~"^AUTO-PCC "]',
        "",
    ]


# ============================================================
# WAN INBOUND CONNECTION MARKING
# ============================================================

def render_wan_inbound(
        plan: PCCPlan,
) -> list[str]:
    lines = [
        "# ============================================================",
        "# AUTO-PCC WAN INBOUND CONNECTION MARKING",
        "# ============================================================",
        "#",
        "# Marks NEW connections according to the WAN interface",
        "# on which the connection arrived.",
        "#",
        "# Used for:",
        "#   - Port forwarding",
        "#   - Public services",
        "#   - Inbound connections",
        "#   - Symmetric replies",
        "#",
        "/ip firewall mangle",
    ]

    for item in plan.plans:
        isp = item.isp

        lines.append(
            "add "
            "chain=prerouting "
            f"in-interface={ros(isp.interface)} "
            "connection-state=new "
            "connection-mark=no-mark "
            "action=mark-connection "
            f"new-connection-mark={ros(isp.connection_mark)} "
            "passthrough=yes "
            f"comment={ros(
                f'{AUTO_PREFIX} INBOUND {isp.name}'
            )}"
        )

    lines.append("")

    return lines


# ============================================================
# PCC CLASSIFICATION
# ============================================================

def render_pcc_classification(
        plan: PCCPlan,
) -> list[str]:
    lines = [
        "# ============================================================",
        "# AUTO-PCC CONNECTION CLASSIFICATION",
        "# ============================================================",
        "#",
        f"# PCC interface list = {PCC_INTERFACE_LIST}",
        "#",
        "# Only NEW and unmarked connections are classified.",
        "# Existing connection marks are preserved.",
        "#",
        "# Manual NET-INTERNAL / NET-VPN bypass rules must be",
        "# above these rules.",
        "#",
        f"# Total PCC buckets = {plan.total_buckets}",
        "#",
        "/ip firewall mangle",
    ]

    for item in plan.plans:

        isp = item.isp

        for bucket in item.buckets:
            comment = (
                f"{AUTO_PREFIX} CONNECTION "
                f"{isp.name} BUCKET-{bucket}"
            )

            lines.append(
                "add "
                "chain=prerouting "
                f"in-interface-list={ros(PCC_INTERFACE_LIST)} "
                "connection-state=new "
                "connection-mark=no-mark "
                "dst-address-type=!local "
                f"per-connection-classifier="
                f"{PCC_METHOD}:{plan.total_buckets}/{bucket} "
                "action=mark-connection "
                f"new-connection-mark={ros(isp.connection_mark)} "
                "passthrough=yes "
                f"comment={ros(comment)}"
            )

    lines.append("")

    return lines


# ============================================================
# CONNECTION MARK -> ROUTING MARK
# ============================================================

def render_connection_to_route(
        plan: PCCPlan,
) -> list[str]:
    lines = [
        "# ============================================================",
        "# AUTO-PCC CONNECTION MARK -> ROUTING MARK",
        "# ============================================================",
        "#",
        "# PCC interface membership is NOT checked here.",
        "#",
        "# PCC membership is only used for NEW connection",
        "# classification.",
        "#",
        "/ip firewall mangle",
    ]

    for item in plan.plans:
        isp = item.isp

        comment = (
            f"{AUTO_PREFIX} ROUTE {isp.name}"
        )

        lines.append(
            "add "
            "chain=prerouting "
            f"connection-mark={ros(isp.connection_mark)} "
            "dst-address-type=!local "
            "action=mark-routing "
            f"new-routing-mark={ros(isp.routing_table)} "
            "passthrough=no "
            f"comment={ros(comment)}"
        )

    lines.append("")

    return lines


# ============================================================
# WAN INBOUND REPLY ROUTING
# ============================================================

def render_inbound_route(
        plan: PCCPlan,
) -> list[str]:
    lines = [
        "# ============================================================",
        "# AUTO-PCC WAN INBOUND REPLY ROUTING",
        "# ============================================================",
        "#",
        "# Keeps inbound connections on the WAN routing table",
        "# from which the connection originally arrived.",
        "#",
        "/ip firewall mangle",
    ]

    for item in plan.plans:
        isp = item.isp

        comment = (
            f"{AUTO_PREFIX} INBOUND-ROUTE "
            f"{isp.name}"
        )

        lines.append(
            "add "
            "chain=prerouting "
            f"in-interface-list={ros(WAN_INTERFACE_LIST)} "
            f"connection-mark={ros(isp.connection_mark)} "
            "action=mark-routing "
            f"new-routing-mark={ros(isp.routing_table)} "
            "passthrough=no "
            f"comment={ros(comment)}"
        )

    lines.append("")

    return lines


# ============================================================
# ROUTER OUTPUT ROUTING
# ============================================================

def render_output_route(
        plan: PCCPlan,
) -> list[str]:
    lines = [
        "# ============================================================",
        "# AUTO-PCC ROUTER OUTPUT ROUTING",
        "# ============================================================",
        "#",
        "# This does NOT classify router-originated NEW connections.",
        "#",
        "# It only routes already-marked connections.",
        "#",
        "/ip firewall mangle",
    ]

    for item in plan.plans:
        isp = item.isp

        comment = (
            f"{AUTO_PREFIX} OUTPUT-ROUTE "
            f"{isp.name}"
        )

        lines.append(
            "add "
            "chain=output "
            f"connection-mark={ros(isp.connection_mark)} "
            "dst-address-type=!local "
            "action=mark-routing "
            f"new-routing-mark={ros(isp.routing_table)} "
            "passthrough=no "
            f"comment={ros(comment)}"
        )

    lines.append("")

    return lines


# ============================================================
# COMPLETE CONFIGURATION
# ============================================================

def render(
        plan: PCCPlan,
) -> str:
    lines: list[str] = []

    lines.extend(
        render_header(plan)
    )

    lines.extend(
        render_manual_bypass()
    )

    lines.extend(
        render_cleanup()
    )

    lines.extend(
        render_wan_inbound(plan)
    )

    lines.extend(
        render_pcc_classification(plan)
    )

    lines.extend(
        render_connection_to_route(plan)
    )

    lines.extend(
        render_inbound_route(plan)
    )

    lines.extend(
        render_output_route(plan)
    )

    lines.extend(
        [
            "# ============================================================",
            "# END AUTO-PCC CONFIGURATION",
            "# ============================================================",
            "",
        ]
    )

    return "\n".join(lines)


# ============================================================
# VALIDATION
# ============================================================

def validate(
        plan: PCCPlan,
) -> None:
    if plan.total_buckets <= 0:
        raise ValueError(
            "PCC must contain at least one bucket."
        )

    all_buckets = [
        bucket
        for item in plan.plans
        for bucket in item.buckets
    ]

    expected_buckets = list(
        range(plan.total_buckets)
    )

    if all_buckets != expected_buckets:
        raise ValueError(
            "PCC buckets are not continuous."
        )

    connection_marks = [
        isp.connection_mark
        for isp in plan.isps
    ]

    if len(connection_marks) != len(
            set(connection_marks)
    ):
        raise ValueError(
            "Duplicate connection marks detected."
        )

    routing_tables = [
        isp.routing_table
        for isp in plan.isps
    ]

    if len(routing_tables) != len(
            set(routing_tables)
    ):
        raise ValueError(
            "Duplicate routing tables detected."
        )

    interfaces = [
        isp.interface
        for isp in plan.isps
    ]

    if len(interfaces) != len(
            set(interfaces)
    ):
        raise ValueError(
            "Duplicate WAN interfaces detected."
        )

    if sum(
            item.bucket_count
            for item in plan.plans
    ) != plan.total_buckets:
        raise ValueError(
            "PCC bucket count mismatch."
        )


# ============================================================
# CONSOLE REPORT
# ============================================================

def print_report(
        plan: PCCPlan,
) -> None:
    bandwidth = " + ".join(
        f"{isp.name}={isp.bandwidth_mbps:g} Mbps"
        for isp in plan.isps
    )

    ratio = ":".join(
        str(value)
        for value in plan.exact_ratio
    )

    bucket_ratio = ":".join(
        str(value)
        for value in plan.bucket_ratio
    )

    print()
    print("=" * 72)
    print("AUTO-PCC PLAN")
    print("=" * 72)

    print(
        f"PCC interface list : "
        f"{PCC_INTERFACE_LIST}"
    )

    print(
        f"WAN interface list : "
        f"{WAN_INTERFACE_LIST}"
    )

    print()
    print(
        f"Bandwidth          : "
        f"{bandwidth}"
    )

    print(
        f"Exact ratio        : "
        f"{ratio}"
    )

    print(
        f"PCC bucket ratio   : "
        f"{bucket_ratio}"
    )

    print(
        f"Total buckets      : "
        f"{plan.total_buckets}"
    )

    print(
        f"Exact              : "
        f"{'YES' if plan.exact else 'NO'}"
    )

    print()
    print("-" * 72)
    print("ISP DISTRIBUTION")
    print("-" * 72)

    for item in plan.plans:
        print()
        print(
            f"[{item.isp.name}]"
        )

        print(
            f"  Bandwidth       : "
            f"{item.isp.bandwidth_mbps:g} Mbps"
        )

        print(
            f"  Exact share     : "
            f"{item.exact_share}%"
        )

        print(
            f"  PCC share       : "
            f"{item.pcc_share}%"
        )

        print(
            f"  Bucket count    : "
            f"{item.bucket_count}"
        )

        print(
            f"  Buckets         : "
            f"{item.buckets}"
        )

        print(
            f"  Connection mark : "
            f"{item.isp.connection_mark}"
        )

        print(
            f"  Routing table   : "
            f"{item.isp.routing_table}"
        )

    print()
    print("-" * 72)
    print("BUCKET MAPPING")
    print("-" * 72)

    print(
        f"{'Bucket':>8}  "
        f"{'ISP':<8}  "
        f"{'Connection Mark':<20}  "
        f"{'Routing Table'}"
    )

    print("-" * 72)

    for item in plan.plans:

        for bucket in item.buckets:
            print(
                f"{bucket:>8}  "
                f"{item.isp.name:<8}  "
                f"{item.isp.connection_mark:<20}  "
                f"{item.isp.routing_table}"
            )

    print()
    print("=" * 72)
    print(
        f"Generated: {OUTPUT_FILE.resolve()}"
    )
    print("=" * 72)
    print()


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    plan = build_plan(
        ISPS,
        max_buckets=50,
    )

    validate(plan)

    configuration = render(plan)

    OUTPUT_FILE.write_text(
        configuration,
        encoding="utf-8",
    )

    print_report(plan)


if __name__ == "__main__":
    main()
