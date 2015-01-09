#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


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


def log(hora, accion, evento):
    fichero = ListaDatos[4][1]['path']
    fich = open(fichero, 'a')
    fich.write(time.strftime('%Y%m%d%H%M%S', time.gmtime(float(hora))))
    fich.write(accion)
    fich.write(evento)
    fich.close()


if __name__ == "__main__":

    entrada = sys.argv

    CONFIG = entrada[1]
    METODO = entrada[2].upper()
    OPTION = entrada[3]

    if len(entrada) != 4:
        sys.exit("Usage: python uaclient.py config method option")

    parser = make_parser()
    Datos = ExtraerDatos()
    parser.setContentHandler(Datos)
    parser.parse(open(CONFIG))
    ListaDatos = Datos.get_tags()

    IP_PR = ListaDatos[3][1]['ip']
    PUERTO_PR = int(ListaDatos[3][1]['puerto'])

    try:

        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PR, PUERTO_PR))

        if METODO == 'REGISTER':
            #REGISTER sip:leonard@bigbang.org:1234 SIP/2.0
            LINE = METODO + ' sip:' + ListaDatos[0][1]['username']
            LINE += ':' + ListaDatos[1][1]['puerto'] + ' SIP/2.0' + '\r\n'
            #Expires: 3600
            LINE += 'Expires: ' + OPTION + '\r\n'
            hora = time.time()
            accion = ' Sent to ' + str(IP_PR) + ':' + str(PUERTO_PR)
            evento = LINE.replace('\r\n', ' ')
            evento = ': ' + evento + '\r\n'
            log(hora, accion, evento)

        elif METODO == 'INVITE':
            #INVITE sip:penny@girlnextdoor.com SIP/2.0
            LINE = METODO + ' sip:' + OPTION + ' SIP/2.0' + '\r\n'
            #Content-Type: application/sdp
            LINE += 'Content-Type: application/sdp\r\n\r\n'
            #v=0
            LINE += 'v=0' + '\r\n'
            #o=leonard@bigbang.org 127.0.0.1
            ip = ListaDatos[1][1]['ip']
            if ip == "" or ip == " ":
                ip = '127.0.0.1'
            LINE += 'o=' + ListaDatos[0][1]['username'] + ' ' + ip + '\r\n'
            #s=misesion
            LINE += 's=misesion' + '\r\n'
            #t=0
            LINE += 't=0' + '\r\n'
            #m=audio 34543 RTP
            LINE += 'm=audio ' + ListaDatos[2][1]['puerto'] + ' RTP'
            hora = time.time()
            accion = ' Sent to ' + str(IP_PR) + ':' + str(PUERTO_PR)
            evento = LINE.replace('\r\n', ' ')
            evento = ': ' + evento + '\r\n'
            log(hora, accion, evento)

        elif METODO == 'BYE':
            #BYE penny@girlnextdoor.com
            LINE = METODO + ' sip:' + OPTION + ' SIP/2.0'
            hora = time.time()
            accion = ' Sent to ' + str(IP_PR) + ':' + str(PUERTO_PR)
            evento = LINE.replace('\r\n', ' ')
            evento = ': ' + evento + '\r\n'
            log(hora, accion, evento)

        else:
            LINE = METODO + ' sip:' + OPTION + ' SIP/2.0'
            hora = time.time()
            accion = ' Sent to ' + str(IP_PR) + ':' + str(PUERTO_PR)
            evento = LINE.replace('\r\n', ' ')
            evento = ': ' + evento + '\r\n'
            log(hora, accion, evento)

        print "Enviando: " + LINE
        my_socket.send(LINE + '\r\n')

        data = my_socket.recv(1024)
        print 'Recibido -- ', data
        sentencia = data.split('\r\n')

        if data == 'SIP/2.0 200 OK\r\n\r\n':
            hora = time.time()
            accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
            evento = data.replace('\r\n', ' ')
            evento = ': ' + evento + '\r\n'
            log(hora, accion, evento)
        elif len(sentencia) == 14:
            Receptor_IP = sentencia[8]
            Receptor_IP = Receptor_IP.split(' ')
            Receptor_IP = Receptor_IP[1]
            Receptor_Puerto = sentencia[11]
            Receptor_Puerto = Receptor_Puerto.split(' ')
            Receptor_Puerto = Receptor_Puerto[1]
            hora = time.time()
            accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
            evento = data.replace('\r\n', ' ')
            evento = ': ' + evento + '\r\n'
            log(hora, accion, evento)
            fichero_audio = ListaDatos[5][1]['path']
            LINE = 'ACK sip:' + OPTION
            LINE += ' SIP/2.0\r\n'
            print 'Enviando: ' + LINE
            my_socket.send(LINE + '\r\n')
            hora = time.time()
            accion = ' Sent to ' + str(IP_PR) + ':' + str(PUERTO_PR)
            evento = LINE.replace('\r\n', ' ')
            evento = ': ' + evento + '\r\n'
            log(hora, accion, evento)
            aEjecutar = "./mp32rtp -i " + str(Receptor_IP) + " -p "
            aEjecutar += str(Receptor_Puerto)
            aEjecutar += " < " + fichero_audio
            os.system('chmod 755 mp32rtp')
            os.system(aEjecutar)
            hora = time.time()
            accion = ' Sent to ' + str(Receptor_IP) + ':'
            accion += str(Receptor_Puerto)
            evento = 'Envio RTP'
            evento = ': ' + evento + '\r\n'
            log(hora, accion, evento)
            data = my_socket.recv(1024)
            print 'Recibido -- ', data
        else:
            hora = time.time()
            accion = ' Error: '
            evento = data.replace('\r\n', ' ')
            evento = evento + '\r\n'
            log(hora, accion, evento)

        print "Terminando socket..."
        my_socket.close()
        print "Fin."

    except socket.error:
        print 'Error: No server listening'
        hora = time.time()
        accion = ' Error: No server listening at '
        evento = str(IP_PR) + ' port ' + str(PUERTO_PR) + '\r\n'
        log(hora, accion, evento)
