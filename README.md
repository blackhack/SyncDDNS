# SyncDDNS
SyncDDNS is a Python script that helps keep your dynamic DNS A (IPv4) and AAAA (IPv6) records up-to-date with the supported DDNS providers.

# Supported DDNS providers
- DuckDNS
- FreeDNS

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

Run just by using:
```
python sync_ddns.py
```

Tested on Python 3.11

## License
This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
