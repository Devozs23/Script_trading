"""
Network utilities for IP detection and latency testing
"""
import requests
import time
import logging
from typing import Optional, Tuple


class NetworkUtils:
    """Network utility functions"""

    IP_SERVICES = [
        "https://api.ipify.org?format=json",
        "https://api.my-ip.io/ip.json",
        "https://ipapi.co/json/"
    ]

    PING_SERVERS = {
        "us-east": "https://cloudflare.com",
        "us-west": "https://cloudflare.com",
        "eu": "https://cloudflare.com",
        "asia": "https://cloudflare.com"
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.timeout = 5

    def get_current_ip(self) -> Optional[str]:
        """
        Get current public IP address

        Returns:
            str: IP address or None if failed
        """
        for service in self.IP_SERVICES:
            try:
                response = requests.get(service, timeout=self.timeout)
                response.raise_for_status()

                data = response.json()

                # Different services use different keys
                if 'ip' in data:
                    ip = data['ip']
                elif 'address' in data:
                    ip = data['address']
                else:
                    continue

                self.logger.info(f"Retrieved IP: {ip}")
                return ip

            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout getting IP from {service}")
                continue

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Failed to get IP from {service}: {e}")
                continue

            except Exception as e:
                self.logger.error(f"Error getting IP from {service}: {e}")
                continue

        self.logger.error("Failed to retrieve IP from all services")
        return None

    def test_latency(self, server_url: str = None) -> Optional[int]:
        """
        Test latency to a server

        Args:
            server_url: URL to test (default: Cloudflare)

        Returns:
            int: Latency in milliseconds or None if failed
        """
        if server_url is None:
            server_url = "https://1.1.1.1"

        try:
            start_time = time.time()
            response = requests.get(server_url, timeout=self.timeout)
            response.raise_for_status()
            latency = int((time.time() - start_time) * 1000)

            self.logger.debug(f"Latency to {server_url}: {latency}ms")
            return latency

        except requests.exceptions.Timeout:
            self.logger.warning(f"Timeout testing latency to {server_url}")
            return None

        except Exception as e:
            self.logger.error(f"Error testing latency: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test if internet connection is available

        Returns:
            bool: True if connected
        """
        try:
            response = requests.get("https://1.1.1.1", timeout=3)
            return response.status_code == 200

        except Exception:
            return False

    def get_location_info(self, ip: str = None) -> Optional[dict]:
        """
        Get location information for an IP

        Args:
            ip: IP address (None for current IP)

        Returns:
            dict: Location info or None
        """
        try:
            if ip:
                url = f"https://ipapi.co/{ip}/json/"
            else:
                url = "https://ipapi.co/json/"

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            return {
                'country': data.get('country_name', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'isp': data.get('org', 'Unknown')
            }

        except Exception as e:
            self.logger.error(f"Error getting location info: {e}")
            return None

    def test_all_servers(self) -> dict:
        """
        Test latency to all VPN servers

        Returns:
            dict: Server name -> latency (ms)
        """
        results = {}

        for server_name, server_url in self.PING_SERVERS.items():
            latency = self.test_latency(server_url)
            results[server_name] = latency if latency else -1

        return results

    def is_vpn_active(self) -> Tuple[bool, Optional[str]]:
        """
        Detect if a VPN is likely active by checking IP location

        Returns:
            Tuple[bool, str]: (is_vpn, reason)
        """
        try:
            location = self.get_location_info()
            if not location:
                return False, "Could not determine location"

            # Check if ISP contains VPN-related keywords
            isp = location.get('isp', '').lower()
            vpn_keywords = ['cloudflare', 'warp', 'vpn', 'proxy', 'hosting', 'datacenter']

            for keyword in vpn_keywords:
                if keyword in isp:
                    return True, f"VPN detected: {location.get('isp')}"

            return False, "No VPN detected"

        except Exception as e:
            self.logger.error(f"Error checking VPN status: {e}")
            return False, str(e)
