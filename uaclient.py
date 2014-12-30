#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa User Agent Client para comunicación SIP
"""

from xml.sax import make_parser
import datahandler
import socket
import sys
import time


#--------------------------------- Métodos ------------------------------------
def log2file(event):
    """
    Método para imprimir mensajes de log en un fichero de texto
    """
    logFile = open(LOG_FILE, 'a')
    logFile.write('...\n')

    formatTime = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    logFile.write(formatTime + ' ' + event + '\n')
    logFile.close()

#-----------------------------Programa principal-------------------------------
# Protocolo y versión
PROTOCOL = "sip"
VERSION = "SIP/2.0"

# Parámetros del usuario
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
attr_dicc = dataHandler.get_attrs()
USER_NAME = attr_dicc['userName']
USER_PASS = attr_dicc['userPass']
UASERV_IP = attr_dicc['servIp']
UASERV_PORT = attr_dicc['servPort']
RTP_PORT = attr_dicc['rtpPort']
PROX_IP = attr_dicc['proxIp']
PROX_PORT = attr_dicc['proxPort']
LOG_FILE = attr_dicc['logPath']
AUDIO_FILE = attr_dicc['audioPath']

# Comenzando el programa...
log2file('Starting...')
