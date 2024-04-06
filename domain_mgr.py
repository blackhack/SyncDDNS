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

import logger_mgr
from network_mgr import NetworkMgr

logger = logger_mgr.initialize_logger(__name__)


class DomainMgr:
    def __init__(self, provider, domain_data):
        self.provider = provider
        self.token = domain_data.get("token", None)
        self.username = domain_data.get("username", None)
        self.password = domain_data.get("password", None)
        self.update_ipv4 = (
            False if domain_data.get("ip_version", "both") == "ipv6" else True
        )
        self.update_ipv6 = (
            False if domain_data.get("ip_version", "both") == "ipv4" else True
        )
        self.domains = domain_data.get("names", [])

        match provider:
            case "DUCKDNS":
                self.get_update_url = self.get_duckdns_update_url
            case "FREEDNS":
                self.get_update_url = self.get_freedns_update_url
            case _:
                self.get_update_url = self.get_unhandled_update_url

    def get_duckdns_update_url(
        self,
        new_ipv4: str = None,
        new_ipv6: str = None,
    ):
        # Check if any domain need to be update, both ipv4 and ipv6 if available
        need_update = False
        if self.update_ipv4 and new_ipv4:
            need_update = any(
                NetworkMgr().get_current_dns_IPs(domain) != new_ipv4
                for domain in self.domains
            )
        if not need_update and self.update_ipv6 and new_ipv6:
            need_update = any(
                NetworkMgr().get_current_dns_IPs(domain, ipv6=True) != new_ipv6
                for domain in self.domains
            )

        if need_update:
            # DuckDNS allow to update multiple domains in a single query
            request_url = (
                "https://www.duckdns.org/update?token=" + self.token + "&domains="
            )
            request_url += ",".join(self.domains)

            if self.update_ipv4 and new_ipv4:
                request_url += "&ip=" + new_ipv4
            if self.update_ipv6 and new_ipv6:
                request_url += "&ipv6=" + new_ipv6

            return [request_url]

        return []

    def get_freedns_update_url(
        self,
        new_ipv4: str = None,
        new_ipv6: str = None,
    ):
        # Check if any domain need to be update, both ipv4 and ipv6 if available
        need_update = False
        if self.update_ipv4 and new_ipv4:
            need_update = any(
                NetworkMgr().get_current_dns_IPs(domain) != new_ipv4
                for domain in self.domains
            )
        if not need_update and self.update_ipv6 and new_ipv6:
            need_update = any(
                NetworkMgr().get_current_dns_IPs(domain, ipv6=True) != new_ipv6
                for domain in self.domains
            )

        if need_update:
            # FreeDNS need one query per IP type
            request_urls = []

            if self.update_ipv4 and new_ipv4:
                request_urls.append(
                    "https://freedns.afraid.org/dynamic/update.php?"
                    + self.token
                    + "&address="
                    + new_ipv4
                )

            if self.update_ipv6 and new_ipv6:
                request_urls.append(
                    "https://freedns.afraid.org/dynamic/update.php?"
                    + self.token
                    + "&address="
                    + new_ipv6
                )

            return request_urls

        return []

    def get_unhandled_update_url(
        self,
        new_ipv4: str = None,
        new_ipv6: str = None,
    ):
        return []
