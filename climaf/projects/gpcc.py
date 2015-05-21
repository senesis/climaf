"""

This module declares GPCC data organization and specifics, as managed by Sophie T. at CNRM;

**Also declares how to derive CMIP5 variables from the original GPCC variables set**

Attributes are 'grid'

Various grids are available. Grids write e.g. as : grid='05d', grid ='1d' and grid ='T127'

Example of an 'gpcc' project dataset declaration ::

 >>> cdef('project','gpcc')
 >>> d=ds(variable='pr',period='198001',grid='05d')
 >>> d2=ds(variable='pr',period='198001',grid='1d')
 >>> d3=ds(variable='pr',period='198001',grid='T127')

"""

from climaf.dataloc import dataloc
from climaf.classes import cproject, calias
from climaf.site_settings import atCNRM

if atCNRM:
    cproject('gpcc','grid')  # grid writes as '05d', '1d' or 'T127'

    url_gpcc="/cnrm/vdr/DATA/OBS/netcdf/monthly_mean/gpcc/GPCC.Reanalysis.${grid}.nc"
    dataloc(project='gpcc', organization='generic', url=[url_gpcc])


    # Defining alias and derived variables for GPCC, together with filenames
    ##############################################################################

    calias("gpcc",'pr'       ,'GPCC' ,scale=1./86400. ,filenameVar='GPCC',units="kg.m-2.s-1")

    #calias("gpcc",'site'    ,'NSTA'  ,filenameVar='GPCC') 
    #NSTA:="Number of stations available for a specific analysis grid in a specific month" 

