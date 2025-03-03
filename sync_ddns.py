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

import os
import sys
import time

import yaml

import logger_mgr
from domain_mgr import DomainMgr
from network_mgr import NetworkMgr

logger = logger_mgr.initialize_logger("sync_ddns")

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.yaml")
config_settings = None


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
    hide_update_queries_on_logs = config["GENERAL"]["hide_update_queries_on_logs"]
    continue_on_provider_fail = config["GENERAL"]["continue_on_provider_fail"]
    logger_mgr.set_log_level(config["GENERAL"]["log_level"])
    dns_servers = config["GENERAL"]["dns_servers"]
    ipv4_servers = config["GENERAL"]["ipv4_servers"]
    ipv6_servers = config["GENERAL"]["ipv6_servers"]

    NetworkMgr(dns_servers, ipv4_servers, ipv6_servers)

    domain_handlers = []

    for domains_info in config["DOMAIN_INFO"]:
        for domain_list in domains_info["domain_list"]:
            provider = domains_info["provider"]
            domain_data = domain_list["domain_data"]

            domain_handlers.append(DomainMgr(provider, domain_data))

    # Set the settings as a dictionary
    global config_settings
    config_settings = {
        "update_delay": update_delay,
        "hide_update_queries_on_logs": hide_update_queries_on_logs,
        "continue_on_provider_fail": continue_on_provider_fail,
        "dns_servers": dns_servers,
        "ipv4_servers": ipv4_servers,
        "ipv6_servers": ipv6_servers,
        "domain_handlers": domain_handlers,
    }


def run_ip_check_cycle():
    current_ipv4 = NetworkMgr().get_current_IP()
    current_ipv6 = NetworkMgr().get_current_IP(ipv6=True)

    for domain_handler in config_settings["domain_handlers"][:]:
        ip_type = (
            "IPv4 and IPv6"
            if domain_handler.update_ipv4 and domain_handler.update_ipv6
            else ("IPv4" if domain_handler.update_ipv4 else "IPv6")
        )
        logger.info(
            f"Checking {ip_type} changes for {domain_handler.provider} - {domain_handler.domains}"
        )

        request_queries = domain_handler.get_update_query(current_ipv4, current_ipv6)
        if not request_queries:
            logger.info("... No updates were performed.")

        for query in request_queries.get("query_urls", []):
            logger.info(
                f"... An update will be performed with the following URL query:"
            )
            logger.info(
                f"...... {'HIDE' if config_settings['hide_update_queries_on_logs'] else query}"
            )

            method = request_queries.get("request_method", None)
            headers = request_queries.get("query_headers", None)
            data = request_queries.get("query_data", None)

            query_response = domain_handler.handle_response(
                NetworkMgr().request_ip_update(query, method, headers, data)
            )

            match query_response:
                case "OK":
                    logger.info("Update request accepted successfully!")
                case "CONTINUE":
                    logger.info("Update request failed, trying on next loop...")
                case "CANCEL":
                    if config_settings["continue_on_provider_fail"]:
                        logger.warning(
                            "Update request rejected by provider. Check your authentication credentials and domain names. "
                            "Due to 'continue_on_provider_fail', the domain will attempt updates in the next loop. "
                            "If not fixed, this can trigger a ban or rate-limit."
                        )
                    else:
                        logger.error(
                            "Update request rejected by provider. Check your authentication credentials and domain names. "
                            "The update process for these domains is halted to prevent bans or rate-limits."
                        )
                        config_settings["domain_handlers"].remove(domain_handler)
                    break




def main():
    load_config()

    try:
        while True:
            logger.info("Starting IPs checking cycle...")
            run_ip_check_cycle()
            logger.info(f"Sleeping for {config_settings['update_delay']} seconds")
            time.sleep(config_settings["update_delay"])
    except KeyboardInterrupt:
        logger.info("Program terminated by user.")
    except Exception as e:
        logger.exception(f"A fatal error occurred: {e}")


if __name__ == "__main__":
    main()
