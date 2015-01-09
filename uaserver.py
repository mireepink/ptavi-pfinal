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


def log(hora, accion, evento):
    fichero = ListaDatos[4][1]['path']
    fich = open(fichero, 'a')
    fich.write(time.strftime('%Y%m%d%H%M%S', time.gmtime(float(hora))))
    fich.write(accion)
    fich.write(evento)
    fich.close()


class SIPHandler(SocketServer.DatagramRequestHandler):
    """
    SIP server class
    """
    Receptor = {'ip': '', 'puerto': 0}

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
                Receptor_IP = recibido[4].split(' ')
                Receptor_IP = Receptor_IP[1]
                self.Receptor['ip'] = Receptor_IP
                Receptor_Puerto = recibido[7].split(' ')
                Receptor_Puerto = Receptor_Puerto[1]
                self.Receptor['puerto'] = Receptor_Puerto
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora, accion, evento)
                sentencia = 'SIP/2.0 100 Trying\r\n\r\n'
                sentencia += 'SIP/2.0 180 Ringing\r\n\r\n'
                sentencia += 'SIP/2.0 200 OK\r\n'
                sentencia += 'Content-Type: application/sdp\r\n\r\n'
                sentencia += 'v=0' + '\r\n'
                IP = ListaDatos[1][1]['ip']
                sentencia += 'o=' + ListaDatos[0][1]['username'] + ' ' + IP
                sentencia += '\r\n' + 's=misesion' + '\r\n'
                sentencia += 't=0' + '\r\n'
                PUERTO = ListaDatos[2][1]['puerto']
                sentencia += 'm=audio ' + PUERTO + ' RTP\r\n\r\n'
                print sentencia
                hora = time.time()
                accion = ' Sent to ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = sentencia.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora, accion, evento)
                self.wfile.write(sentencia)
            elif recibido[0] == 'ACK':
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora, accion, evento)
                fichero_audio = ListaDatos[5][1]['path']
                IP = self.Receptor['ip']
                PUERTO = self.Receptor['puerto']
                aEjecutar = './mp32rtp -i ' + str(IP) + ' -p ' + str(PUERTO)
                aEjecutar += ' < ' + fichero_audio
                print aEjecutar
                os.system('chmod 755 mp32rtp')
                os.system(aEjecutar)
                hora = time.time()
                accion = ' Sent to ' + str(IP) + ':' + str(PUERTO)
                evento = 'Envio RTP'
                evento = ': ' + evento + '\r\n'
                log(hora, accion, evento)
                print "Finalizado envío"
            elif recibido[0] == 'BYE':
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora, accion, evento)
                sentencia = 'SIP/2.0 200 OK\r\n\r\n'
                hora = time.time()
                accion = ' Sent to ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = sentencia.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora, accion, evento)
                print sentencia
                self.wfile.write(sentencia)
            elif recibido[0] not in lista:
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora, accion, evento)
                sentencia = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                hora = time.time()
                accion = ' Sent to ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = sentencia.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora, accion, evento)
                print sentencia
                self.wfile.write(sentencia)
            else:
                hora = time.time()
                accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora, accion, evento)
                sentencia = 'SIP/2.0 400 Bad Request\r\n\r\n'
                hora = time.time()
                accion = ' Sent to ' + str(IP_PR) + ':' + str(PUERTO_PR)
                evento = sentencia.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                uaclient.log(hora, accion, evento)
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
    IP = ListaDatos[1][1]['ip']
    if IP == "" or IP == " ":
        IP = '127.0.0.1'
    PUERTO = ListaDatos[1][1]['puerto']
    hora = time.time()
    accion = ' Starting...\r\n'
    log(hora, accion, '')
    serv = SocketServer.UDPServer((IP, int(PUERTO)), SIPHandler)
    print "Listening..."
    serv.serve_forever()
    hora = time.time()
    accion = ' Finishing...\r\n'
    log(hora, accion, '')
