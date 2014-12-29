# !/usr/bin/python
# -*- coding: utf-8 -*-

from xml.sax import make_parser
import datahandler
import sys
import os


class ConfigReader(datahandler.DataHandler):
    """
    Clase XMLReader. Parsea e imprime en orden el XML
    """

    def __init__(self, my_file):
        """
        Constructor. Parsea el fichero SMIL y obtiene etiquetas y atributos.
        """
        parser = make_parser()
        dataHandler = datahandler.DataHandler()
        parser.setContentHandler(dataHandler)
        parser.parse(open(my_file))

        self.tag_list = dataHandler.get_tags()

    def __str__(self):
        """
        Método que imprime lista de etiquetas y atributos.
        """
        tag_list = ""
        for element in self.tag_list:
            # Índice par: etiqueta; índice impar: atributo
            if not self.tag_list.index(element) % 2:
                tag_list += element + '\t'
            else:
                for key in element:
                    if element[key] != "":
                        tag_list += '%s="%s"\t' % (key, element[key])
                tag_list += '\n'
        return tag_list
