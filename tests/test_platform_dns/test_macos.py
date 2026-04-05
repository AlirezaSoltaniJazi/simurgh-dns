"""Tests for macOS DNS setter."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from simurgh_dns.platform_dns.macos import MacOSDNSSetter


@pytest.fixture
def setter() -> MacOSDNSSetter:
    return MacOSDNSSetter()


class TestGetActiveInterface:
    @patch("subprocess.run")
    def test_finds_active_service(
        self, mock_run: MagicMock, setter: MacOSDNSSetter
    ) -> None:
        mock_run.side_effect = [
            MagicMock(stdout="An asterisk denotes...\nWi-Fi\nEthernet"),
            MagicMock(stdout="IP address: 192.168.1.100\n"),
        ]
        assert setter.get_active_interface() == "Wi-Fi"

    @patch("subprocess.run")
    def test_no_active_service(
        self, mock_run: MagicMock, setter: MacOSDNSSetter
    ) -> None:
        mock_run.side_effect = [
            MagicMock(stdout="An asterisk denotes...\nWi-Fi"),
            MagicMock(stdout="IP address: none\n"),
        ]
        assert setter.get_active_interface() is None

    @patch("subprocess.run")
    def test_command_not_found(
        self, mock_run: MagicMock, setter: MacOSDNSSetter
    ) -> None:
        mock_run.side_effect = FileNotFoundError
        assert setter.get_active_interface() is None


class TestGetCurrentDns:
    @patch("subprocess.run")
    def test_has_dns_servers(self, mock_run: MagicMock, setter: MacOSDNSSetter) -> None:
        mock_run.return_value = MagicMock(stdout="8.8.8.8\n8.8.4.4\n")
        assert setter.get_current_dns("Wi-Fi") == [
            "8.8.8.8",
            "8.8.4.4",
        ]

    @patch("subprocess.run")
    def test_dhcp_automatic(self, mock_run: MagicMock, setter: MacOSDNSSetter) -> None:
        mock_run.return_value = MagicMock(
            stdout="There aren't any DNS Servers set on Wi-Fi."
        )
        assert setter.get_current_dns("Wi-Fi") == ["(DHCP - automatic)"]


class TestSetDns:
    @patch("subprocess.run")
    def test_success(self, mock_run: MagicMock, setter: MacOSDNSSetter) -> None:
        assert setter.set_dns("Wi-Fi", ["1.1.1.1", "1.0.0.1"]) is True

    @patch("subprocess.run")
    def test_failure(self, mock_run: MagicMock, setter: MacOSDNSSetter) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, "networksetup")
        assert setter.set_dns("Wi-Fi", ["1.1.1.1"]) is False


class TestResetDns:
    @patch("subprocess.run")
    def test_success(self, mock_run: MagicMock, setter: MacOSDNSSetter) -> None:
        assert setter.reset_dns("Wi-Fi") is True

    @patch("subprocess.run")
    def test_failure(self, mock_run: MagicMock, setter: MacOSDNSSetter) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, "networksetup")
        assert setter.reset_dns("Wi-Fi") is False
