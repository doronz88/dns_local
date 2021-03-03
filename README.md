# Description

`dns_local` is a simple python-based CLI to manage `dnsmasq` entries on OSX.

```
Usage: dns_local [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  cli-remove  Remove a DNS entry
  list        List current DNS entries
  set         Insert/Update a DNS entry
```

# Installation

```sh
brew install dnsmasq

git clone git@github.com:doronz88/dns_local.git
cd dns_local
python3 -m pip install -e .
```



