"""Cross-platform DNS configuration — factory for platform-specific setters."""

import sys

from simurgh_dns.platform_dns.base import DNSSetter


def get_dns_setter() -> DNSSetter:
    """Return a DNSSetter for the current platform."""
    if sys.platform == "darwin":
        from simurgh_dns.platform_dns.macos import MacOSDNSSetter

        return MacOSDNSSetter()
    elif sys.platform == "linux":
        from simurgh_dns.platform_dns.linux import LinuxDNSSetter

        return LinuxDNSSetter()
    elif sys.platform == "win32":
        from simurgh_dns.platform_dns.windows import WindowsDNSSetter

        return WindowsDNSSetter()
    else:
        msg = f"Unsupported platform: {sys.platform}"
        raise RuntimeError(msg)


__all__ = ["DNSSetter", "get_dns_setter"]
