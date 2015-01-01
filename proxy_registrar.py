#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor SIP
"""

import SocketServer
import socket
import sys
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class ExtraerDatos(ContentHandler):

    def __init__(self):
        self.lista = []
        self.etiquetas = [
            'server', 'database', 'log']
        self.atributos = {
            'server': ["name", "ip", "puerto"],
            'database': ["path", "passwdpath"],
            'log': ["path"]}

    def startElement(self, etiqueta, attrs):
        diccionario = {}
        if etiqueta in self.etiquetas:
            for atributo in self.atributos[etiqueta]:
                diccionario[atributo] = attrs.get(atributo, "")
            self.lista.append([etiqueta, diccionario])

    def get_tags(self):
        return self.lista

class SIPRegisterHandler(SocketServer.DatagramRequestHandler):
    """
    Clase SIPRegisterHandler
    """
    lista = []
    diccionario = {}
    metodos = ['REGISTER', 'INVITE', 'ACK', 'BYE']

    def register2file(self):
        """
        Metodo que rellena el fichero
        """
        fich = open('registered.txt', 'w')
        fich.write("User" + "\t" + "IP" + "\t" + "Expires" + "\r\n")
        for direccion in self.diccionario.keys():
            ip = self.diccionario[direccion][0]
            puerto = self.diccionario[direccion][2]
            fich.write(direccion + '\t' + ip + '\t' + puerto + '\t')
            estructura = time.gmtime(self.diccionario[direccion][1])
            fich.write(time.strftime('%Y-%m-%d %H:%M:%S', estructura) + "\r\n")
        fich.close()

    def handle(self):
        """
        Metodo que trata la peticion REGISTER
        """
        while 1:
            line = self.rfile.read()
            if not line:
                break
            entrada = line.split(' ')
            print line
            print entrada
            if entrada[0] == 'REGISTER':
                hora = float(time.time()) + float(entrada[3])
                dir_puerto = entrada[1].split(':')
                dirsip = dir_puerto[1]
                puerto = dir_puerto[2]
                self.lista = [self.client_address[0], hora, puerto]
                self.diccionario[dirsip] = self.lista
                hora_actual = float(time.time())
                for direccion in self.diccionario.keys():
                    if self.diccionario[direccion][1] < hora_actual:
                        del self.diccionario[direccion]
                print "Enviando..." + "SIP/2.0 200 OK\r\n\r\n"
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                self.register2file()

            elif entrada[0] == 'INVITE':
                if self.diccionario.has_key(entrada[1]) == True:
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((self.diccionario[entrada[1]][1], int(self.diccionario[entrada[1]][2])))
                    my_socket.send(line)
                else:
                    print "SIP/2.0 404 User Not Found\r\n\r\n"
                    self.wfile.write("SIP/2.0 404 User Not Found\r\n\r\n")

            elif entrada[0] == 'ACK':
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((self.diccionario[entrada[1]][1], int(self.diccionario[entrada[1]][2])))
                my_socket.send(line)
        
            elif entrada[0] == 'BYE':
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((self.diccionario[entrada[1]][1], int(self.diccionario[entrada[1]][2])))
                my_socket.send(line)

            elif entrada[0] not in metodos:
                print 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                self.wfile.write('SIP/2.0 405 Method Not Allowed\r\n\r\n')
                
            else:
                print "SIP/2.0 400 Badrequest\r\n\r\n"
                self.wfile.write("SIP/2.0 400 bad request\r\n\r\n")

if __name__ == "__main__":
    """
    Procedimiento principal
    """
    Entrada = sys.argv
    CONFIG = Entrada[1]
    if len(Entrada) != 2:
        sys.exit('Usage: python proxy_registrar.py config')    

    parser = make_parser()
    Datos = ExtraerDatos()
    parser.setContentHandler(Datos)
    parser.parse(open(CONFIG))
    ListaDatos = Datos.get_tags()

    serv = SocketServer.UDPServer((ListaDatos[0][1]['ip'], int(ListaDatos[0][1]['puerto'])),  SIPRegisterHandler)

    print "Server MiServidorBigBang listening at port " + ListaDatos[0][1]['puerto'] + "..."
    serv.serve_forever()
