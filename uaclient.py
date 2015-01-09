#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
UACLIENT
"""
import os
import sys
import socket
import time
from uaserver import MiThread


try:
    UA = sys.argv[0] = 'uaclient.py'
    CONFIG = sys.argv[1]
    METOD = sys.argv[2]
    OPTION = sys.argv[3]
    data = []
    tt = str(time.time())
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
    #PUERTO AUDIO RTP
    line_rtp = line[3].split(">")
    rtpaudio = line_rtp[0].split("=")[1]
    PUERTO_AUDIO = rtpaudio.split(" ")[0][1:-1]
    #IP DEL PROXY
    line_regproxy = line[4].split(">")
    regproxy = line_regproxy[0].split("=")[1]
    IP_PROXY = regproxy.split(" ")[0][1:-1]
    #PUERTO DEL PROXY
    regproxy1 = line_regproxy[0].split("=")[2]
    PUERTO_PROXY = regproxy1.split(" ")[0][1:-1]
    #PATH DEL LOG
    line_log = line[5].split(">")
    log = line_log[0].split("=")[1]
    PATH_LOG = log.split(" ")[0][1:-1]
    #PATH DEL AUDIO
    line_audio = line[6].split(">")
    audio = line_audio[0].split("=")[1]
    PATH_AUDIO = audio.split(" ")[0][1:-1]
    #Contraseña
    passw = line_account[0].split("=")[2]
    PASSWORD = passw.split(" ")[0][1:-1]

    #Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP_PROXY, int(PUERTO_PROXY)))

    fich = open(PATH_LOG, 'a')

    def dataf(my_socket):
        global data
        my_socket.send(LINEA)

        try:
            data = my_socket.recv(1024)
        except socket.error:
            fich.write(tt + " Error:No server listening at "
                       + IP_PROXY + " port " + PUERTO_PROXY)
            sys.exit(tt + " Error:No server listening at "
                     + IP_PROXY + " port " + PUERTO_PROXY)

    if len(sys.argv) != 4:
        LINEA = 'Bad_Request'
        dataf(my_socket)
        print data
        sys.exit("Usage: python uaclient.py config method option")
except IndexError:
    print 'SIP/2.0 400 Bad Request' + '\r\n'
    sys.exit("Usage: python uaclient.py config method option")

#Metodos posibles a enviar
Lista = ["REGISTER", "INVITE", "BYE"]
if METOD not in Lista:
    print "Usage: python uaclient.py config method option" + '\r\n'
    LINEA = str(METOD) + ' ' + str(OPTION)
    dataf(my_socket)
    print data
    print "Method = " + str(Lista)

if METOD == 'REGISTER':
    fich = open(PATH_LOG, 'a')
    Sent_Register = ": REGISTER sip:" + USUARIO + ":" + PUERTO
    Sent_Register += " SIP/2.0 Expires: " + OPTION + '\r\n'
    fich.write(tt + " Sent to " + IP_PROXY + ":"
               + PUERTO_PROXY + Sent_Register)

    LINEA1 = "REGISTER " + "sip:" + USUARIO
    LINEA1 += ":" + PUERTO + " SIP/2.0\r\n" + "Expires: " + OPTION + "\r\n\r\n"
    Contrasena = ' Password: ' + PASSWORD + ' \r\n'
    LINEA = LINEA1 + Contrasena
    print LINEA1
    dataf(my_socket)
    rcv_register = data.split('\r\n\r\n')[0:-1]
    if rcv_register == ['SIP/2.0 200 OK']:
        print "Recibido --", data
        fich.write(tt + " Received from " + IP_PROXY
                   + ":" + PUERTO_PROXY + ": 200 OK" + '\r\n')
    else:
        print data

    if OPTION == '0':
        fich.write(tt + " Terminando socket..." + USUARIO + '\r\n')
        fich.close()
        print "Terminando socket..."
        my_socket.close()
    else:
        fich.write(tt + " Starting..." + '\r\n')

if METOD == 'INVITE':
    fich = open(PATH_LOG, 'a')
    LINEA = "INVITE " + "sip:" + OPTION + " SIP/2.0\r\n"
    LINEA += "Content-Type: application/sdp\r\n\r\n" + "v=0\r\n"
    LINEA += "o=" + USUARIO + " " + IP + " \r\n"
    LINEA += "s=vampireando" + "\r\n" + "t=0" + "\r\n"
    LINEA += "m=audio " + PUERTO_AUDIO + " RTP" + "\r\n"
    fich.write(tt + " Sent to " + IP_PROXY + ":"
               + PUERTO_PROXY + ': ' + LINEA + '\r\n')
    print LINEA
    dataf(my_socket)

    try:
        if data != 'Accion no posible sin registrar\r\n':
            if data != "SIP/2.0 404 User Not Found":
                Puerto_RTP = data.split(' ')[14]
                rcv_invite = data.split('\r\n\r\n')[0:-1]
                rcv_invite1 = rcv_invite[0:3]
                rcv_invite2 = str(rcv_invite1)
                print 'Recibido PROXY: ' + rcv_invite2
                fich.write(tt + " Received from " + IP_PROXY
                           + ":" + PUERTO_PROXY + ': ' + rcv_invite2 + '\r\n')
                METOD = 'ACK'
                NEWLINE = METOD + ' sip:' + OPTION + ' SIP/2.0\r\n'
                print '\r\n\r\n' + "Enviando: " + NEWLINE
                fich.write(tt + " Sent to " + IP_PROXY + ":"
                           + PUERTO_PROXY + ': ' + NEWLINE)
                my_socket.send(NEWLINE)
                fich.write(tt + ' Conexion audio RTP ' + '\r\n')
                t = MiThread(IP, Puerto_RTP)
                t.start()
                t.join()
                aAejecutar = './mp32rtp -i ' + IP + ' -p '
                aAejecutar += str(Puerto_RTP) + ' < ' + PATH_AUDIO
                print 'Vamos a ejecutar', aAejecutar
                os.system(aAejecutar)
                print 'Ejecutado', '\r\n\r\n'
            else:
                print data
        else:
            print data

    except IndexError:
        fich.write(tt + " Error:No uaserver listening")
        sys.exit(tt + " Error:No uaserver listening")

if METOD == 'BYE':
    fich = open(PATH_LOG, 'a')
    Sent_BYE = 'BYE ' + "sip:" + OPTION + " SIP/2.0" + '\r\n'
    print Sent_BYE
    Mi_Direccion = 'Mi direccion es ' + USUARIO
    LINEA = Sent_BYE + Mi_Direccion
    fich.write(tt + " Sent to " + IP_PROXY
               + ":" + PUERTO_PROXY + ': ' + Sent_BYE)
    dataf(my_socket)

    rcv_bye = data.split('\r\n\r\n')[0:-1]
    if rcv_bye == ['SIP/2.0 200 OK']:
        fich.write(tt + " Received from " + IP_PROXY
                   + ":" + PUERTO_PROXY + ": 200 OK" + '\r\n')
        fich.close()
        print data
    else:
        print data
