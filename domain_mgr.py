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

import json
import re
import sys

import logger_mgr
from network_mgr import NetworkMgr

logger = logger_mgr.initialize_logger(__name__)


class DomainMgr:
    def __init__(self, provider, domain_data):
        self.provider = provider
        self.token = domain_data.get("token", None)

        # CloudFlare specific
        self.zone_id = domain_data.get("zone_id", None)
        self.dns_record_id = domain_data.get("dns_record_id", None)

        # No-ip specific
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
                self.check_duckdns_config()
                self.handle_response = self.handle_duckdns_query_response
                self.get_update_query = self.get_duckdns_update_query
            case "FREEDNS":
                self.check_freedns_config()
                self.handle_response = self.handle_freedns_query_response
                self.get_update_query = self.get_freedns_update_query
            case "NOIP":
                self.check_noip_config()
                self.handle_response = self.handle_noip_query_response
                self.get_update_query = self.get_noip_update_query
            case "CLOUDFLARE":
                self.check_cloudflare_config()
                self.handle_response = self.handle_cloudflare_query_response
                self.get_update_query = self.get_cloudflare_update_query
            case _:
                logger.error(f"Invalid provider - {provider}")
                sys.exit(1)

    #### DuckDNS ####

    def check_duckdns_config(self):
        if not self.token or not self.domains:
            logger.error("Invalid DuckDNS settings!")
            sys.exit(1)

    def handle_duckdns_query_response(self, response):
        if response["response_text"] == "OK":
            return "OK"
        elif response["response_text"] == "KO":
            return "CANCEL"

        return "CONTINUE"

    def get_duckdns_update_query(
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

            return {"query_urls": [request_url], "request_method": "GET"}

        return {}

    #### FreeDNS ####

    def check_freedns_config(self):
        if not self.token or not self.domains:
            logger.error("Invalid FreeDNS settings!")
            sys.exit(1)

    def handle_freedns_query_response(self, response):
        invalid_url = re.compile(r"^ERROR: Invalid update URL .*")
        invalid_token_domain = re.compile(r"^ERROR: Unable to locate this record .*")

        if not response["response_text"]:
            return "CONTINUE"
        elif invalid_url.match(response["response_text"]) or invalid_token_domain.match(
            response["response_text"]
        ):
            return "CANCEL"

        return "OK"

    def get_freedns_update_query(
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

            return {"query_urls": [request_urls], "request_method": "GET"}

        return {}

    #### No-IP ####

    def check_noip_config(self):
        if not self.username or not self.password or not self.domains:
            logger.error("Invalid No-IP settings!")
            sys.exit(1)

    def handle_noip_query_response(self, response):
        ok_response = re.compile(r"^good .*")
        non_change_response = re.compile(r"^nochg .*")

        if not response["response_text"]:
            return "CONTINUE"
        elif ok_response.match(response["response_text"]) or non_change_response.match(
            response["response_text"]
        ):
            return "OK"

        return "CANCEL"

    def get_noip_update_query(
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
            # NO-IP allow to update multiple domains in a single query
            request_url = f"https://{self.username}:{self.password}@dynupdate.no-ip.com/nic/update?hostname="
            request_url += ",".join(self.domains)
            request_url += "&myip="

            ip_addresses = []
            if self.update_ipv4 and new_ipv4:
                ip_addresses.append(new_ipv4)
            if self.update_ipv6 and new_ipv6:
                ip_addresses.append(new_ipv6)

            # Join the IP addresses with a comma only if both are present
            request_url += ",".join(ip_addresses)

            return {"query_urls": [request_url], "request_method": "GET"}

        return {}

    #### CloudFlare ####

    def check_cloudflare_config(self):
        if not self.token or not self.zone_id or not self.dns_record_id or not self.domains:
            logger.error("Invalid CloudFlare settings!")
            sys.exit(1)

    def handle_cloudflare_query_response(self, response):
        if not response["response_text"]:
            return "CONTINUE"
        else:
            response_dict = json.loads(response["response_text"])
            if response_dict.get("success", False):
                return "OK"

        return "CANCEL"

    def get_cloudflare_update_query(
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
            request_url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{self.dns_record_id}"

            headers = {
                'Authorization': f'Bearer {self.token}',
                "Content-Type": "application/json",
            }

            data = {
                "type": "AAAA" if self.update_ipv6 else "A",
                "name": self.domains[0],
                "content": new_ipv6 if self.update_ipv6 else new_ipv4,
            }

            return {
                "query_urls": [request_url],
                "request_method": "PATCH",
                "query_headers": headers,
                "query_data": data,
            }

        return {}
