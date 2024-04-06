#    Copyright 2024 JDavid(Blackhack) <davidaristi.0504@gmail.com>

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import re
import requests

import logger_mgr
from nslookup import Nslookup

logger = logger_mgr.initialize_logger(__name__)


class NetworkMgr:
    _instance = None
    dns_servers = []
    ipv4_servers = []
    ipv6_servers = []

    def __new__(cls, dns_servers=None, ipv4_servers=None, ipv6_servers=None):
        if cls._instance is None:
            if dns_servers is None or ipv4_servers is None or ipv6_servers is None:
                raise ValueError(
                    "dns_servers, ipv4_servers, and ipv6_servers must be provided on the first instantiation."
                )

            cls._instance = super(NetworkMgr, cls).__new__(cls)
            cls.dns_servers = dns_servers
            cls.ipv4_servers = ipv4_servers
            cls.ipv6_servers = ipv6_servers

        return cls._instance

    def get_current_IP(self, ipv6: bool = False):
        """Try to return the current host's ip."""

        request_result = None
        getters_url = self.ipv6_servers if ipv6 else self.ipv4_servers

        for url in getters_url:
            try:
                request_result = requests.get(url, timeout=5)
                if request_result.status_code == 200:
                    ip_result = self.check_ip_validity(request_result.text.rstrip())
                    if not ip_result:
                        logger.error(
                            f"Server {url} responded, but it wasn't a valid IP address!"
                        )
                        logger.debug(f"Response: {request_result.text.rstrip()}")
                    else:
                        return ip_result
            except requests.exceptions.RequestException as error:
                logger.error(
                    f"Can't get current {'IPv6' if ipv6 else 'IPv4'} using the server {url}, "
                    f"check the status of the server or your internet connection"
                )
                logger.debug(f"Error: {error}")

        if request_result is None or request_result.status_code != 200:
            logger.warning(
                f"Not valid results from get_current_IP({'IPv6' if ipv6 else 'IPv4'}), "
                f"check if {'IPV6' if ipv6 else 'IPV4'}_GETTER servers are working as intended."
            )

            return None

    def get_current_dns_IPs(self, domain: str, ipv6: bool = False):
        """Try to return the current domain's A or AAAA record."""
        dns_query = Nslookup(dns_servers=self.dns_servers)
        ip_result = None

        try:
            ip_result = (
                dns_query.dns_lookup6(domain).answer
                if ipv6
                else dns_query.dns_lookup(domain).answer
            )

            ip_result = (
                self.check_ip_validity(ip_result[0]) if len(ip_result) > 0 else None
            )

            if not ip_result:
                logger.warning(f"Obtained no A record for domain: {domain}")
        except Exception as error:
            ip_result = None
            logger.error(
                f"An error occurred while requesting domain A record: {domain}"
            )
            logger.debug(f"Error: {error}")

        return ip_result

    def request_ip_update(self, url_query: str):
        try:
            response = requests.get(url_query, timeout=5)
            logger.debug(f"request_ip_update - Server response: {response.text}")
        except requests.exceptions.RequestException as error:
            response = None
            logger.error(f"request_ip_update - Error while requesting IP update")
            logger.debug(f"Error: {error}")

        if response and response.status_code == 200:
            return True

        return False

    def check_ip_validity(self, ip: str) -> str | None:
        """
        Check the validity of an IP address.

        Validates whether the input is a well-formed IP address string.
        If the IP address is valid, returns the same IP address string.
        If the IP address is invalid or not a string, returns None.

        Parameters:
        ip (str): The IP address string to validate.

        Returns:
        str | None: The original IP address string if valid, None otherwise.
        """

        if not ip or not isinstance(ip, str):
            return None

        ipv4_pattern = re.compile(
            r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )

        ipv6_pattern = re.compile(
            r"^((?:[0-9A-Fa-f]{1,4}:){7}(?:[0-9A-Fa-f]{1,4}|:)|"
            r"(?:[0-9A-Fa-f]{1,4}:){6}(?::[0-9A-Fa-f]{1,4}|"
            r"(?:[0-9A-Fa-f]{1,4}:)?:(?:[0-9A-Fa-f]{1,4}:)?"
            r"[0-9A-Fa-f]{1,4}|:)|"
            r"(?:[0-9A-Fa-f]{1,4}:){5}(?:(?::[0-9A-Fa-f]{1,4}){1,2}|:"
            r"(?:[0-9A-Fa-f]{1,4}:){1,2}:[0-9A-Fa-f]{1,4}|:)|"
            r"(?:[0-9A-Fa-f]{1,4}:){4}(?:(?::[0-9A-Fa-f]{1,4}){1,3}|:"
            r"(?:[0-9A-Fa-f]{1,4}:){1,3}:[0-9A-Fa-f]{1,4}|:)|"
            r"(?:[0-9A-Fa-f]{1,4}:){3}(?:(?::[0-9A-Fa-f]{1,4}){1,4}|:"
            r"(?:[0-9A-Fa-f]{1,4}:){1,4}:[0-9A-Fa-f]{1,4}|:)|"
            r"(?:[0-9A-Fa-f]{1,4}:){2}(?:(?::[0-9A-Fa-f]{1,4}){1,5}|:"
            r"(?:[0-9A-Fa-f]{1,4}:){1,5}:[0-9A-Fa-f]{1,4}|:)|"
            r"(?:[0-9A-Fa-f]{1,4}:){1}(?:(?::[0-9A-Fa-f]{1,4}){1,6}|:"
            r"(?:[0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4}|:)|"
            r"(?::((?::[0-9A-Fa-f]{1,4}){1,7}|:))"
            r")(?:%[0-9a-zA-Z]{1,})?$"
        )

        if ipv4_pattern.match(ip) or ipv6_pattern.match(ip):
            return ip

        return None
