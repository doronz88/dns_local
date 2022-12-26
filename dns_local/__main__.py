import logging
import threading
from typing import List

import click
import coloredlogs

from dns_local.dnsserver import DEFAULT_PORT, DomainName, DomainEntry, MyThreadingUDPServer, MyThreadingTCPServer, \
    UDPRequestHandler, TCPRequestHandler

coloredlogs.install(level=logging.DEBUG)

logger = logging.getLogger(__name__)

DEFAULT_BIND = f'0.0.0.0:{DEFAULT_PORT}'


@click.command()
@click.option('--bind', default=DEFAULT_BIND, help='bind address')
@click.option('--tcp', is_flag=True, help='enable TCP server')
@click.option('--udp', is_flag=True, help='enable UDP server')
@click.option('--domain', multiple=True, help='domain reply (e.g. example.com:127.0.0.1)')
@click.option('--fallback', help='fallback dns server (e.g. 8.8.8.8)')
def cli(bind: str, tcp: bool, udp: bool, domain: List[str], fallback: str = None):
    """ Start a DNS implemented in Python """

    address, port = bind.split(':')
    port = int(port)

    domains = []
    for d in domain:
        name, ip = d.split(':', 1)
        if not name.endswith('.'):
            name += '.'
        domains.append(DomainEntry(domain=DomainName(name), ip=ip))

    logger.info(f'loaded domains: {domains}')

    servers = []
    if udp:
        servers.append(MyThreadingUDPServer(domains, fallback, (address, port), UDPRequestHandler))
    if tcp:
        servers.append(MyThreadingTCPServer(domains, fallback, (address, port), TCPRequestHandler))

    for s in servers:
        thread = threading.Thread(target=s.serve_forever)  # that thread will start one more thread for each request
        thread.daemon = True  # exit the server thread when the main thread terminates

        logger.info('starting dns server')
        thread.start()
        logger.info(f'{s} server loop running in thread: {thread.name}')

    input('> Hit RETURN to stop')
    for s in servers:
        s.shutdown()


if __name__ == '__main__':
    cli()
