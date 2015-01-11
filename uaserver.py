#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
UASERVER
"""

import SocketServer
import sys
import os
import os.path
import socket
import threading
import time


class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    server class
    """

    def handle(self):
        while 1:
            global Puerto_RTP
            # Leyendo línea a línea lo que nos envía el cliente
            lines = self.rfile.read()
            # Si no hay más líneas salimos del bucle infinito
            if not lines:
                break
            print "El cliente nos manda " + lines
            Metod = lines.split(' ')[0]
            if not Metod in Metodos:
                self.wfile.write('SIP/2.0 405 Method Not Allowed' + '\r\n\r\n')
                print 'SIP/2.0 405 Method Not Allowed' + '\r\n\r\n'
            elif Metod == 'INVITE':
                Destinatario = lines.split(' ')[2]
                Puerto_RTP = lines.split(' ')[6]
                print 'Mandamos...'
                rcv_invite = 'SIP/2.0 100 Trying' + '\r\n\r\n'
                rcv_invite += 'SIP/2.0 180 Ringing' + '\r\n\r\n'
                rcv_invite += 'SIP/2.0 200 OK' + '\r\n\r\n'
                rcv_invite += "Content-Type: application/sdp \r\n\r\n"
                rcv_invite += "v=0 \r\n" + "o=" + USUARIO + " " + IP + ' \r\n'
                rcv_invite += "s=vampireando" + ' \r\n' + "t=0" + ' \r\n'
                rcv_invite += "m=audio " + str(PUERTO_AUDIO) + ' RTP\r\n\r\n'
                print rcv_invite
                self.wfile.write(rcv_invite)
            elif Metod == 'ACK':
                t = MiThread(IP, Puerto_RTP, PATH_AUDIO)
                t.start()
                t.join()
            elif Metod == 'BYE':
                self.wfile.write('SIP/2.0 200 OK' + '\r\n\r\n')
                print 'Terminando conversación...'
            elif len(lines) != 4:
                self.wfile.write('SIP/2.0 400 Bad Request' + '\r\n\r\n')
                print 'SIP/2.0 400 Bad Request' + '\r\n\r\n'


class MiThread(threading.Thread):
    """
    Thread class
    """

    def __init__(self, IP, Puerto_RTP, PATH_AUDIO):
        threading.Thread.__init__(self)
        self.IP = IP
        self.Puerto_RTP = Puerto_RTP
        self.Path_Audio = PATH_AUDIO

    def run(self):
        aAejecutar1 = 'cvlc rtp://@' + self.IP + ':'
        aAejecutar1 += str(self.Puerto_RTP) + ' &'
        print 'Vamos a ejecutar', aAejecutar1
        os.system(aAejecutar1)
        aAejecutar = './mp32rtp -i ' + self.IP + ' -p '
        aAejecutar += str(self.Puerto_RTP) + ' < ' + self.Path_Audio
        print 'Vamos a ejecutar', aAejecutar
        os.system(aAejecutar)
        print 'Ejecutado', '\r\n\r\n'

if __name__ == "__main__":

    Puerto_RTP = []
    Metodos = ['INVITE', 'ACK', 'BYE']
    try:
        UA = sys.argv[0] = 'uaserver.py'
        CONFIG = sys.argv[1]
    except IndexError:
        sys.exit("Usage: python uaserver.py config")

    print 'Listening...'
    #Abrimos el fichero xml y leemos de él la información
    fich = open(CONFIG, 'r')
    line = fich.readlines()
    fich.close()
    #USUARIO
    line_account = line[1].split(">")
    account = line_account[0].split("=")[1]
    USUARIO = account.split(" ")[0][1:-1]
    #IP
    line_uaserver = line[2].split(">")
    uaserver = line_uaserver[0].split("=")[1]
    IP = uaserver.split(" ")[0][1:-1]
    #PUERTO
    uaserver1 = line_uaserver[0].split("=")[2]
    PUERTO = uaserver1.split(" ")[0][1:-1]
    #IP DEL PROXY
    line_regproxy = line[4].split(">")
    regproxy = line_regproxy[0].split("=")[1]
    IP_PROXY = regproxy.split(" ")[0][1:-1]
    #PUERTO DEL PROXY
    regproxy1 = line_regproxy[0].split("=")[2]
    PUERTO_PROXY = regproxy1.split(" ")[0][1:-1]
    #PUERTO AUDIO RTP
    line_rtp = line[3].split(">")
    rtpaudio = line_rtp[0].split("=")[1]
    PUERTO_AUDIO = rtpaudio.split(" ")[0][1:-1]
    #PATH DEL LOG
    line_log = line[5].split(">")
    log = line_log[0].split("=")[1]
    PATH_LOG = log.split(" ")[0][1:-1]
    #PATH DEL AUDIO
    line_audio = line[6].split(">")
    audio = line_audio[0].split("=")[1]
    PATH_AUDIO = audio.split(" ")[0][1:-1]
    if not os.path.exists(PATH_AUDIO):
        sys.exit('Usage: python uaserver.py AUDIO doesnt exist')
    print PUERTO

    #Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP_PROXY, int(PUERTO_PROXY)))

    try:
        serv = SocketServer.UDPServer(("127.0.0.1", int(PUERTO)), EchoHandler)
        serv.serve_forever()
    except KeyboardInterrupt:
        fich = open(PATH_LOG, 'a')
        fich.write(str(time.time()) + " Finishing..." + '\r\n')
        fich.close()
