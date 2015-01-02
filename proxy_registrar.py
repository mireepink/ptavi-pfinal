#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import SocketServer
import sys
import os
import time

# Variables globales
users = {}
LOG_FILE = ""


#-------------------------------- Clases --------------------------------------
class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        """
        Método para recibir en el manejador y establecer comunicación SIP
        """
        # IP y puerto del cliente (de tupla client_address)
        self.clientIP = str(self.client_address[0])
        self.clientPort = str(self.client_address[1])

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            request = self.rfile.read()

            # Si no hay más líneas salimos del bucle infinito
            if not request:
                break
            else:
                # Evaluación de los parámetros que nos envía el cliente
                log_debug('receive', self.clientIP, self.clientPort, request)
                try:
                    parameters = request.split()
                    self.method = parameters[0]
                    protocol = parameters[1].split(':')[0]
                    self.address = parameters[1].split(':')[1]
                    login = self.address.split('@')[0]
                    server_ip = self.address.split('@')[1]
                    client_version = parameters[2]
                    self.option = parameters[4]

                # Envío de "Bad Request"
                    if protocol != 'sip' or client_version != 'SIP/1.0'\
                        and client_version != 'SIP/2.0':
                        response = MY_VERSION + " 400 Bad Request\r\n\r\n"
                        self.wfile.write(response)
                        log_debug('send', self.clientIP, self.clientPort, response)
                        break
                except:
                    response = MY_VERSION + " 400 Bad Request\r\n\r\n"
                    self.wfile.write(response)
                    log_debug('send', self.clientIP, self.clientPort, response)
                    break

                # Evaluación del método SIP recibido
                self.checkmethod()

    def checkmethod(self):
        """
        Método para evaluar método SIP recibido
        """
        # ------------------------- REGISTER ----------------------------------
        if self.method == 'REGISTER':
            expires = float(self.option)

            # Comprobamos caducidad de usuarios registrados
            self.check_expires()

            # Registro del usuario
            if expires != 0:
                users[self.address] = (self.clientIP, expires, time.time(),
                                          self.clientPort)
                self.register2file()
                print "Añadido el usuario " + self.address
                # Envío de "OK"
                response = MY_VERSION + " 200 OK\r\n\r\n"
                self.wfile.write(response)
                log_debug('send', self.clientIP, self.clientPort, response)

            # Borrado del usuario (si existe en el diccionario)
            else:
                found = 0
                for user in users:
                    if self.address == user:
                        found = 1
                # Usuario encontrado
                if found:
                    del users[self.address]
                    self.register2file()
                    print "Eliminado el usuario " + self.address
                    # Envío de "OK"
                    response = MY_VERSION + " 200 OK\r\n\r\n"
                    self.wfile.write(response)
                    log_debug('send', self.clientIP, self.clientPort, response)
                # Ususario no encontrado
                else:
                    # Envío de "Not Found"
                    response = MY_VERSION + " 404 User Not Found\r\n\r\n"
                    self.wfile.write(response)
                    log_debug('send', self.clientIP, self.clientPort, response)

        # ------------------------- INVITE ------------------------------------
        elif self.method == 'INVITE':
            # Envío de "Trying, Ringing, OK"
            response = MY_VERSION + " 100 Trying\r\n\r\n"\
                     + MY_VERSION + " 180 Ringing\r\n\r\n"\
                     + MY_VERSION + " 200 OK\r\n\r\n"
            self.wfile.write(response)
            log_debug('send', self.clientIP, self.clientPort, response)

        # -------------------- Método no permitido ----------------------------
        else:
            # Envío de "Method Not Allowed"
            response = MY_VERSION + " 405 Method Not Allowed\r\n\r\n"
            self.wfile.write(response)
            log_debug('send', self.clientIP, self.clientPort, response)

    def register2file(self):
        """
        Método para imprimir los usuarios registrados en un fichero de texto
        """
        users_file = open('registered.txt', 'w')
        users_file.write('User' + '\t\t\t\t' + 'IP' + '\t\t\t' + 'Port' + '\t'\
                         + 'Log Time' + '\t\t' + 'Expires' + '\n')
        for user in users:
            ip = str(users[user][0])
            expires = str(users[user][1])
            log_time = str(users[user][2])
            port = str(users[user][3])
            users_file.write(user + "\t" + ip + "\t" + port + "\t" + log_time \
                             + "\t" + expires + "\n")
        users_file.close()

    def check_expires(self):
        """
        Método para comprobar caducidad de usuarios registrados
        """
        addresses = []
        for user in users:
            addresses.append(user)
        for address in addresses:
            expires = users[address][1]
            log_time = users[address][2]
            elapsed_time = time.time() - log_time

            # Si ha expirado el tiempo eliminamos al usuario
            if elapsed_time >= expires:
                del users[address]
                self.register2file()
                print "Tiempo expirado para " + address,
                print "--> Usuario eliminado."

class DataHandler(ContentHandler):
    """
    DataHandler class
    """
    def __init__(self):
        """
        Constructor. Inicializa el diccionario de atributos
        """
        self.attr_dicc = {}

    def startElement(self, name, attrs):
        """
        Método que añade atributos al diccionario
        """
        if name == 'log':
            path = attrs.get('path', "")
            self.attr_dicc['logPath'] = path

        if name == 'server':
            name = attrs.get('name', "")
            ip = attrs.get('ip', "")
            puerto = attrs.get('puerto', "")
            self.attr_dicc['servName'] = name
            self.attr_dicc['servIp'] = ip
            self.attr_dicc['servPort'] = puerto

        if name == 'database':
            path = attrs.get('path', "")
            passwdpath = attrs.get('passwdpath', "")
            self.attr_dicc['regPath'] = path
            self.attr_dicc['regPasswdPath'] = passwdpath

    def get_attrs(self):
        """
        Método que devuelve lista con atributos
        """
        return self.attr_dicc

#--------------------------------- Métodos ------------------------------------
def log_debug(oper, ip, port, msg):
    """
    Método para imprimir log en fichero de texto y debug por pantalla
    """
    formatTime = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    msgLine = msg.replace("\r\n", " ")
    info = ''
    if oper == 'send':
        info = "Send to " + str(ip) + ':' + str(port) + ':'
        print info + '\n' + msg
    elif oper == 'receive':
        info = "Received from " + str(ip) + ':' + str(port) + ':'
        print info + '\n' + msg
    elif oper == 'error':
        print formatTime + ' ' + msg
    logFile = open(LOG_FILE, 'a')
    logFile.write(formatTime + ' ' + info + msgLine + '\n')
    logFile.close()

#-----------------------------Programa principal-------------------------------
if __name__ == "__main__":

    # Versión del protocolo SIP
    MY_VERSION = "SIP/2.0"

    # Evaluación de parámetros de la línea de comandos
    if len(sys.argv) != 2:
        sys.exit("Usage: python proxy_registrar.py config")
    else:
        CONFIG = sys.argv[1]

    # Parseo del fichero XML
    parser = make_parser()
    dataHandler = DataHandler()
    parser.setContentHandler(dataHandler)
    parser.parse(open(CONFIG))

    # Lectura del archivo de configuración UA
    attr_dicc = dataHandler.get_attrs()
    SERVERNAME = attr_dicc['servName']
    MY_IP = attr_dicc['servIp']
    MY_PORT = int(attr_dicc['servPort'])
    REG_FILE = attr_dicc['regPath']
    REGPASS_FILE = attr_dicc['regPasswdPath']
    LOG_FILE = attr_dicc['logPath']

    # Comenzando el programa...
    log_debug('', '', '', 'Starting...')

    # Creamos servidor de eco y escuchamos
    serv = SocketServer.UDPServer((MY_IP, MY_PORT), EchoHandler)
    print "Server " + SERVERNAME + " listening at port " + str(MY_PORT) + "..."
    serv.serve_forever()
