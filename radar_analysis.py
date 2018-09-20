# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 10:23:04 2018

@author: s1326314
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 10:03:20 2018

@author: imcnicol
"""

## Load necessary libraries

from osgeo import gdal, gdal_array
import numpy as np
import glob
import os, os.path
import math
import osgeo.ogr
import csv

# Where is your data?
dirpath = '/home/s1326314/RBGdata'

# get radar image
gRed = gdal.Open(dirpath + '/PALSAR/N03E016_17_MOS_F02DAR/N03E016_17_sl_HV_F02DAR') 

""" Crop shapefiles """
shapefiles_merg = sorted( glob.glob(dirpath + '/shpfiles_merged/*.shp'))

output=[]
for shp in shapefiles_merg:
    base=os.path.splitext(os.path.basename(shp))[0].replace(' ', '_')
    crop_fname = dirpath + '/temp.tif'
    os.system('gdalwarp -overwrite -cutline ' + shp.replace(' ', '\ ') + ' -crop_to_cutline ' + filename  + ' ' + crop_fname)
    g =gdal.Open(crop_fname)    
    data = gdal_array.DatasetReadAsArray(g)
    mean = np.mean(data)
    std = np.std(data)
    output.append([base,mean,std]) #for each plot, save label, mean, std
print(output)

#export to csv    
with open(dirpath + '/stats_radar_merged.csv', "w") as myfile:
    writer = csv.writer(myfile, lineterminator='\n')
    writer.writerow(('Plot','Mean','Std'))
    writer.writerows(output)
myfile.close()