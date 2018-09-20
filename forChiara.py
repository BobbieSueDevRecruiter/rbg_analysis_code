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



## This should be defined before first use to avoid error appearing
def createGeoTIFF(filename, g, orig_array_shape, new_array, data_type=gdal.GDT_Float32, noData = '', overwrite = 'no'):
    """
    Create a GeoTiff file from an array.
    Input args:
    fname (str): filename for exported dataset
    g (gdal dataset object): gdal object (from gdal.Open(...) )
    orig_array_shape (numpy array): result frm shape(). from which the new array's shape will be based on
    new_array (numpy array): numpy array to export as GeoTiff
    dtype (string): data type for the output - defaults to GDT_Float32
    """  
    if isinstance(g, gdal.Dataset)==False:
         print ("createGeoTiff: g is not of type 'gdal.Dataset'. Skipping.")
         return    
    if os.path.exists(filename) and overwrite != 'yes':
        print ("createGeoTIFF file exists and overwrite is not 'yes'. Skipping.")
        print ('createGeoTIFF:' + filename)
        return
    # Create GeoTiff  
    (X, deltaX, rotation, Y, rotation, deltaY) = g.GetGeoTransform()
    srs_wkt = g.GetProjection()
    driver = gdal.GetDriverByName("GTiff")
    # Create old array shape
    Nx = orig_array_shape[-2]
    Ny = orig_array_shape[-1]
    dataset = driver.Create(filename, Ny, Nx, 1, data_type) #GDT_Byte for int # CR instead of data_type this used to read gdal.GDT_Float32
    dataset.SetGeoTransform((X, deltaX, rotation, Y, rotation, deltaY))
    dataset.SetProjection(srs_wkt)
    if noData == '':
        noData = dataset.GetRasterBand(1).GetNoDataValue()
    else:
        dataset.GetRasterBand(1).SetNoDataValue(noData)
    dataset.GetRasterBand(1).WriteArray(new_array)
    dataset = None
    print ('..Exported')


# Where is your data?
dirpath = '/home/s1326314/RBGdata'

# Find Red and NIR bands
landsat_bands = sorted( glob.glob(dirpath + '/LandSat/LC08_L1TP_182058_20180523_20180605_01_T1.tar/*.TIF'))
bands = [x for x in landsat_bands if "B4" in x or "B5" in x] # "List comprehension
# Load the red band to get spatial information
gRed = gdal.Open(bands[0]) 

# Get the spatial information for the image
(x_min, pixel_width, rotation, y_max, rotation, pixel_height) = gRed.GetGeoTransform()
x_max = x_min + pixel_width * gRed.RasterXSize
y_min = y_max + pixel_height * gRed.RasterYSize

# Stack the band as a vrt
vrt_name = dirpath + '/temp_vrt.vrt'        
os.system('gdalbuildvrt -q -srcnodata "0" -vrtnodata "0" -separate -te ' + str(x_min) + ' ' + str(y_min) + ' ' + str(x_max) + ' ' + str(y_max) + ' ' +  vrt_name + ' ' + ' ' .join(bands)) 
g = gdal.Open(vrt_name)
data = gdal_array.DatasetReadAsArray(g)
os.remove(vrt_name)

"""
Extract gain and offset values for converting DN to radiance, and then convert to reflectance
https://yceo.yale.edu/how-convert-landsat-dns-top-atmosphere-toa-reflectance
"""
metaPath = glob.glob(dirpath + '/LandSat/LC08_L1TP_182058_20180523_20180605_01_T1.tar/*MTL.txt')[0]
metadata = open(metaPath, 'r') # Read in the metadata
gain= []; 
offset = []; 
band_name = []; count = 1
for line in metadata:
    print (line)
    if ( line.find ("RADIANCE_MULT_BAND") >= 0 ):
        s = float(line.split("=")[-1])               
        band_name.append(count); count = count+1
        gain.append(s)
    if ( line.find ("RADIANCE_ADD_BAND") >= 0 ):
        t = float(line.split("=")[-1])               
        offset.append(t)
    if ( line.find ("EARTH_SUN_DISTANCE") >= 0 ):
        sun_dist = float(line.split("=")[-1])               
    if ( line.find ("SUN_ELEVATION") >= 0 ):
        sun_elev = float(line.split("=")[-1])               
        solar_zenith = 90 - sun_elev        
metadata.close(); metadata = None       


""" Convert DN to TOA Reflectance """
red_TOA = (math.pi * ( gain[3] * data[0,:,:] + offset[3] ) * (sun_dist**2) ) / float((1551 *math.cos(math.radians(solar_zenith)) ))
nir_TOA = (math.pi * ( gain[4] * data[1,:,:] + offset[4] ) * (sun_dist**2) ) / float((1036 *math.cos(math.radians(solar_zenith))))
""" Calculate NDVI """
ndvi_data = np.where( (data[0,:,:]>0) | (data[1,:,:] >0), ((nir_TOA - red_TOA) /  (nir_TOA + red_TOA) ), -32768) 
ndvi_data = np.where( (ndvi_data >1) | ((ndvi_data < 0) & (ndvi_data != -32768)), 0, ndvi_data) # Recode negative


filename = '/home/s1326314/RBGdata/NDVI.tif' 
createGeoTIFF(filename, gRed, np.shape(data[0,:,:]),ndvi_data,noData = -32768, overwrite = 'yes')


""" Crop shapefiles """
shapefiles = sorted( glob.glob(dirpath + '/shpfiles_poly_proj/projected/*.shp')
#shapefiles_merg = sorted( glob.glob(dirpath + '/shpfiles_merged/*.shp'))

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
with open(dirpath + '/stats.csv', "w") as myfile:
    writer = csv.writer(myfile, lineterminator='\n')
    writer.writerow(('Plot','Mean','Std'))
    writer.writerows(output)
myfile.close()
    
    
    
    
    
    




