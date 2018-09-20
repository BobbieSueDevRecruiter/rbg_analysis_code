### Playing with shapefiles

library(raster)
library(sp)
library(rgdal)

dirpath = '/home/s1326314/RBGdata'
shapefiles = list.files(paste0(dirpath, "/shpfiles"),pattern = "bt_15_utm_esri.shp",full.names = TRUE)

# Open layer (e.g. raster) with coordiante system you want to convert to
temp = raster('/home/s1326314/RBGdata/LandSat/LC08_L1TP_182058_20180523_20180605_01_T1.tar/LC08_L1TP_182058_20180523_20180605_01_T1_B10.TIF')
newProj = as.character(crs(temp))

for (i in 1:length(shapefiles) ) {  
  shp = shapefiles[i] # Get shapefile path
  print(shp)
  # sp::spTransform()  #  [package]::[function in said pacakge] - not neecessary, but good form and needed if function name is common to multiple packages
  toProject =  shapefile(shp) # First load the shapefile
  newShp = sp::spTransform(toProject , newProj ) # the project it
  # Export the shapefile to a new folder called "projected" in your shapefile folder
  writeOGR(newShp, paste0( dirname(shp), "/projected/",basename(shp)), layer = basename(shp), driver = "ESRI Shapefile", overwrite_layer = TRUE )
}

#convert lines to polygons
  
    

