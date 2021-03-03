#!/usr/bin/env python3

import subprocess
import os

import click

RESOLVER = '/etc/resolver'
DNSMASQ_CONF = '/usr/local/etc/dnsmasq.conf'
ADDRESS_LINE_PREFIX = 'address=/'


@click.group()
def cli():
    """
    Simple utility to manage dns entries on OSX using dnsmasq
    """
    pass


def add_localhost_as_dns_server():
    proc = subprocess.Popen(['scutil'], stdin=subprocess.PIPE, shell=True)
    proc.stdin.writelines([b'open\n',
                           b'd.init\n',
                           b'd.add ServerAddresses * 127.0.0.1\n',
                           b'set State:/Network/Service/PRIMARY_SERVICE_ID/DNS\n',
                           b'quit\n',
                           ])
    proc.communicate()
    proc.wait()
    assert 0 == proc.returncode, f'scutil failed: {proc.returncode}'


def restart_dnsmasq():
    proc = subprocess.Popen(['brew', 'services', 'restart', 'dnsmasq'])
    proc.communicate()
    proc.wait()
    assert 0 == proc.returncode


def get_local_dns_entries():
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


def remove(name):
    buf = ''
    with open(DNSMASQ_CONF) as f:
        for line in f.readlines():
            if not line.startswith(ADDRESS_LINE_PREFIX + name + '/'):
                buf += line

    with open(DNSMASQ_CONF, 'w') as f:
        f.write(buf)


@cli.command()
@click.argument('name')
def cli_remove(name):
    """ Remove a DNS entry """
    remove(name)
    add_localhost_as_dns_server()
    restart_dnsmasq()


@cli.command('list')
def cli_list():
    """ List current DNS entries """
    for name, ip in get_local_dns_entries().items():
        print(name, ip)


@cli.command('set')
@click.argument('name')
@click.argument('ip')
def cli_set(name, ip):
    """ Insert/Update a DNS entry """
    if not os.path.exists(RESOLVER):
        os.mkdir(RESOLVER)

    with open(os.path.join(RESOLVER, name), 'w') as f:
        f.write('nameserver 127.0.0.1\n')

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

    add_localhost_as_dns_server()
    restart_dnsmasq()


def main():
    click.CommandCollection(sources=[cli])()


if __name__ == '__main__':
    main()
