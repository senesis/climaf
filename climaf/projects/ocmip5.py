"""

This module declares how to access OCMIP5 data on Ciclad.

Use attributes 'model' and 'frequency'

Example of a path : /prodigfs/OCMIP5/OUTPUT/IPSL/IPSL-CM4/CTL/mon/CACO3/CACO3_IPSL_IPSL-CM4_CTL_1860-1869.nc


Example ::

    >>> cdef('model','IPSL-CM4') 
    >>> cdef('frequency','mon') 
    >>> cactl=ds(project='OCMIP5_Ciclad', experiment='CTL', variable='CACO3', period='1860-1861')


"""

import os

import climaf

if climaf.site_settings.onCiclad :
    climaf.classes.cproject("OCMIP5","model","frequency")
    climaf.dataloc.dataloc(project="OCMIP5", organization="generic",
            url=['/prodigfs/OCMIP5/OUTPUT/*/${model}/${experiment}/${frequency}/'
                 '${variable}/${variable}_*_${model}_${experiment}_YYYY-YYYY.nc'])
    