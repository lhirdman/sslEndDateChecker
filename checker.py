#!/usr/bin/env python

import sys
import ssl
from datetime import datetime
import pytz
import OpenSSL
import socket
from netaddr import *

def get_enddate( hostip ):
    color = {
            False: "\033[31;1m",
            True: "\033[32;1m",
            'end': "\033[0m",
            'error': "\033[33;1m",
            }
    ctx = OpenSSL.SSL.Context(ssl.PROTOCOL_TLSv1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    x509 = None

    try:
        s.connect((hostip, 443))
        cnx = OpenSSL.SSL.Connection(ctx, s)
        cnx.set_tlsext_host_name(hostip)
        cnx.set_connect_state()
        cnx.do_handshake()

        x509 = cnx.get_peer_certificate()
        s.close()
    except Exception as e:
        print "%30s: %s%s%s" % (hostip, color['error'], e, color['end'])

    issuer = x509.get_issuer()
    issuer_corp = x509.get_issuer().organizationName
    issuer_url = x509.get_issuer().organizationalUnitName
    issuer_x509 = x509.get_issuer().commonName
    server_name = x509.get_subject().commonName

    now = datetime.now(pytz.utc)
    begin = datetime.strptime(x509.get_notBefore(), "%Y%m%d%H%M%SZ").replace(tzinfo=pytz.UTC)
    begin_ok = begin < now
    end = datetime.strptime(x509.get_notAfter(), "%Y%m%d%H%M%SZ").replace(tzinfo=pytz.UTC)
    end_ok = end > now

    print "%30s: begin=%s%s%s end=%s%s%s issuer=%s" % (hostip,
            color[begin_ok], begin.strftime("%d.%m.%Y"), color['end'],
            color[end_ok], end.strftime("%d.%m.%Y"), color['end'],
            issuer_corp)

def test_conn( ip ):
    try:
        socket.gethostbyaddr(ip)
    except socket.herror:
        print "Connection failed:" + ip
        return False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((ip,443))
    except socket.timeout:
        print "Host up, port 443 not available for:" + ip
        return False
    print "Connection successful:" + ip
    return True


for ip in IPNetwork('194.132.85.0/24'):
    if test_conn( str(ip) ):
        get_enddate( str(ip) )