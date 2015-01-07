#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un User Agent Server en SIP
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import SocketServer
import sys
import os
import time


# Variables globales
MY_ADDRESS = ''
MY_SERVIP = ''
RTP_PORT = ''
uaorig_tuple = ()

#--------------------------------- Clases -------------------------------------
class SIPHandler(SocketServer.DatagramRequestHandler):
    """
    Clase SIPHandler. Recibe, procesa y envía mensajes SIP
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
        # ------------------------- INVITE ------------------------------------
        if self.method == 'INVITE':
            try:
                # Evaluación de parámetros SDP
                uaorig_IP = self.request_list[7]
                uaorig_mediaport = self.request_list[11]
                global uaorig_tuple # (Para poder modificar la var. global)
                uaorig_tuple = (uaorig_IP, uaorig_mediaport)
            except:
                # Excepción. Envío de "Bad Request"
                response = MY_VERSION + " 400 Bad Request\r\n\r\n"
                self.wfile.write(response)
                log_debug('send', self.clientIP, self.clientPort, response)
                pass
            # Petición incorrecta. Envío de "Bad Request"
            if self.request_list[4] != 'application/sdp':
                response = MY_VERSION + " 400 Bad Request\r\n\r\n"
                self.wfile.write(response)
                log_debug('send', self.clientIP, self.clientPort, response)
            # Petición correcta. Envío de "Trying, Ringing, OK"
            else:
                response = MY_VERSION + " 100 Trying\r\n\r\n"\
                         + MY_VERSION + " 180 Ringing\r\n\r\n"\
                         + MY_VERSION + " 200 OK\r\n"\
                         + 'Content-Type: application/sdp\r\n\r\n' + 'v=0\r\n'\
                         + 'o=' + MY_ADDRESS + ' ' + MY_IP + '\r\n'\
                         + 's=sesion_sip\r\n' + 't=0\r\n' + 'm=audio '\
                         + str(RTP_PORT) + ' RTP\r\n'
                self.wfile.write(response)
                log_debug('send', self.clientIP, self.clientPort, response)
        # ---------------------------- ACK ------------------------------------
        elif self.method == 'ACK':
            uadest_IP = uaorig_tuple[0]
            uadest_mediaport = uaorig_tuple[1]
            # Escucha con (c)vlc en background del audio enviado (OPCIONAL)
            toRun = "cvlc rtp://@" + uadest_IP + ":" + uadest_mediaport + "&"
            os.system(toRun)
            # --------------------- Envío RTP ---------------------------------
            toRun = "./mp32rtp -i " + uadest_IP + " -p " + uadest_mediaport \
                  + " < " + AUDIO_FILE
            log_debug('send', uadest_IP, uadest_mediaport, AUDIO_FILE)
            print "Sending RTP audio to UA..."
            os.system(toRun)
            print "Sending RTP audio completed."
        # ---------------------------- BYE ------------------------------------
        elif self.method == 'BYE':
            # Envío de "OK"
            response = MY_VERSION + " 200 OK\r\n\r\n"
            self.wfile.write(response)
            log_debug('send', self.clientIP, self.clientPort, response)
        # -------------------- Método no permitido ----------------------------
        else:
            # Envío de "Method Not Allowed"
            response = MY_VERSION + " 405 Method Not Allowed\r\n\r\n"
            self.wfile.write(response)
            log_debug('send', self.clientIP, self.clientPort, response)

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
        if name == 'account':
            username = attrs.get('username', "")
            passwd = attrs.get('passwd', "")
            self.attr_dicc['userName'] = username
            self.attr_dicc['userPass'] = passwd
        if name == 'uaserver':
            ip = attrs.get('ip', "127.0.0.1")
            puerto = attrs.get('puerto', "")
            self.attr_dicc['servIp'] = ip
            self.attr_dicc['servPort'] = puerto
        if name == 'rtpaudio':
            puerto = attrs.get('puerto', "")
            self.attr_dicc['rtpPort'] = puerto
        if name == 'regproxy':
            ip = attrs.get('ip', "")
            puerto = attrs.get('puerto', "")
            self.attr_dicc['proxIp'] = ip
            self.attr_dicc['proxPort'] = puerto
        if name == 'log':
            path = attrs.get('path', "")
            self.attr_dicc['logPath'] = path
        if name == 'audio':
            path = attrs.get('path', "")
            self.attr_dicc['audioPath'] = path

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

#-----------------------------Programa principal-------------------------------
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
    xmlHandler_obj = XMLHandler()
    parser.setContentHandler(xmlHandler_obj)
    parser.parse(open(CONFIG))
    # Lectura del archivo de configuración UA
    attr_dicc = xmlHandler_obj.get_attrs()
    MY_USERNAME = attr_dicc['userName']
    MY_USERPASS = attr_dicc['userPass']
    MY_IP = attr_dicc['servIp']
    MY_PORT = int(attr_dicc['servPort'])
    RTP_PORT = attr_dicc['rtpPort']
    PROX_IP = attr_dicc['proxIp']
    PROX_PORT = attr_dicc['proxPort']
    LOG_FILE = attr_dicc['logPath']
    AUDIO_FILE = attr_dicc['audioPath']
    # Dirección SIP
    MY_ADDRESS = MY_USERNAME + '@dominio.com'
    # Comenzando el programa...
    log_debug('', '', '', 'Starting...')
    # Creamos servidor SIP y escuchamos
    serv = SocketServer.UDPServer((MY_IP, MY_PORT), SIPHandler)
    print "UA Server listening at " + MY_IP + ':' + str(MY_PORT) + "..."
    serv.serve_forever()
