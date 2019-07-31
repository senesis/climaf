#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import  # , unicode_literals

# Some projects like atmosphere_derived_variables, others don't
# __all__= [ "atmosphere_derived_variables", "ocean_derived_variables" ]
__all__ = ["ocean_derived_variables"]

from climaf.site_settings import atIPSL, atCerfacs

# -- Load only the ipsl derived variables if we are at IPSL
if atIPSL:
    from . import ipsl_derived_variables

# Load atmosphere derived variables at Cerfacs
if atCerfacs:
    from . import atmosphere_derived_variables
