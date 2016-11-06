import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import grads
from netCDF4 import Dataset
from pylab import title, savefig

file = '/home/jota/meteo-only/dataout/POSPROCESS/METEO-ONLY-A-2016-10-23-010000-g1.ctl'

#ga = grads.GaNum(Bin='grads',Echo=False,Window=False)
ga = grads.GrADS(Window=False)
fh = ga.open(file)
tempk = ga.expr('tempk')
temp = tempk - 273.15
ga.contour(temp)
title('Temperatura')
savefig('fig.png')



#vars = ['tempk','rh','lon','lat']
#
#tempk = ga.expr('tempk')
#rh = ga.expr('rh')
#lon = ga.expr('lon')
#lat = ga.expr('lat')
#temperatura = []
#latitude = []
#longitude = []
#
#print fh




#print "Tempk:\n{}".format(tempk)
#for temp in tempk[28]:
#    temperatura.append(float(temp))
#
##print "Lat:\n{}".format(lat)
#for l in lat[28]:
#    latitude.append(float(l))
#
#
#for lg in lon[28]:
#    longitude.append(float(lg))
#
#
#
#
#map = Basemap(projection='merc', lat_0=-22.846902, lon_0=-45.231665,
#        resolution='l', lat_ts=20)
#        #area_thresh=1000.0)
#        #llcrnrlon=-50.7238, llcrnrlat=-25.3241,
#        #urcrnrlon=-39.91333, urcrnrlat=-20.35492)
#
#
#map.drawcoastlines()
#map.drawcountries()
#map.fillcontinents(color='coral', lake_color='aqua')
#map.drawmapboundary(fill_color='aqua')
#
#
#map.drawmeridians(np.arange(0,360,30), labels=[True, False, False, True])
#map.drawparallels(np.arange(-90,90,30), labels=[False, True, True, False])
#
#plt.title(fh.title + ', SP - Temperatura')
#x, y = map(longitude, latitude)
#map.plot(x,y,'bo', markersize=5)
#sc = plt.scatter(x, y,c=temperatura)
#cbar = plt.colorbar(sc, shrink=.5)
#cbar.set_label('temp')
#plt.show()
