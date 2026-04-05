"""Abstract base class for platform-specific DNS configuration."""

from abc import ABC, abstractmethod


class DNSSetter(ABC):
    """Interface for getting and setting system DNS servers."""

    @abstractmethod
    def get_active_interface(self) -> str | None:
        """Detect the active network interface/service name."""

    @abstractmethod
    def get_current_dns(self, interface: str) -> list[str]:
        """Get the current DNS servers for a network interface."""

    @abstractmethod
    def set_dns(self, interface: str, dns_ips: list[str]) -> bool:
        """Set DNS servers for a network interface. Returns True on success."""

    @abstractmethod
    def reset_dns(self, interface: str) -> bool:
        """Reset DNS to DHCP default. Returns True on success."""
