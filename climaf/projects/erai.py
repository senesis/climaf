"""

This module declares ERA Interim data organization and specifics, as managed by Sophie T. at CNRM;

**Also declares how to derive CMIP5 variables from the original ERAI variables set (aliasing)**

Attributes are 'grid', and 'frequency'

Various grids are available. Original grid writes as : grid='_'. Other grids write e.g. as : grid ='.T42.'

Example of an 'erai' project dataset declaration ::

 >>> cdef('project','erai')
 >>> d=ds(variable='tas',period='198001',grid='_', frequency='monthly')
 >>> d2=ds(variable='tas',period='198001',grid='.T42',frequency='daily')

"""

from climaf.dataloc import dataloc
from climaf.classes import cproject, calias

cproject('erai','grid', 'frequency')  # no grid writes as '_' , otherwise as e.g. '.T42.'

root="/cnrm/vdr/DATA/OBS/netcdf/${frequency}"
patmonth=root+"_mean/erai/erai_???_mm_${variable}${grid}YYYY-YYYY.nc"
patday  =root+"/erai/ei_${variable}${grid}YYYY-YYYY.nc"
dataloc(project='erai', organization='generic', url=[patmonth,patday])


# Defining alias and derived variables for ERAI, together with filenames
##############################################################################
# Valid both for daily and monthly data (to check : energy flux in W for
# daily and Joules for monthly ????)

calias("erai",'sic'    ,'ci'  ,filenameVar='CI')
calias("erai",'tos'    ,'sst' ,filenameVar='SSTK')
calias("erai",'zg'     ,'z'   ,filenameVar='Z')
calias("erai",'ta'     ,'t'   ,filenameVar='T')
calias("erai",'ua'     ,'u'   ,filenameVar='U')
calias("erai",'va'     ,'v'   ,filenameVar='V')
calias("erai",'hus'    ,'q'   ,filenameVar='Q')
calias("erai",'prw'    ,'tcw' ,filenameVar='TCW')
calias("erai",'prc'    ,'cp'  ,filenameVar='CP')
calias("erai",'prl'    ,'lsp' ,filenameVar='LSP')
calias("erai",'prsn'   ,'sf'  ,filenameVar='SF')
calias("erai",'hfss'   ,'sshf',filenameVar='SSHF')
calias("erai",'hfls'   ,'slhf',filenameVar='SLHF')
calias("erai",'ps'     ,'msl' ,filenameVar='MSL')
calias("erai",'clt'    ,'tcc' ,filenameVar='TCC')
calias("erai",'uas'    ,'u10' ,filenameVar='10U')
calias("erai",'vas'    ,'v10' ,filenameVar='10V')
calias("erai",'tas'    ,'t2m' ,filenameVar='2T')
calias("erai",'das'    ,'d2m' ,filenameVar='2D')
calias("erai",'rsds'   ,'ssrd',filenameVar='SSRD')
calias("erai",'rlds'   ,'sstrd',filenameVar='SSTRD')
calias("erai",'rss'    ,'ssr' ,filenameVar='SSR')
calias("erai",'rls'    ,'str' ,filenameVar='STR')
calias("erai",'rlut'   ,'ttr' ,filenameVar='TTR')
calias("erai",'tauu'   ,'ewss',filenameVar='EWSS')
calias("erai",'tauv'   ,'nsss',filenameVar='NSSS')
calias("erai",'evspsbl','e'   ,filenameVar='E')
calias("erai",'tasmax' ,'mx2t',filenameVar='MX2T')
calias("erai",'tasmin' ,'mn2t',filenameVar='MN2T')
calias("erai",'mrro'   ,'ro'  ,filenameVar='RO')
calias("erai",'rsscs'  ,'ssrc',filenameVar='SSRC')
calias("erai",'rlscs'  ,'strc',filenameVar='STRC')
calias("erai",'pr','tp',filenameVar='TP')
#derive("erai",'pr','add','prl','prc')

# Some additional daily fields
calias("erai",'v850'   ,'v850',filenameVar='V850')
calias("erai",'u850'   ,'u850',filenameVar='U850')
calias("erai",'v200'   ,'v200',filenameVar='V200')
calias("erai",'u200'   ,'u200',filenameVar='U200')

# To do : either read specific files for hurs and huss or provide a CliMAF operator
