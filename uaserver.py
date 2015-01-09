#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de SIP
"""

import socket
import SocketServer
import uaclient
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

entrada = sys.argv

CONFIG = entrada[1]

class SIPHandler(SocketServer.DatagramRequestHandler):
    """
    SIP server class
    """
    Receptor_IP = ""    
    Receptor_Puerto = ""

    def handle(self):
        lista = ['INVITE', 'ACK', 'BYE']
        IP_CLIENT = str(self.client_address[0])
        while 1:
            line = self.rfile.read()
            recibido = line.split(' ')
            print line
            if not line:
                break
            if recibido[0] == 'INVITE':
                recibido = line.split('\r\n')
                self.Receptor_IP = recibido[3].split(' ')
                self.Receptor_IP = self.Receptor_IP[1]
                self.Receptor_Puerto = recibido[6].split(' ')
                self.Receptor_Puerto = self.Receptor_Puerto[1]
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora,accion,evento)
                sentencia = 'SIP/2.0 100 Trying\r\n\r\n'
                sentencia += 'SIP/2.0 180 Ringing\r\n\r\n'
                sentencia += 'SIP/2.0 200 OK\r\n'
                sentencia += 'Content-Type: application/sdp\r\n'
                sentencia += 'v=0' + '\r\n'
                sentencia += 'o=' + ListaDatos[0][1]['username'] + ' ' + ListaDatos[1][1]['ip'] + '\r\n'
                sentencia += 's=misesion' + '\r\n'
                sentencia += 't=0' + '\r\n'
                sentencia += 'm=audio ' + ListaDatos[2][1]['puerto'] + ' RTP\r\n\r\n'
                print sentencia
                hora = time.time()
                accion = ' Send to ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = sentencia.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora,accion,evento)
                self.wfile.write(sentencia)
            elif recibido[0] == 'ACK':
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora,accion,evento)
                fichero_audio = ListaDatos[5][1]['path']
                aEjecutar = './mp32rtp -i ' + str(self.Receptor_IP) + ' -p ' + str(self.Receptor_Puerto)
                aEjecutar += ' < ' + fichero_audio
                os.system('chmod 755 mp32rtp')
                os.system(aEjecutar)
                #comando = 'cvlc rtp://@' + str(self.Receptor_IP) + ':' + str(self.Receptor_Puerto)
                #os.system(comando)
                print "Finalizado envío"
            elif recibido[0] == 'BYE':
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora,accion,evento)
                sentencia = 'SIP/2.0 200 OK\r\n\r\n'
                hora = time.time()
                accion = ' Send to ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = sentencia.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora,accion,evento)
                print sentencia
                self.wfile.write(sentencia)
            elif recibido[0] not in lista:
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora,accion,evento)
                sentencia = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                hora = time.time()
                accion = ' Send to ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = sentencia.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora,accion,evento)
                print sentencia
                self.wfile.write(sentencia)
            else:
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora,accion,evento)
                sentencia = 'SIP/2.0 400 Bad Request\r\n\r\n'
                hora = time.time()
                accion = ' Send to ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = sentencia.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora,accion,evento)
                print sentencia
                self.wfile.write(sentencia)

if __name__ == "__main__":

    if len(entrada) != 2:
        sys.exit('Usage: python uaserver.py config')

    parser = make_parser()
    Datos = uaclient.ExtraerDatos()
    parser.setContentHandler(Datos)
    parser.parse(open(CONFIG))
    ListaDatos = Datos.get_tags() 
    IP_PR = ListaDatos[3][1]['ip']
    PUERTO_PR = int(ListaDatos[3][1]['puerto'])
    serv = SocketServer.UDPServer((ListaDatos[1][1]['ip'], int(ListaDatos[1][1]['puerto'])), SIPHandler)
    print "Listening..."
    serv.serve_forever()
