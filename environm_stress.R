### Calculate environmental stress variable for a list of coordinates
### as in http://chave.ups-tlse.fr/pantropical_allometry.htm

library(raster)
library(ncdf4)

#get raster data
source("http://chave.ups-tlse.fr/pantropical_allometry/readlayers.r")
retrieve_raster(raster,coord,plot=FALSE,format="nc")

dirpath = '/home/s1326314/rbg_analysis/processed_data/site1_process/'

#import csv file
tree_coord <- read.csv(paste0(dirpath, "/lat_long.csv"))

#loop over lat and long data to get coordinates for each tree
for(tree in tree_coord) {
  lat = tree_coord[c("Lat")]
  long = tree_coord[c("Long")]
  coord=cbind(long,lat) 
}
#retrieve raster for E 
environm_stress <- retrieve_raster("E",coord)

#save output to file
write.csv(environm_stress, file=(paste0(dirpath, "/E_forall.csv")))

