#!/usr/bin/env python3

import subprocess
import os
from typing import List, Mapping

import click
import ifaddr

RESOLVER = '/etc/resolver'
DNSMASQ_CONF = '/usr/local/etc/dnsmasq.conf'
ADDRESS_LINE_PREFIX = 'address=/'


def get_interface_address(name: str) -> str:
    for interface in ifaddr.get_adapters():
        if interface.name == name:
            return interface.ips[0].ip


def add_localhost_as_dns_server(ip: str) -> None:
    proc = subprocess.Popen(['scutil'], stdin=subprocess.PIPE, shell=True)
    proc.stdin.writelines([b'open\n',
                           b'd.init\n',
                           f'd.add ServerAddresses * {ip}\n'.encode(),
                           b'set State:/Network/Service/PRIMARY_SERVICE_ID/DNS\n',
                           b'quit\n',
                           ])
    proc.communicate()
    proc.wait()
    assert 0 == proc.returncode, f'scutil failed: {proc.returncode}'


def restart_dnsmasq() -> None:
    proc = subprocess.Popen(['brew', 'services', 'restart', 'dnsmasq'])
    proc.communicate()
    proc.wait()
    assert 0 == proc.returncode


def get_local_dns_entries() -> List[Mapping]:
    result = {}
    with open(DNSMASQ_CONF, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith(ADDRESS_LINE_PREFIX):
                try:
                    name, ip = line.split(ADDRESS_LINE_PREFIX, 1)[1].split('/')
                except ValueError:
                    print(f'failed to parse line: {line}')
                result.update({name: ip})
    return result


def remove(name: str) -> None:
    buf = ''
    with open(DNSMASQ_CONF) as f:
        for line in f.readlines():
            if not line.startswith(ADDRESS_LINE_PREFIX + name + '/'):
                buf += line

    with open(DNSMASQ_CONF, 'w') as f:
        f.write(buf)


@click.group()
def cli():
    """
    Simple utility to manage dns entries on OSX using dnsmasq
    """
    pass


@cli.command('remove')
@click.argument('interface')
@click.argument('name')
def cli_remove(interface: str, name: str):
    """ Remove a DNS entry """
    remove(name)
    add_localhost_as_dns_server(get_interface_address(interface))
    restart_dnsmasq()


@cli.command('list')
def cli_list():
    """ List current DNS entries """
    for name, ip in get_local_dns_entries().items():
        print(name, ip)


@cli.command('restart')
@click.argument('interface')
def cli_restart(interface: str):
    """ Restart DNS service """
    add_localhost_as_dns_server(get_interface_address(interface))
    restart_dnsmasq()


@cli.command('set')
@click.argument('interface')
@click.argument('name')
@click.argument('ip')
def cli_set(interface: str, name: str, ip: str):
    """ Insert/Update a DNS entry """
    if not os.path.exists(RESOLVER):
        os.mkdir(RESOLVER)

    with open(os.path.join(RESOLVER, name), 'w') as f:
        f.write(f'nameserver {get_interface_address(interface)}\n')

    # make sure not already there
    remove(name)

    # add the new line
    with open(DNSMASQ_CONF) as f:
        buf = f.read()

    if not buf.endswith('\n'):
        buf += '\n'

    buf += f'{ADDRESS_LINE_PREFIX}{name}/{ip}\n'

    with open(DNSMASQ_CONF, 'w') as f:
        f.write(buf)

    add_localhost_as_dns_server(get_interface_address(interface))
    restart_dnsmasq()


if __name__ == '__main__':
    cli()
