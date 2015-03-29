# example for 
#  1- defining a dataset restricted to a lat-lon box
#  2- applying a further, explicit extraction of a sub box

from climaf.api import *
clog(logging.DEBUG)

cdef("frequency","monthly")
dataloc(experiment="AMIPV6ALB2G", organization="example",url=[cpath+"/../examples/data/AMIPV6ALB2G"])

dg=ds(experiment="AMIPV6ALB2G", variable="tas", period="1980-1981", domain=[10,80,-50,40])
cshow(ncview(dg))
	
de=llbox(dg, latmin=30, latmax=60, lonmin=-30, lonmax=30)
cshow(ncview(de))

# How to use names rather than latmin/latmax/lonmin/lonmax
box=dict()
box["nino28"]=[-150,-130,-5,5]
dg_nino28=ds(experiment="AMIPV6ALB2G", variable="tas", period="1980-1981", domain=box["nino28"])

