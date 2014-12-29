# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
Definición de la clase DataHandler
"""

from xml.sax.handler import ContentHandler


class DataHandler(ContentHandler):
    """
    Clase DataHandler. Extrae e imprime las etiquetas y atributos del XML
    """

    def __init__(self):
        """
        Constructor. Inicializa la lista de etiquetas y atributos.
        """
        self.tag_list = []

    def startElement(self, name, attrs):
        """
        Método que añade etiquetas y atributos a la lista
        """
        if name == 'account':
            self.tag_list.append(name)

            username = attrs.get('username', "")
            passwd = attrs.get('passwd', "")
            account_attrs = {'username': username, 'passwd': passwd}

            self.tag_list.append(account_attrs)

        if name == 'uaserver':
            self.tag_list.append(name)

            ip = attrs.get('ip', "")
            puerto = attrs.get('puerto', "")
            uaserver_attrs = {'ip': ip, 'puerto': puerto}

            self.tag_list.append(uaserver_attrs)

        if name == 'rtpaudio':
            self.tag_list.append(name)

            puerto = attrs.get('puerto', "")
            rtpaudio_attrs = {'puerto': puerto}

            self.tag_list.append(rtpaudio_attrs)

        if name == 'regproxy':
            self.tag_list.append(name)

            ip = attrs.get('ip', "")
            puerto = attrs.get('puerto', "")
            regproxy_attrs = {'ip': ip, 'puerto': puerto}

            self.tag_list.append(regproxy_attrs)

        if name == 'log':
            self.tag_list.append(name)

            path = attrs.get('path', "")
            log_attrs = {'path': path}

            self.tag_list.append(log_attrs)

        if name == 'audio':
            self.tag_list.append(name)

            path = attrs.get('path', "")
            audio_attrs = {'path': path}

            self.tag_list.append(audio_attrs)

        if name == 'server':
            self.tag_list.append(name)

            name = attrs.get('name', "")
            ip = attrs.get('ip', "")
            puerto = attrs.get('puerto', "")
            server_attrs = {'name': name, 'ip': ip, 'puerto': puerto}

            self.tag_list.append(server_attrs)

        if name == 'database':
            self.tag_list.append(name)

            path = attrs.get('path', "")
            passwdpath = attrs.get('passwdpath', "")
            database_attrs = {'path': path, 'passwdpath': passwdpath}

            self.tag_list.append(database_attrs)

    def get_tags(self):
        """
        Método que devuelve lista con etiquetas, atributos y contenido de ellos
        """
        return self.tag_list
