#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa User Agent Client para comunicación SIP
"""

from xml.sax import make_parser
import datahandler
import socket
import sys


# Protocolo y versión
PROTOCOL = "sip"
VERSION = "SIP/2.0"

# Parámetros del usuario.
if len(sys.argv) != 4:
    sys.exit("Usage: python uaclient.py config method option")
else:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2].upper()
    OPTION = sys.argv[3]

    # Parseo del fichero XML    
    parser = make_parser()
    dataHandler = datahandler.DataHandler()
    parser.setContentHandler(dataHandler)
    parser.parse(open(CONFIG))

    # Lectura del archivo de configuración UA
    attr_dicc = {}
    attr_dicc = dataHandler.get_attrs()
    for attr in attr_dicc.keys():
        if attr == 'username':
            USERNAME = attr_dicc[attr]
        elif attr == 'userpass':
            USERPASS = attr_dicc[attr]
        elif attr == 'servIp':
            UASERV_IP = attr_dicc[attr]
        elif attr == 'servPort':
            UASERV_PORT = attr_dicc[attr]
        elif attr == 'rtpPort':
            RTP_PORT = attr_dicc[attr]
        elif attr == 'proxIp':
            PROX_IP = attr_dicc[attr]
        elif attr == 'proxPort':
            PROX_PORT = attr_dicc[attr]
        elif attr == 'logPath':
            LOG_PATH = attr_dicc[attr]
        elif attr == 'audioPath':
            AUDIO_PATH = attr_dicc[attr]

    print USERNAME, USERPASS, UASERV_IP, UASERV_PORT, RTP_PORT, PROX_IP, PROX_PORT, LOG_PATH, AUDIO_PATH
