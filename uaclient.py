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
    formatTime = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    logFile = open(LOG_FILE, 'a')
    logFile.write(formatTime + ' ' + event + '\n')
    logFile.close()

def send_receive(request, servIP, servPort):
    """
    Método para enviar solicitur a un servidor y recibir respuesta del mismo
    """
    # Creamos el socket, lo configuramos y lo atamos al servidor/puerto registrar
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((servIP, servPort))

    # Enviamos solicitud
    formatTime = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    my_socket.send(request)
    print "Send to " + str(servIP) + ':' + str(servPort) + ':\n' + request
    reqstLine = request.replace("\r\n", " ")
    event = "Send to " + str(servIP) + ':' + str(servPort) + ': ' + reqstLine
    log2file(event)

    # Recibimos respuesta
    try:
        response = my_socket.recv(1024)
    except socket.error:
        print (formatTime + " Error: No server listening at " + servIP \
               + " port " + str(servPort))
        raise SystemExit
    print "Received from " + str(servIP) + ':' + str(servPort) + ':\n' \
          + response
    respLine = response.replace("\r\n", " ")
    event = "Received from " + str(servIP) + ':' + str(servPort) + ': ' \
          + respLine
    log2file(event)

    # Finalizamos programa                                                          # ??????
    print "Terminando socket..."
    my_socket.close()
    print "Fin."

#-----------------------------Programa principal-------------------------------
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
MY_USERNAME = attr_dicc['userName']
MY_USERPASS = attr_dicc['userPass']
UASERV_IP = attr_dicc['servIp']
UASERV_PORT = int(attr_dicc['servPort'])
RTP_PORT = int(attr_dicc['rtpPort'])
PROX_IP = attr_dicc['proxIp']
PROX_PORT = int(attr_dicc['proxPort'])
LOG_FILE = attr_dicc['logPath']
AUDIO_FILE = attr_dicc['audioPath']

# Comenzando el programa...
log2file('Starting...')

#-----------------------------------Registro-----------------------------------
if METHOD == 'REGISTER':

    # Enviamos solicitud y recibimos respuesta
    request = METHOD + ' ' + 'sip:' + MY_USERNAME + '@dominio.net ' + VERSION \
            + '\r\n' + 'Expires: ' + OPTION + '\r\n\r\n'
    send_receive(request, PROX_IP, PROX_PORT)
