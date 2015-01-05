#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
UACLIENT
"""
import os
import sys
import socket
import time


try:
    UA = sys.argv[0] = 'uaclient.py'
    CONFIG = sys.argv[1]
    METOD = sys.argv[2]
    OPTION = sys.argv[3]
except IndexError:
    sys.exit("Usage: python uaclient.py config method option")

#Metodos posibles a enviar
Lista = ["REGISTER", "INVITE", "BYE"]
if METOD not in Lista:
    sys.exit("Usage: python uaclient.py config method option")

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

#Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IP_PROXY, int(PUERTO_PROXY)))

fich = open(PATH_LOG, 'r+')

if METOD == 'REGISTER':
    fich.write(str(time.time()) + " Starting..." + '\r\n')
    Sent_Register = ": REGISTER sip:" + USUARIO + ":" + PUERTO + " SIP/2.0 Expires: " + OPTION + '\r\n'
    fich.write(str(time.time()) + " Sent to " + IP_PROXY + ":" + PUERTO_PROXY + Sent_Register)

    LINEA = 'REGISTER ' + "sip:" + USUARIO 
    LINEA += ":" + PUERTO + " SIP/2.0 \r\n" + "Expires: " + OPTION + '\r\n'
    print LINEA
    my_socket.send(LINEA)

    try:
        data = my_socket.recv(1024)
    except socket.error:
        fich.write(str(time.time()) + " Error:No server listening at " + IP_PROXY + " port " + PUERTO_PROXY)
        sys.exit(str(time.time()) + " Error:No server listening at " + IP_PROXY + " port " + PUERTO_PROXY)

    rcv_register = data.split('\r\n\r\n')[0:-1]
    if rcv_register == ['SIP/2.0 200 OK']:
        print "Recibido --", data
        fich.write(str(time.time()) + " Received from " + IP_PROXY + ":" + PUERTO_PROXY + ": 200 OK" + '\r\n')
    fich.close() 

    if OPTION == '0':
        fich = open(PATH_LOG, 'a')
        fich.write(str(time.time()) + " Finishing..." + '\r\n')
        fich.close()
        print "Terminando socket..."
        my_socket.close()  

if METOD == 'INVITE':
    fich = open(PATH_LOG, 'a')
    Sent_Invite = ": INVITE sip:" + USUARIO + ":" + PUERTO + " SIP/2.0 Expires: " + OPTION + '\r\n'
    fich.write(str(time.time()) + " Sent to " + IP_PROXY + ":" + PUERTO_PROXY + Sent_Invite)
    LINEA1 = 'INVITE ' + "sip: " + OPTION + " SIP/2.0 \r\n"
    LINEA1 += "Content-Type: application/sdp \r\n\r\n" + "v=0 \r\n"        
    LINEA1 +="o=" + USUARIO + " " + IP + ' \r\n'
    LINEA1 += "s=vampireando"
    LINEA1 +=' \r\n' + "t=0" + ' \r\n' + "m=audio " + PUERTO_AUDIO + ' RTP' + '\r\n'
    fich.write(str(time.time()) + " " + LINEA1)
    my_socket.send(LINEA1)
    print LINEA1
    try:
        data1 = my_socket.recv(1024)
    except socket.error:
        fich.write(str(time.time()) + " Error:No server listening at " + IP_PROXY + " port " + PUERTO_PROXY)
        sys.exit(str(time.time()) + " Error:No server listening at " + IP_PROXY + " port " + PUERTO_PROXY)
    except IndexError:
        fich.write(str(time.time()) + " Error:No uaserver listening")
        sys.exit(str(time.time()) + " Error:No uaserver listening")

    if data1 != "SIP/2.0 404 User Not Found":
        Puerto_RTP = data1.split(' ')[14]
        rcv_invite = data1.split('\r\n\r\n')[0:-1]
        rcv_invite1 = rcv_invite[0:3]
        rcv_invite2 = str(rcv_invite1)
        print 'Recibido ' + rcv_invite2
        fich.write(str(time.time()) + " Received from " + IP_PROXY + ":" + PUERTO_PROXY + ': ' + rcv_invite2)
        METOD = 'ACK'
        NEWLINE = METOD + ' sip:' + OPTION + ' SIP/2.0\r\n\r\n' + PUERTO_AUDIO
        print '\r\n\r\n' + "Enviando: " + NEWLINE
        fich.write(str(time.time()) + " Sent to " + IP_PROXY + ":" + PUERTO_PROXY + ': ' + NEWLINE)
        my_socket.send(NEWLINE)
        fich.write(str(time.time()) + 'Conexion audio RTP ')
        aAejecutar = './mp32rtp -i ' + IP + ' -p ' + str(Puerto_RTP) + ' < ' + PATH_AUDIO
        print 'Vamos a ejecutar', aAejecutar
        os.system(aAejecutar)
        print 'Ejecutado', '\r\n\r\n'
    else:
        print data1

if METOD == 'BYE':
    fich = open(PATH_LOG, 'a')
    Sent_BYE = 'BYE ' + "sip:" + OPTION + " SIP/2.0" + '\r\n\r\n'
    print Sent_BYE
    fich.write(str(time.time()) + " Sent to " + IP_PROXY + ":" + PUERTO_PROXY + Sent_BYE)
    my_socket.send(Sent_BYE + '\r\n\r\n')
    try:
        data = my_socket.recv(1024)
    except socket.error:
        fich.write(str(time.time()) + " Error:No server listening at " + IP_PROXY + " port " + PUERTO_PROXY)
        sys.exit(str(time.time()) + " Error:No server listening at " + IP_PROXY + " port " + PUERTO_PROXY)
    except IndexError:
        fich.write(str(time.time()) + " Error:No uaserver listening")
        sys.exit(str(time.time()) + " Error:No uaserver listening")

    rcv_bye = data.split('\r\n\r\n')[0:-1]
    if rcv_bye == ['SIP/2.0 200 OK']:
        fich.write(str(time.time()) + " Received from " + IP_PROXY + ":" + PUERTO_PROXY + ": 200 OK" + '\r\n')
        fich.close()
        print data
