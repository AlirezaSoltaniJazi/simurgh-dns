"""DNS server registry and benchmark constants."""

DNS_SERVERS: dict[str, list[str]] = {
    "Google": ["8.8.8.8", "8.8.4.4"],
    "Cloudflare": ["1.1.1.1", "1.0.0.1"],
    "Quad9": ["9.9.9.9", "149.112.112.112"],
    "OpenDNS": ["208.67.222.222", "208.67.220.220"],
    "AdGuard": ["94.140.14.14", "94.140.15.15"],
    "NextDNS": ["45.90.28.0", "45.90.30.0"],
    "CleanBrowsing": ["185.228.168.9", "185.228.169.9"],
    "Comodo Secure": ["8.26.56.26", "8.20.247.20"],
    "Level3": ["4.2.2.1", "4.2.2.2"],
    "Verisign": ["64.6.64.6", "64.6.65.6"],
    "Norton/LifeLock": ["199.85.126.10", "199.85.127.10"],
    "Yandex": ["77.88.8.8", "77.88.8.1"],
    "DNS.WATCH": ["84.200.69.80", "84.200.70.40"],
    "Freenom": ["80.80.80.80", "80.80.81.81"],
    "Alternate DNS": ["76.76.19.19", "76.223.122.150"],
}

TEST_DOMAINS: list[str] = [
    "google.com",
    "amazon.com",
    "github.com",
    "youtube.com",
    "wikipedia.org",
]

DEFAULT_TIMEOUT = 3
DEFAULT_ROUNDS = 3
DEFAULT_MAX_WORKERS = 10
