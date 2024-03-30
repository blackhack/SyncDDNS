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


class ProviderUrl:
    def __init__(self, provider, domains):
        self.provider = provider
        self.domains = domains
        match provider:
            case "DUCKDNS":
                self.get_update_url = self.get_duckdns_update_url
            case "FREEDNS":
                self.get_update_url = self.get_freedns_update_url
            case _:
                self.get_update_url = self.get_unhandled_update_url

    def get_duckdns_update_url(
        self,
        token: str,
        domain: str,
        old_ipv4: str = None,
        new_ipv4: str = None,
        old_ipv6: str = None,
        new_ipv6: str = None,
    ):
        request_url = (
            "https://www.duckdns.org/update?domains=" + domain + "&token=" + token
        )
        need_update = False

        if new_ipv4 and old_ipv4 != new_ipv4:
            request_url += "&ip=" + new_ipv4
            need_update = True

        if new_ipv6 and old_ipv6 != new_ipv6:
            request_url += "&ipv6=" + new_ipv6
            need_update = True

        return [request_url] if need_update else [None]

    def get_freedns_update_url(
        self,
        token: str,
        domain: str,
        old_ipv4: str = None,
        new_ipv4: str = None,
        old_ipv6: str = None,
        new_ipv6: str = None,
    ):
        request_url_v4 = None
        request_url_v6 = None

        if new_ipv4 and old_ipv4 != new_ipv4:
            request_url_v4 = (
                "https://freedns.afraid.org/dynamic/update.php?"
                + token
                + "&address="
                + new_ipv4
            )

        if new_ipv6 and old_ipv6 != new_ipv6:
            request_url_v6 = (
                "https://freedns.afraid.org/dynamic/update.php?"
                + token
                + "&address="
                + new_ipv6
            )

        return [request_url_v4, request_url_v6]

    def get_unhandled_update_url(
        self,
        token: str,
        domain: str,
        old_ipv4: str = None,
        new_ipv4: str = None,
        old_ipv6: str = None,
        new_ipv6: str = None,
    ):
        return [None]
