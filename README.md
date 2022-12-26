[![Python application](https://github.com/doronz88/dns_local/workflows/Python%20application/badge.svg)](https://github.com/doronz88/dns_local/actions/workflows/python-app.yml "Python application action")
[![Pypi version](https://img.shields.io/pypi/v/dns_local.svg)](https://pypi.org/project/dns_local/ "PyPi package")

# Description

Simple python3 DNS server

# Installation

```shell
python3 -m pip install dns_local
```

Or directly from sources:

```shell
git clone git@github.com:doronz88/dns_local.git
cd dns_local
python3 -m pip install -e .
```

# Usage

```
Usage: python -m dns_local [OPTIONS]

  Start a DNS implemented in Python

Options:
  --bind TEXT      bind address
  --tcp            enable TCP server
  --udp            enable UDP server
  --domain TEXT    domain reply (e.g. example.com:127.0.0.1)
  --fallback TEXT  fallback dns server (e.g. 8.8.8.8)
  --help           Show this message and exit.
```

For example, consider the following usage:

```shell
python3 -m dns_local --bind 192.168.2.1:53 --udp --fallback 8.8.8.8 --domain kaki:192.168.2.1 --domain kaki2:192.168.2.1
```

This will start a `udp` DNS server listening at `192.168.2.1:53` with the two entries:

- `kaki1` -> `192.168.2.1`
- `kaki2` -> `192.168.2.1`

And use Google's DNS server (`8.8.8.8`) as a fallback for any entry not in given domain list.

