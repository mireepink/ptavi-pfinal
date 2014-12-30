#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un User Agent Server en SIP
"""

from xml.sax import make_parser
import datahandler
import SocketServer
import sys
import os
import time


#--------------------------------- Clase --------------------------------------
class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        """
        Método para recibir en el manejador y establecer comunicación SIP
        """
        # Escribe dirección y puerto del cliente (de tupla client_address)
        client_ip = str(self.client_address[0])
        client_port = str(self.client_address[1])
        print "IP cliente: " + client_ip + "| Puerto cliente: " + client_port

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break
            else:
                # Evaluación de los parámetros que nos envía el cliente
                print "Recibido:\n" + line

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
if __name__ == "__main__":

    # Versión del protocolo SIP
    MY_VERSION = "SIP/2.0"

    # Evaluación de parámetros de la línea de comandos
    if len(sys.argv) != 2:
        sys.exit("Usage: python uaserver.py config")
    else:
        CONFIG = sys.argv[1]

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
