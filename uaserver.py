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
