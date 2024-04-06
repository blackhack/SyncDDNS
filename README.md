# SyncDDNS
SyncDDNS is a Python script that helps keep your dynamic DNS A (IPv4) and AAAA (IPv6) records up-to-date with the supported DDNS providers.

# Supported DDNS providers
- [DuckDNS](https://www.duckdns.org)
- [FreeDNS](https://freedns.afraid.org)
- [No-IP](https://www.noip.com)

## Setting Up the Environment

To set up the environment for SyncDDNS using Anaconda:
```
conda env create -f environment.yml
conda activate SyncDDNS
```
Or just using pip:

```
pip install requests pyyaml nslookup
```

Run it by using:
```
python sync_ddns.py
```

Tested on Python 3.11

# Config parameters

- **`update_delay`**: Defines the number of seconds to wait between each check for IP changes. If changes are detected, the script will update the domain records accordingly. It’s important to set this value in accordance with the DDNS provider’s rate limit.

- **`hide_update_queries_on_logs`**: A boolean value that determines whether update queries should be hidden in the logs. This is useful to hide tokens or other sensitive information out of the console and file logs.

- **`log_level`**: Sets the verbosity of the logs.
  - *Valid Values*:
    - `DEBUG`
    - `INFO` 

- **`dns_servers`**: Specifies the DNS servers to be used by nslookup to check the current domain's IPs.

- **`ipv4_servers:`**: List of servers that return the host's current IPv4 in plain text format, without any extra headers.

- **`ipv6_servers`**: List of servers that return the host's current IPv6 in plain text format, without any extra headers.

- **`provider`**: The DDNS service provider for the domain update.
  - *Supported Values*:
    - `DUCKDNS`
    - `FREEDNS`
    - `NOIP`

- **`token`**: A unique authentication token string provided by the DDNS service. If the DDNS provider issues a token, then the use of username and password is not necessary for authentication.

- **`username`**: The user’s account identifier used for login purposes.

- **`password`**: The secret key associated with the username for account access.

- **`domain_list`**: A list of domains to be updated.

- **`domain_data`**: The specific data for a domain. An object containing the token, IP version, and names for a particular domain.

- **`ip_version`**: Specifies the IP version for the domain. This parameter is optional.
  - *Valid Values*:
    - `ipv4`: Use this value if the domain only uses IPv4.
    - `ipv6`: Use this value if the domain only uses IPv6.
    - `both`: Use this value or omit the parameter if the domain will use both IPv4 and IPv6.

- **`names`**: An array of strings, each representing a fully qualified domain name to be updated.

## License
This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
