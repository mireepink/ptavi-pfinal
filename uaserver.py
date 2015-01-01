#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de SIP
"""

import SocketServer
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

entrada = sys.argv

CONFIG = entrada[1]

class ExtraerDatos(ContentHandler):

    def __init__(self):
        self.lista = []
        self.etiquetas = [
            'account', 'uaserver', 'rtpaudio', 'regproxy', 'log', 'audio']
        self.atributos = {
            'account': ["username", "passwd"],
            'uaserver': ["ip", "puerto"],
            'rtpaudio': ["puerto"],
            'regproxy': ["ip", "puerto"],
            'log': ["path"],
            'audio': ["path"]}

    def startElement(self, etiqueta, attrs):
        diccionario = {}
        if etiqueta in self.etiquetas:
            for atributo in self.atributos[etiqueta]:
                diccionario[atributo] = attrs.get(atributo, "")
            self.lista.append([etiqueta, diccionario])

    def get_tags(self):
        return self.lista

class SIPHandler(SocketServer.DatagramRequestHandler):
    """
    SIP server class
    """

    def handle(self):
        lista = ['INVITE', 'ACK', 'BYE']
        IP_CLIENT = str(self.client_address[0])
        while 1:
            line = self.rfile.read()
            recibido = line.split(' ')
            print recibido
            if not line:
                break
            if recibido[0] == 'INVITE':
                #Receptor_IP =
                #Receptor_Puerto =
                sentencia = 'SIP/2.0 100 Trying\r\n\r\n'
                sentencia += 'SIP/2.0 180 Ringing\r\n\r\n'
                sentencia += 'SIP/2.0 200 OK\r\n'
                sentencia += 'Content-Type: application/sdp\r\n\r\n'
                print sentencia
                self.wfile.write(sentencia)
            elif recibido[0] == 'ACK':
                aEjecutar = './mp32rtp -i ' + Receptor_IP + ' -p '
                aEjecutar += Receptor_Puerto + ' < '
                os.system('chmod 755 mp32rtp')
                os.system(aEjecutar)
                print "Finalizado envío"
            elif recibido[0] == 'BYE':
                sentencia = 'SIP/2.0 200 OK\r\n\r\n'
                print sentencia
                self.wfile.write(sentencia)
            elif recibido[0] not in lista:
                print 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                self.wfile.write('SIP/2.0 405 Method Not Allowed\r\n\r\n')
            else:
                print 'SIP/2.0 400 Bad Request\r\n\r\n'
                self.wfile.write("SIP/2.0 400 bad request\r\n\r\n")

if __name__ == "__main__":

    if len(entrada) != 2:
        sys.exit('Usage: python uaserver.py config')

    parser = make_parser()
    Datos = ExtraerDatos()
    parser.setContentHandler(Datos)
    parser.parse(open(CONFIG))
    ListaDatos = Datos.get_tags() 

    serv = SocketServer.UDPServer((ListaDatos[1][1]['ip'], int(ListaDatos[1][1]['puerto'])), SIPHandler)
    print "Listening...
    serv.serve_forever()
