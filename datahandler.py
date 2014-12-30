# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
Definición de la clase DataHandler
"""

from xml.sax.handler import ContentHandler


class DataHandler(ContentHandler):
    """
    Clase DataHandler
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
            self.attr_dicc['username'] = username
            self.attr_dicc['userpass'] = passwd

        if name == 'uaserver':
            ip = attrs.get('ip', "")
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
