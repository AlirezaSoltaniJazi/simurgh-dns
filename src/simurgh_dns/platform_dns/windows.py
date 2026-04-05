"""Windows DNS configuration via netsh."""

import subprocess

from simurgh_dns.platform_dns.base import DNSSetter


class WindowsDNSSetter(DNSSetter):
    """DNS setter for Windows using netsh."""

    def get_active_interface(self) -> str | None:
        """Detect the active network interface on Windows."""
        try:
            result = subprocess.run(
                [
                    "netsh",
                    "interface",
                    "ipv4",
                    "show",
                    "config",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            current_interface = None
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line.startswith("Configuration for interface"):
                    current_interface = line.split('"')[1] if '"' in line else None
                elif "IP Address:" in line and current_interface:
                    ip_part = line.split(":")[-1].strip()
                    if ip_part and ip_part != "0.0.0.0":  # noqa: S104
                        return current_interface
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            IndexError,
        ):
            pass
        return None

    def get_current_dns(self, interface: str) -> list[str]:
        """Get the current DNS servers for an interface."""
        try:
            result = subprocess.run(
                [
                    "netsh",
                    "interface",
                    "ipv4",
                    "show",
                    "dnsservers",
                    interface,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            servers = []
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line and line[0].isdigit() and "." in line:
                    servers.append(line.split()[0])
            if not servers:
                if "dhcp" in result.stdout.lower():
                    return ["(DHCP - automatic)"]
                return ["(automatic)"]
            return servers
        except subprocess.CalledProcessError:
            return ["(unknown)"]

    def set_dns(self, interface: str, dns_ips: list[str]) -> bool:
        """Set DNS servers for an interface."""
        try:
            subprocess.run(
                [
                    "netsh",
                    "interface",
                    "ipv4",
                    "set",
                    "dns",
                    f"name={interface}",
                    "static",
                    dns_ips[0],
                ],
                check=True,
            )
            for i, ip in enumerate(dns_ips[1:], start=2):
                subprocess.run(
                    [
                        "netsh",
                        "interface",
                        "ipv4",
                        "add",
                        "dns",
                        f"name={interface}",
                        ip,
                        f"index={i}",
                    ],
                    check=True,
                )
            return True
        except subprocess.CalledProcessError:
            return False

    def reset_dns(self, interface: str) -> bool:
        """Reset DNS to DHCP default."""
        try:
            subprocess.run(
                [
                    "netsh",
                    "interface",
                    "ipv4",
                    "set",
                    "dns",
                    f"name={interface}",
                    "dhcp",
                ],
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
