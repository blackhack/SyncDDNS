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

import logging
import os
import re
import sys
import time
import yaml

import requests
from nslookup import Nslookup

from provider_url import ProviderUrl


script_dir = os.path.dirname(os.path.abspath(__file__))
logger_path = os.path.join(script_dir, "console.log")
config_path = os.path.join(script_dir, "config.yaml")


def initialize_logger():
    """Initialize and configure the logger."""
    # Create a logger object
    logger = logging.getLogger("SyncDDNS")
    logger.setLevel(logging.INFO)

    # Create handlers for writing to file and printing to console
    file_handler = logging.FileHandler(logger_path, "w")
    console_handler = logging.StreamHandler()

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = initialize_logger()


def load_config():
    """Load the configuration from the config.ini file."""

    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(
            "'config.yaml' not found. Please copy 'config.yaml.dev', "
            "rename it to 'config.yaml', and then edit it with your own settings."
        )
        sys.exit(1)

    update_delay = config["GENERAL"]["update_delay"]
    dns_servers = config["GENERAL"]["dns_servers"]
    ipv4_servers = config["GENERAL"]["ipv4_servers"]
    ipv6_servers = config["GENERAL"]["ipv6_servers"]

    domains_dict = {}

    for domains_list in config["DOMAINS_LIST"]:
        for domains in domains_list["domains"]:
            domains_dict[domains["token"]] = ProviderUrl(
                domains_list["provider"], domains["details"]
            )

    # Return the settings as a dictionary
    return {
        "update_delay": update_delay,
        "dns_servers": dns_servers,
        "ipv4_servers": ipv4_servers,
        "ipv6_servers": ipv6_servers,
        "domains_dict": domains_dict,
    }


config_settings = load_config()


def get_current_IP(ipv6: bool = False):
    """Try to return the current host's ip."""

    request_result = None
    getters_url = (
        config_settings["ipv6_servers"] if ipv6 else config_settings["ipv4_servers"]
    )

    for url in getters_url:
        try:
            request_result = requests.get(url, timeout=5)
            if request_result.status_code == 200:
                return request_result.text.rstrip()
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Can't get current {'IPv6' if ipv6 else 'IPv4'} using the server {url}, check the status of the server or your internet connection!"
            )

    if request_result is None or request_result.status_code != 200:
        logger.warning(
            f"Not valid results from get_current_IP({'IPv6' if ipv6 else 'IPv4'}), check if {'IPV6' if ipv6 else 'IPV4'}_GETTER servers are working as intended."
        )

        return None


def get_current_dns_IPs(domain: str, ipv4: bool = True, ipv6: bool = True):
    """Try to return the current domain A and AAAA records."""
    dns_query = Nslookup(dns_servers=config_settings["dns_servers"])
    ipv4_result = None
    ipv6_result = None

    if ipv4:
        try:
            ipv4_result = dns_query.dns_lookup(domain).answer

            if len(ipv4_result) == 0:
                ipv4_result = None
                logger.warning(f"Obtained no A record for domain: {domain}")
            else:
                ipv4_result = ipv4_result[0]
        except Exception as e:
            ipv4_result = None
            logger.error(
                f"An error occurred while requesting domain A record: {domain}"
            )

    if ipv6:
        try:
            ipv6_result = dns_query.dns_lookup6(domain).answer

            if len(ipv6_result) == 0:
                ipv6_result = None
                logger.warning(f"Obtained no AAAA record for domain: {domain}")
            else:
                ipv6_result = ipv6_result[0]
        except Exception as e:
            ipv6_result = None
            logger.error(
                f"An error occurred while requesting domain AAAA record: {domain}"
            )

    return {
        "ipv4": ipv4_result,
        "ipv6": ipv6_result,
    }


def CheckIPValidity(ip):
    if not ip or not isinstance(ip, str):
        return None

    ipv4_pattern = re.compile(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )
    ipv6_pattern = re.compile(
        r"^((?:[0-9A-Fa-f]{1,4}:){7}(?:[0-9A-Fa-f]{1,4}|:)|(?:[0-9A-Fa-f]{1,4}:){6}(?::[0-9A-Fa-f]{1,4}|(?:[0-9A-Fa-f]{1,4}:)?:(?:[0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4}|:)|(?:[0-9A-Fa-f]{1,4}:){5}(?:(?::[0-9A-Fa-f]{1,4}){1,2}|:(?:[0-9A-Fa-f]{1,4}:){1,2}:[0-9A-Fa-f]{1,4}|:)|(?:[0-9A-Fa-f]{1,4}:){4}(?:(?::[0-9A-Fa-f]{1,4}){1,3}|:(?:[0-9A-Fa-f]{1,4}:){1,3}:[0-9A-Fa-f]{1,4}|:)|(?:[0-9A-Fa-f]{1,4}:){3}(?:(?::[0-9A-Fa-f]{1,4}){1,4}|:(?:[0-9A-Fa-f]{1,4}:){1,4}:[0-9A-Fa-f]{1,4}|:)|(?:[0-9A-Fa-f]{1,4}:){2}(?:(?::[0-9A-Fa-f]{1,4}){1,5}|:(?:[0-9A-Fa-f]{1,4}:){1,5}:[0-9A-Fa-f]{1,4}|:)|(?:[0-9A-Fa-f]{1,4}:){1}(?:(?::[0-9A-Fa-f]{1,4}){1,6}|:(?:[0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4}|:)|(?::((?::[0-9A-Fa-f]{1,4}){1,7}|:)))(?:%[0-9a-zA-Z]{1,})?$"
    )

    if ipv4_pattern.match(ip):
        return ip
    elif ipv6_pattern.match(ip):
        return ip
    else:
        return None


while True:
    logger.info("Starting IPs checking loop...")

    current_ipv4 = CheckIPValidity(get_current_IP())
    current_ipv6 = CheckIPValidity(get_current_IP(ipv6=True))

    for token, domains_mgr in config_settings["domains_dict"].items():
        for domain in domains_mgr.domains:
            ipv4 = False if "ipv6_only" in domain else True
            ipv6 = False if "ipv4_only" in domain else True

            ip_type = "IPv4 and IPv6" if ipv4 and ipv6 else ("IPv4" if ipv4 else "IPv6")
            logger.info(
                f"Checking {ip_type} changes for {domains_mgr.provider} domain: {domain['name']}"
            )
            old_ips = get_current_dns_IPs(domain["name"], ipv4, ipv6)

            request_urls = domains_mgr.get_update_url(
                token,
                domain["name"],
                CheckIPValidity(old_ips["ipv4"]),
                current_ipv4 if ipv4 else None,
                CheckIPValidity(old_ips["ipv6"]),
                current_ipv6 if ipv6 else None,
            )

            if all(element is None for element in request_urls):
                logger.info(f"Skipping all updates for domain: {domain['name']}")
            else:
                for url in request_urls:
                    if url:
                        logger.info(f"Requesting update: {url}")
                        try:
                            result_update = requests.get(url, timeout=5)
                            logger.info(f"Server response: {result_update}")
                        except requests.exceptions.RequestException as e:
                            logger.error(
                                "Result: Error while requesting IP update, retrying in the next loop."
                            )
                            logger.error(e.strerror)

    logger.info(f"Sleeping for {config_settings['update_delay']} seconds")
    time.sleep(config_settings["update_delay"])
