"""macOS DNS configuration via networksetup."""

import subprocess

from simurgh_dns.platform_dns.base import DNSSetter


class MacOSDNSSetter(DNSSetter):
    """DNS setter for macOS using networksetup."""

    def get_active_interface(self) -> str | None:
        """Detect the active network service on macOS."""
        try:
            result = subprocess.run(
                ["networksetup", "-listallnetworkservices"],
                capture_output=True,
                text=True,
                check=True,
            )
            services = [
                line
                for line in result.stdout.strip().split("\n")[1:]
                if not line.startswith("*")
            ]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

        for service in services:
            try:
                info = subprocess.run(
                    ["networksetup", "-getinfo", service],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                for line in info.stdout.split("\n"):
                    if line.startswith("IP address:") and "none" not in line.lower():
                        return service
            except subprocess.CalledProcessError:
                continue

        return None

    def get_current_dns(self, interface: str) -> list[str]:
        """Get the current DNS servers for a network service."""
        try:
            result = subprocess.run(
                ["networksetup", "-getdnsservers", interface],
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout.strip()
            if "any dns" in output.lower() or "there aren't" in output.lower():
                return ["(DHCP - automatic)"]
            return [line.strip() for line in output.split("\n") if line.strip()]
        except subprocess.CalledProcessError:
            return ["(unknown)"]

    def set_dns(self, interface: str, dns_ips: list[str]) -> bool:
        """Set DNS servers for a network service (requires sudo)."""
        try:
            subprocess.run(
                [
                    "sudo",
                    "networksetup",
                    "-setdnsservers",
                    interface,
                    *dns_ips,
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
                    "sudo",
                    "networksetup",
                    "-setdnsservers",
                    interface,
                    "empty",
                ],
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
