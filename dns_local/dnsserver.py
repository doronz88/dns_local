#!/usr/bin/env python
import abc
import logging
import socketserver
import struct
import traceback
from dataclasses import dataclass
from socket import socket, AF_INET, SOCK_DGRAM
from typing import List

from dnslib import SOA, NS, AAAA, A, CNAME, MX, DNSRecord, DNSHeader, QTYPE, RR

from dns_local.exceptions import DnsLocalException

logger = logging.getLogger(__name__)

DEFAULT_PORT = 53
CHUNK_SIZE = 8192


class DomainName(str):
    def __getattr__(self, item: str) -> str:
        return DomainName(item + '.' + self)


@dataclass
class DomainEntry:
    domain: DomainName
    ip: str


class BaseRequestHandler(socketserver.BaseRequestHandler):
    def _create_response(self, data: bytes) -> bytes:
        request = DNSRecord.parse(data)

        logger.debug(f'Request:\n{request}')

        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

        qname = request.q.qname
        qn = str(qname)
        qtype = request.q.qtype
        qt = QTYPE[qtype]

        for entry in self.server.domains:
            D = entry.domain
            IP = entry.ip
            TTL = 60 * 5

            soa_record = SOA(
                mname=D.nameserver,  # primary name server
                rname=D.admin_email,  # email of the domain administrator
                times=(
                    201307231,  # serial number
                    60 * 60 * 1,  # refresh
                    60 * 60 * 3,  # retry
                    60 * 60 * 24,  # expire
                    60 * 60 * 1,  # minimum
                )
            )
            ns_records = [NS(D.ns1), NS(D.ns2)]
            records = {
                D: [A(IP), AAAA((0,) * 16), MX(D.mail), soa_record] + ns_records,
                D.ns1: [A(IP)],  # MX and NS records must never point to a CNAME alias (RFC 2181 section 10.3)
                D.ns2: [A(IP)],
                D.mail: [A(IP)],
                D.andrei: [CNAME(D)],
            }

            if qn == D or qn.endswith('.' + D):
                for name, rrs in records.items():
                    if name == qn:
                        for rdata in rrs:
                            rqt = rdata.__class__.__name__
                            if qt in ['*', rqt]:
                                reply.add_answer(
                                    RR(rname=qname, rtype=getattr(QTYPE, rqt), rclass=1, ttl=TTL, rdata=rdata))

                for rdata in ns_records:
                    reply.add_ar(RR(rname=D, rtype=QTYPE.NS, rclass=1, ttl=TTL, rdata=rdata))

                reply.add_auth(RR(rname=D, rtype=QTYPE.SOA, rclass=1, ttl=TTL, rdata=soa_record))

                logger.debug(f'Reply:\n{reply}')
                return reply.pack()

        # no response
        fallback = self.server.fallback
        if fallback is not None:
            client = socket(family=AF_INET, type=SOCK_DGRAM)

            if ':' in fallback:
                hostname, port = fallback.split(':')
                port = int(port)
            else:
                hostname = fallback
                port = DEFAULT_PORT
            client.sendto(data, (hostname, port))
            return client.recvfrom(CHUNK_SIZE)[0]

        # default: reply with no answer
        return reply.pack()

    @abc.abstractmethod
    def get_data(self) -> bytes:
        pass

    @abc.abstractmethod
    def send_data(self, data: bytes) -> None:
        pass

    def handle(self) -> None:
        logger.info(f'handle client: {self.client_address}')
        # noinspection PyBroadException
        try:
            data = self.get_data()
            logger.debug(f'client message: {data}')
            self.send_data(self._create_response(data))
        except Exception:
            # catch all possible exception, so we can debug it via logging
            logger.error(traceback.format_exc())


class TCPRequestHandler(BaseRequestHandler):
    def get_data(self) -> bytes:
        data = self.request.recv(CHUNK_SIZE).strip()
        sz = struct.unpack('>H', data[:2])[0]
        if sz < len(data) - 2:
            raise DnsLocalException('Wrong size of TCP packet')
        elif sz > len(data) - 2:
            raise DnsLocalException('Too big TCP packet')
        return data[2:]

    def send_data(self, data: bytes) -> None:
        sz = struct.pack('>H', len(data))
        self.request.sendall(sz + data)


class UDPRequestHandler(BaseRequestHandler):
    def get_data(self) -> bytes:
        return self.request[0].strip()

    def send_data(self, data: bytes) -> None:
        self.request[1].sendto(data, self.client_address)


class MyThreadingServer:
    def __init__(self, domains: List[DomainEntry], fallback: str = None):
        self.allow_reuse_address = True
        self.domains = domains
        self.fallback = fallback


class MyThreadingUDPServer(socketserver.ThreadingUDPServer, MyThreadingServer):
    def __init__(self, domains: List[DomainEntry], fallback: str = None, *kwargs):
        MyThreadingServer.__init__(self, domains, fallback)
        socketserver.ThreadingUDPServer.__init__(self, *kwargs)


class MyThreadingTCPServer(socketserver.ThreadingTCPServer, MyThreadingServer):
    def __init__(self, domains: List[DomainEntry], fallback: str = None, *kwargs):
        MyThreadingServer.__init__(self, domains, fallback)
        socketserver.ThreadingTCPServer.__init__(self, *kwargs)
