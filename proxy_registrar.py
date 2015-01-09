#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa Proxy
"""
import sys
import SocketServer
import time
import os
import os.path
import socket


class Proxy(SocketServer.DatagramRequestHandler):

    def handle(self):
        """
        Se encarga de guardarme en un diccionario
        el cliente, su IP y su tiempo Expires al recibir un REGISTER,
        además de ir eliminando los clientes cuando Expires=0
        """
        global Continuar, Destinatario, line, Aceptado, Fichero, Registrados
        while 1:
            line = self.rfile.read()
            if not line:
                break
            line_list = line.split(' ')
            IP = self.client_address[0]
            Puerto_Emisor = self.client_address[1]
            if line_list[0] == 'Bad_Request':
                print 'PROXY: SIP/2.0 400 Bad Request' + '\r\n\r\n'
                self.wfile.write('SIP/2.0 400 Bad Request' + '\r\n\r\n')
            elif line_list[0] == 'REGISTER':
                print 'PROXY ' + line
                direccion = line_list[1].split(':')[1]
                password = line_list[5]
                self.seguridad(direccion, password)
                if Aceptado is True:
                    try:
                        expires = int(line_list[3])
                        if expires == '0':
                            fich.write(tt + " Borrando: " + direccion + '\r\n')
                        else:
                            fich.write(tt + " Starting..." + '\r\n')
                            fich.write(tt + " Register " + direccion + '\r\n')
                    except:
                        entero = 'Expires tiene que ser un numero entero\r\n'
                        print entero
                        self.wfile.write(entero)
                        break
                    print "Enviando ", "SIP/2.0 200 OK" + '\r\n\r\n'
                    self.wfile.write("SIP/2.0 200 OK" + '\r\n\r\n')
                    port = int(line_list[1].split(':')[2])
                    timenow = time.time()
                    timexp = timenow + expires
                    valores = [IP, port, timenow, timexp]
                    diccionario[direccion] = valores
                    self.register2file()
                    for direccion in diccionario.keys():
                        if timenow >= diccionario[direccion][3]:
                            del diccionario[direccion]
                            print direccion + " ha sido borrado" + '\r\n'
                    self.register2file()
            elif line_list[0] == 'INVITE':
                print 'PROXY ' + line
                Destinatario = line_list[1].split(':')[1]
                Mi_User = line_list[3].split('=')[2]
                us = False
                for linea in Fichero:
                    Usuario = linea.split('\t')[0]
                    if Usuario == Mi_User:
                        us = True
                        self.Buscar_y_enviar()
                        if Continuar is True:
                            continue
                if us is False:
                    Registrados = 'Accion no posible sin registrar\r\n'
                    print Registrados
                    self.wfile.write(str(Registrados))
            elif line_list[0] == 'ACK':
                Destinatario1 = line.split(':')[1]
                Destinatario = Destinatario1.split(' ')[0]
                print 'PROXY ' + line
                self.Buscar_y_enviar()
                if Continuar is True:
                    continue
            elif line_list[0] == 'BYE':
                print 'PROXY ' + line + '\r\n'
                bye = line_list[1]
                Destinatario = bye.split(':')[1]
                Mi_User = line_list[5]
                us = False
                for linea in Fichero:
                    Usuario = linea.split('\t')[0]
                    if Usuario == Mi_User:
                        us = True
                        self.Buscar_y_enviar()
                        if Continuar is True:
                            continue
                if us is False:
                    Registrados = 'Accion no posible sin registrar\r\n'
                    print Registrados
                    self.wfile.write(str(Registrados))
            elif not line_list[0] in Lista:
                Destinatario = line_list[1]
                self.Buscar_y_enviar()
                break

    def register2file(self):
        """
        Su función es la de escribir en el fichero los usuarios
        con su IP y tiempo
        """
        global Fichero
        fich1 = open(PATH_DATABASE, 'w')
        fich1.write("User\tIP\tPuerto\tFecha de Registro\tExpires\r\n")
        for Client in diccionario.keys():
            IP = diccionario[Client][0]
            port = diccionario[Client][1]
            timenow = diccionario[Client][2]
            timexp = diccionario[Client][3]
            fich1.write(Client + '\t' + IP + '\t' + str(port)
                        + '\t' + str(timenow) + '\t' + str(timexp) + '\r\n')
        fich1 = open(PATH_DATABASE, 'r')
        Fichero = fich1.readlines()
        fich1.close()

    def Buscar_y_enviar(self):
        """
        Buscamos la IP y el Puerto del usuario
        si esta registrado,
        para poder enviarle los mensajes
        """
        global Continuar, Destinatario, line, Fichero
        line_list = line.split(' ')
        Client = ' '
        for linea in Fichero:
            Usuario = linea.split('\t')[0]
            if Usuario == Destinatario:
                Client = Destinatario
                TO_IP = linea.split('\t')[1]
                TO_PUERTO = linea.split('\t')[2]
                #Creamos el socket
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((TO_IP, int(TO_PUERTO)))
                my_socket.send(line + '(Vía PROXY)' + '\r\n')
                myline = my_socket.recv(1024)
                if line_list[0] == 'INVITE':
                    fich.write(tt + ' Recibido ' + line + '\r\n')
                    rcv_invite = myline.split('\r\n\r\n')[0:-1]
                    rcv_invite1 = rcv_invite[0:3]
                    rcv_invite2 = str(rcv_invite1)
                    fich.write(tt + ' Enviando respuesta de '
                               + Destinatario + ': ' + rcv_invite2 + '\r\n')
                    self.wfile.write(myline)
                elif line_list[0] == 'ACK':
                    fich.write(tt + ' Recibido ACK sip: '
                               + Destinatario + '\r\n')
                elif line_list[0] == 'BYE':
                    print 'Enviando ' + myline
                    fich.write(tt + ' Recibido BYE sip: '
                               + Destinatario + '\r\n')
                    self.wfile.write(myline)
                elif not line_list[0] in Lista:
                    print myline
                    fich.write(tt + " " + myline + '\r\n')
                    self.wfile.write(myline)

        if Client != Destinatario:
            self.wfile.write("SIP/2.0 404 User Not Found")
            Continuar = True

    def seguridad(self, direccion, password):
        global diccionario, Aceptado
        fich2 = open('passwords.txt', 'r')
        passwords = fich2.readlines()
        for linea in range(len(passwords)):
            user = passwords[linea].split(' ')[1]
            passwd = passwords[linea].split(' ')[3]
            if user == direccion:
                if passwd == password:
                    print 'Check Password, usuario ' + user + ' correcto.\r\n'
                    Aceptado = True
                else:
                    msg = 'Acceso denegado '
                    print msg
                    self.wfile.write(msg)
        fich2.close()

if __name__ == "__main__":
    """
    Creamos un servidor y escuchamos
    """
    diccionario = {}
    Destinatario = []
    Continuar = False
    Aceptado = False
    line = []
    Registrados = []
    tt = str(time.time())
    IP_P = '127.0.0.1'
    #Metodos posibles
    Lista = ["REGISTER", "INVITE", "BYE"]
    try:
        UA = sys.argv[0] = 'proxy_registrar.py'
        CONFIG = sys.argv[1]
    except IndexError:
        sys.exit("Usage: python proxy_registrar.py config")

    #Abrimos el fichero xml y leemos de él la información
    fich = open(CONFIG, 'r')
    lines = fich.readlines()
    fich.close()
    #Servidor
    line_server = lines[1].split(">")
    server = line_server[0].split("=")[1]
    SERVIDOR = server.split(" ")[0][1:-1]
    #PUERTO
    puerto_ = line_server[0].split("=")[3]
    PUERTO_PROX = puerto_.split(" ")[0][1:-1]
    #DATABASE
    line_database = lines[2].split(">")
    database = line_database[0].split("=")[1]
    PATH_DATABASE = database.split(" ")[0][1:-1]
    #LOGPROX
    line_log = lines[3].split(">")
    log = line_log[0].split("=")[1]
    PATH_LOGPROX = log.split(" ")[0][1:-1]

    fich = open(PATH_LOGPROX, 'a')
    fich1 = open(PATH_DATABASE, 'a')
    fich1 = open(PATH_DATABASE, 'r+')
    Fichero = fich1.readlines()

    Mensaje_prox = "Server: " + SERVIDOR + " listening at port "
    Mensaje_prox += PUERTO_PROX + "..." + '\r\n'
    print Mensaje_prox
    try:
        proxy_serv = SocketServer.UDPServer((IP_P, int(PUERTO_PROX)), Proxy)
        proxy_serv.serve_forever()
    except KeyboardInterrupt:
        fich.write(tt + " Finishing..." + '\r\n')
        fich.close()
        fich1.close()
