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


def check_ip_validity(ip: str) -> str | None:
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
