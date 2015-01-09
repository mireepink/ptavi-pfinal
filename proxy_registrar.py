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

def log(hora, accion, evento):
    fichero = ListaDatos[2][1]['path']
    fich = open(fichero, 'a')
    fich.write(str(hora))
    fich.write(accion)
    fich.write(evento)
    fich.close()

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

    def register2file(self):
        """
        Metodo que rellena el fichero
        """
        fichero = ListaDatos[1][1]['path']
        fich = open(fichero, 'w')
        fich.write("User" + "\t" + "IP" + "\t" + "Puerto" + "\t" + "Expires" + "\r\n")
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
        metodos = ['INVITE', 'ACK', 'BYE', 'SIP/2.0']
        while 1:
            line = self.rfile.read()
            if not line:
                break
            entrada = line.split(' ')
            if entrada[0] == 'REGISTER':
                hora = float(time.time()) + float(entrada[3])
                dir_puerto = entrada[1].split(':')
                dirsip = dir_puerto[1]
                puerto = dir_puerto[2]
                self.lista = [self.client_address[0], hora, puerto]
                self.diccionario[dirsip] = self.lista
                hora_actual = float(time.time())
                hora = time.time()
                accion = ' Received from ' + str(self.lista[0]) + ':' + str(self.lista[2])
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora,accion,evento)
                for direccion in self.diccionario.keys():
                    if self.diccionario[direccion][1] < hora_actual:
                        del self.diccionario[direccion]
                line = "SIP/2.0 200 OK\r\n\r\n"
                hora = time.time()
                accion = ' Send to ' + str(self.lista[0]) + ':' + str(self.lista[2])
                evento = line.replace('\r\n', ' ')
                evento = ': ' + evento + '\r\n'
                log(hora,accion,evento)
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                self.register2file()
            elif entrada[0] in metodos:
                nombre_peticion = entrada[1].split(':')
                nombre_peticion = nombre_peticion[1]
                if self.diccionario.has_key(nombre_peticion) == True:
                    IP_UAS = self.diccionario[nombre_peticion][0]
                    PUERTO_UAS = int(self.diccionario[nombre_peticion][2])
                    hora = time.time()
                    accion = ' Received from ' + str(IP_UAS) + ':' + str(PUERTO_UAS)
                    evento = line.replace('\r\n', ' ')
                    evento = ': ' + evento + '\r\n'
                    log(hora,accion,evento)
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((IP_UAS, PUERTO_UAS))    
                    my_socket.send(line)
                    hora = time.time()
                    accion = ' Send to ' + str(IP_UAS) + ':' + str(PUERTO_UAS)
                    evento = line.replace('\r\n', ' ')
                    evento = ': ' + evento + '\r\n'
                    log(hora,accion,evento)
                    data = my_socket.recv(1024)
                    hora = time.time()
                    accion = ' Received from ' + str(IP_UAS) + ':' + str(PUERTO_UAS)
                    evento = line.replace('\r\n', ' ')
                    evento = ': ' + evento + '\r\n'
                    log(hora,accion,evento)
                    self.wfile.write(data)
                else:
                    hora = time.time()
                    accion = ' Received from ' + str(IP_PR) + ':' + str(PUERTO_PR)
                    evento = line.replace('\r\n', ' ')
                    evento = ': ' + evento + '\r\n'
                    log(hora,accion,evento)
                    line = "SIP/2.0 404 User Not Found\r\n\r\n"
                    hora = time.time()
                    accion = ' Error: '
                    evento = line.replace('\r\n', ' ')
                    evento = ': ' + evento + '\r\n'
                    log(hora,accion,evento)
                    self.wfile.write("SIP/2.0 404 User Not Found\r\n\r\n")

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
    #log(fichero,hora,estructura,evento):
    serv = SocketServer.UDPServer((ListaDatos[0][1]['ip'], int(ListaDatos[0][1]['puerto'])),  SIPRegisterHandler)

    print "Server MiServidorBigBang listening at port " + ListaDatos[0][1]['puerto'] + "..."
    serv.serve_forever()
