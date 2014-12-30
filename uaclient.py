#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

entrada = sys.argv

CONFIG = entrada[1]
METODO = entrada[2].upper()
OPTION = entrada[3]

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

if __name__ == "__main__":

    if len(entrada) != 4:
        sys.exit("Usage: python uaclient.py config method option")    

    try:

        parser = make_parser()
        Datos = ExtraerDatos()
        parser.setContentHandler(Datos)
        parser.parse(open(CONFIG))
        ListaDatos = Datos.get_tags()    

        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((ListaDatos[3][1]['ip'], int(ListaDatos[3][1]['puerto'])))
        if METODO == 'REGISTER':
            #REGISTER sip:leonard@bigbang.org:1234 SIP/2.0
            LINE = METODO + ' sip:' + ListaDatos[0][1]['username']
            LINE += ':' + ListaDatos[1][1]['puerto'] + ' SIP/2.0' + '\r\n'    
            #Expires: 3600
            LINE += 'Expires: ' + OPTION + '\r\n'

            print "Enviando: " + LINE
            my_socket.send(LINE + '\r\n')

        elif METODO == 'INVITE':
            #INVITE sip:penny@girlnextdoor.com SIP/2.0
            LINE = METODO + ' sip:' + OPTION + ' SIP/2.0' + '\r\n'
            #Content-Type: application/sdp
            LINE += 'Content-Type: application/sdp' + '\r\n'
            #v=0
            LINE += 'v=0' + '\r\n'
            #o=leonard@bigbang.org 127.0.0.1
            LINE += 'o=' + ListaDatos[0][1]['username'] + ' ' + ListaDatos[1][1]['ip'] + '\r\n'
            #s=misesion
            LINE += 's=misesion' + '\r\n'
            #t=0
            LINE += 't=0' + '\r\n'
            #m=audio 34543 RTP
            LINE += 'm=audio' + ListaDatos[2][1]['puerto'] + ' RTP'

            print "Enviando: " + LINE
            my_socket.send(LINE + '\r\n')

        elif METODO == 'BYE':
            #BYE penny@girlnextdoor.com
            LINE = METODO + ' sip:' + OPTION + ' SIP/2.0'

            print "Enviando: " + LINE
            my_socket.send(LINE + '\r\n')

        data = my_socket.recv(1024)
        print 'Recibido -- ', data
        sentencia = 'SIP/2.0 100 Trying\r\n\r\n'
        sentencia += 'SIP/2.0 180 Ringing\r\n\r\n'
        sentencia += 'SIP/2.0 200 OK\r\n\r\n'

        if data == sentencia:
            LINE = 'ACK' + ' sip:' + OPTION
            LINE += ' SIP/2.0' + '\r\n'
            print 'Enviando: ' + LINE
            my_socket.send(LINE + '\r\n')
            data = my_socket.recv(1024)
            print 'Recibido -- ', data

        print "Terminando socket..."

        my_socket.close()
        print "Fin."

    except socket.error:
        PORT = str(PORT_SERVER)
        #añadir al log "fecha Error: No server listening at ' + IP_SERVER + ' port ' + PORT
