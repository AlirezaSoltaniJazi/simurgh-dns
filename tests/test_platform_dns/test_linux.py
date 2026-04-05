"""Tests for Linux DNS setter."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from simurgh_dns.platform_dns.linux import LinuxDNSSetter


@pytest.fixture
def setter_resolvectl() -> LinuxDNSSetter:
    with patch("shutil.which", return_value="/usr/bin/resolvectl"):
        return LinuxDNSSetter()


@pytest.fixture
def setter_resolv_conf() -> LinuxDNSSetter:
    with patch("shutil.which", return_value=None):
        return LinuxDNSSetter()


class TestGetActiveInterface:
    @patch("subprocess.run")
    def test_finds_interface(
        self,
        mock_run: MagicMock,
        setter_resolvectl: LinuxDNSSetter,
    ) -> None:
        mock_run.return_value = MagicMock(
            stdout=("1.1.1.1 via 192.168.1.1 dev eth0 src 192.168.1.100")
        )
        assert setter_resolvectl.get_active_interface() == "eth0"

    @patch("subprocess.run")
    def test_command_not_found(
        self,
        mock_run: MagicMock,
        setter_resolvectl: LinuxDNSSetter,
    ) -> None:
        mock_run.side_effect = FileNotFoundError
        assert setter_resolvectl.get_active_interface() is None


class TestResolvectlDns:
    @patch("subprocess.run")
    def test_get_dns(
        self,
        mock_run: MagicMock,
        setter_resolvectl: LinuxDNSSetter,
    ) -> None:
        mock_run.return_value = MagicMock(stdout="Link 2 (eth0): 8.8.8.8 8.8.4.4")
        result = setter_resolvectl.get_current_dns("eth0")
        assert "8.8.8.8" in result

    @patch("subprocess.run")
    def test_set_dns(
        self,
        mock_run: MagicMock,
        setter_resolvectl: LinuxDNSSetter,
    ) -> None:
        assert setter_resolvectl.set_dns("eth0", ["1.1.1.1"]) is True

    @patch("subprocess.run")
    def test_set_dns_failure(
        self,
        mock_run: MagicMock,
        setter_resolvectl: LinuxDNSSetter,
    ) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, "resolvectl")
        assert setter_resolvectl.set_dns("eth0", ["1.1.1.1"]) is False

    @patch("subprocess.run")
    def test_reset_dns(
        self,
        mock_run: MagicMock,
        setter_resolvectl: LinuxDNSSetter,
    ) -> None:
        assert setter_resolvectl.reset_dns("eth0") is True


class TestResolvConfDns:
    @patch("simurgh_dns.platform_dns.linux.RESOLV_CONF")
    def test_get_dns(
        self,
        mock_path: MagicMock,
        setter_resolv_conf: LinuxDNSSetter,
    ) -> None:
        mock_path.read_text.return_value = "nameserver 8.8.8.8\nnameserver 8.8.4.4\n"
        result = setter_resolv_conf.get_current_dns("eth0")
        assert result == ["8.8.8.8", "8.8.4.4"]

    @patch("subprocess.run")
    @patch("simurgh_dns.platform_dns.linux.RESOLV_CONF_BACKUP")
    @patch("simurgh_dns.platform_dns.linux.RESOLV_CONF")
    def test_set_dns(
        self,
        mock_conf: MagicMock,
        mock_backup: MagicMock,
        mock_run: MagicMock,
        setter_resolv_conf: LinuxDNSSetter,
    ) -> None:
        mock_conf.exists.return_value = True
        mock_backup.exists.return_value = False
        assert setter_resolv_conf.set_dns("eth0", ["1.1.1.1"]) is True
