#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
CliMAF utilities.
"""

from __future__ import print_function, division, unicode_literals, absolute_import

from climaf.clogging import clogger, dedent


class Climaf_Error(Exception):
    def __init__(self, valeur):
        self.valeur = valeur
        clogger.error(self.__str__())
        dedent(100)

    def __str__(self):
        return repr(self.valeur)


class Climaf_Classes_Error(Climaf_Error):
    pass


class Climaf_Cache_Error(Climaf_Error):
    pass


class Climaf_Operator_Error(Climaf_Error):
    pass


class Climaf_Data_Error(Climaf_Error):
    pass
