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
import socket


# Variables globales
users = {}
LOG_FILE = ""

#-------------------------------- Clases --------------------------------------
class SIPProxyRegisterHandler(SocketServer.DatagramRequestHandler):
    """
    Clase SIPProxyRegisterHandler. Recibe, procesa y reenvía mensajes SIP
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
            self.request = self.rfile.read()
            # Si no hay más líneas salimos del bucle infinito
            if not self.request:
                break
            else:
                # Evaluación parámetros obligatorios enviados por cliente
                log_debug('receive', self.clientIP, self.clientPort,
                          self.request)
                try:
                    self.request_list = self.request.split()
                    self.method = self.request_list[0]
                    protocol = self.request_list[1].split(':')[0]
                    self.address = self.request_list[1].split(':')[1]
                    client_version = self.request_list[2]
                # Excepción. Envío de "Bad Request"
                except:
                    response = MY_VERSION + " 400 Bad Request\r\n\r\n"
                    self.wfile.write(response)
                    log_debug('send', self.clientIP, self.clientPort, response)
                    break
                # Petición incorrecta. Envío de "Bad Request"
                if protocol != 'sip' or client_version != 'SIP/1.0'\
                    and client_version != 'SIP/2.0':
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
        # -------------------------- REGISTRO ---------------------------------
        if self.method == 'REGISTER':
            # Evaluación de puerto y parámetro opcional
            try:
                server_port = self.request_list[1].split(':')[2]
                expires = float(self.request_list[4])
            except:
                # Envío de "Bad Request"
                response = MY_VERSION + " 400 Bad Request\r\n\r\n"
                self.wfile.write(response)
                log_debug('send', self.clientIP, self.clientPort, response)
                pass
            # Comprobamos caducidad de usuarios registrados
            self.check_expires()
            # Registro del usuario
            if expires != 0:
                users[self.address] = (self.clientIP, expires, time.time(),
                                       server_port)
                self.register2file()
                print "Added user " + self.address + ':' + str(server_port)
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
                # Usuario encontrado en registro
                if found:
                    print "Deleted user " + self.address + ':' \
                          + users[self.address][3]
                    del users[self.address]
                    self.register2file()
                    # Envío de "OK"
                    response = MY_VERSION + " 200 OK\r\n\r\n"
                    self.wfile.write(response)
                    log_debug('send', self.clientIP, self.clientPort, response)
                # Ususario no encontrado en registro
                else:
                    # Envío de "Not Found"
                    response = MY_VERSION + " 404 User Not Found\r\n\r\n"
                    self.wfile.write(response)
                    log_debug('send', self.clientIP, self.clientPort, response)
        # ----------------------- REENVÍO DE INVITE y BYE ---------------------
        elif self.method == 'INVITE' or self.method == 'BYE':
            found = 0
            for user in users:
                if self.address == user:
                    found = 1
            # UA destino registrado
            if found:
                ua_destIP = users[self.address][0]
                ua_destPort = int(users[self.address][3])
                # Reenvío de solicitud al UA destino
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                send(my_socket, self.request, ua_destIP, ua_destPort)
                response = receive(my_socket, ua_destIP, ua_destPort)
                my_socket.close()
                # Reenvío de respuesta al UA origen
                self.wfile.write(response)
                log_debug('send', self.clientIP, self.clientPort, response)
            # UA destino no registrado
            if not found:
                # Envío de "Not Found"
                response = MY_VERSION + " 404 User Not Found\r\n\r\n"
                self.wfile.write(response)
                log_debug('send', self.clientIP, self.clientPort, response)
        # ------------------------- REENVÍO DE ACK ----------------------------
        elif self.method == 'ACK':
            # Buscamos IP y puerto del UA destino
            for user in users:
                if self.address == user:
                    ua_destIP = users[user][0]
                    ua_destPort = int(users[user][3])
            # Reenvío de solicitud al UA destino
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            send(my_socket, self.request, ua_destIP, ua_destPort)
            my_socket.close()
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

class XMLHandler(ContentHandler):
    """
    Clase XMLHandler. Extrae etiquetas y atributos de un XML
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
            ip = attrs.get('ip', "127.0.0.1")
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
        info = "Send to " + str(ip) + ':' + str(port) + ': '
        print info + '\n' + msg
    elif oper == 'receive':
        info = "Received from " + str(ip) + ':' + str(port) + ': '
        print info + '\n' + msg
    else:
        print formatTime + ' ' + msg
    logFile = open(LOG_FILE, 'a')
    logFile.write(formatTime + ' ' + info + msgLine + '\n')
    logFile.close()

def send(my_socket, request, servIP, servPort):
    """
    Método para enviar solicitur a un servidor
    """
    # Creamos el socket, lo configuramos y lo atamos al servidor/puerto
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((servIP, servPort))
    # Enviamos solicitud
    my_socket.send(request)
    log_debug('send', servIP, servPort, request)

def receive(my_socket, servIP, servPort):
    """
    Método para recibir respuesta de un servidor
    """
    # Recibimos respuesta
    try:
        response = my_socket.recv(1024)
    except socket.error:
        error_msg = "Error: No server listening at " + servIP  + " port " \
                  + str(servPort)
        log_debug('', '', '', error_msg)
        raise SystemExit
    log_debug('receive', servIP, servPort, response)
    return response

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
    xmlHandler_obj = XMLHandler()
    parser.setContentHandler(xmlHandler_obj)
    parser.parse(open(CONFIG))
    # Lectura del archivo de configuración UA
    attr_dicc = xmlHandler_obj.get_attrs()
    SERVERNAME = attr_dicc['servName']
    MY_IP = attr_dicc['servIp']
    MY_PORT = int(attr_dicc['servPort'])
    REG_FILE = attr_dicc['regPath']
    REGPASS_FILE = attr_dicc['regPasswdPath']
    LOG_FILE = attr_dicc['logPath']
    # Comenzando el programa...
    log_debug('', '', '', 'Starting...')
    # Creamos servidor SIP y escuchamos
    serv = SocketServer.UDPServer((MY_IP, MY_PORT), SIPProxyRegisterHandler)
    print "Server " + SERVERNAME + " listening at " + MY_IP + ':' \
          + str(MY_PORT) + "..."
    serv.serve_forever()
