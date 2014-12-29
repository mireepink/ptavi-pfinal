#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa User Agent Client para comunicación SIP
"""

import configreader
import socket
import sys


# Protocolo y versión
PROTOCOL = "sip"
VERSION = "SIP/2.0"

# Parámetros del usuario.
if len(sys.argv) != 4:
    sys.exit("Usage: python uaclient.py config method option")
else:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2].upper()
    OPTION = sys.argv[3]

    # Lectura e impresión del archivo de configuración
    config = configreader.ConfigReader(CONFIG)
    print config
