# This a short script where I produced a few plots based on spatial data
#
# Created by Daniel Díez Alonso, all rights reserved.
# Shared only for recruitment purposes. Please, do not circulate for any other purposes.

setwd("C:/Users/username/OneDrive/Niger DFF/data_analysis")

# Load the raster package
library(tidyr)
library(sf)
library(ggplot2)
library(raster)
library(dplyr)

# Set options for the sf package
options("sf_use_s2" = TRUE)
options("sf_parallel_handling" = "st")

# Read the .tif file as a raster object
pop_density_layer <- raster("ner_popdensity_gen_2020.tif")
  # download.file("https://data.humdata.org/dataset/ab6939a8-2546-48db-836e-644150628a2d/resource/d1d523fb-acfe-477a-bae0-6ab4d66b5734/download/ner_general_2020_geotiff.zip",destfile = 'popden.zip')
    # unzip(zipfile='popden', exdir='popden')

# Read the file containing population density values
pop_density_values <- read.csv("ner_general_2020.csv")

# Load Niger shape files for different administrative levels
  # download.file("https://data.humdata.org/dataset/c0e0998c-b45a-4aea-ac06-c1de1d94e596/resource/3d941be1-4607-434a-8795-de8f1de51b34/download/ner_adm_ignn_20230720_ab_shp.zip",destfile = 'shapefiles.zip')
    # unzip(zipfile='shapefiles', exdir='Niger_shapefiles')
niger_admin3 <- st_read("Niger_shapefiles/NER_admbnda_adm3_IGNN_20230720.shp")
niger_districts <- st_read("Niger_shapefiles/NER_admbnda_adm2_IGNN_20230720.shp")
niger_regions <- st_read("Niger_shapefiles/NER_admbnda_adm1_IGNN_20230720.shp")   # Instead of using shapefile("")

# Signal Tahoua region separately:
  tahoua_polygon <- filter(niger_districts, ADM2_FR =="Tahoua")
  tahouaville_polygon <- filter(niger_districts, ADM2_FR=="Ville de Tahoua")

# Perform a spatial join and calculate the average value for each polygon
pop_density_sf <- st_as_sf(pop_density_values,coords = c("longitude","latitude"), crs = st_crs(niger_admin3))
joined_data <- st_join(niger_admin3, pop_density_sf, join=st_within) %>%
  group_by(AMD3_PCODE) %>%
  summarise(avg_density = mean(ner_general_2020,na.rm = TRUE), total_points=n())

# Merge the average values back into the shapefile
niger_shapefile <- merge(niger_admin3,avg_density,by.x="AMD3_PCODE", by.y="AMD3_PCODE")


# Plot regional map showing the smaller units
ggplot() + geom_sf(data=niger_shapefile, aes(fill=avg_density)) +
  scale_fill_gradient(low="lightblue", high="darkblue") +
  geom_sf(data=niger_regions,fill=NA, colour="red", lwd=1) + theme_minimal()

ggplot() + geom_sf(data=niger_districts) +
  geom_sf(data=niger_regions,fill=NA, colour="red", lwd=1) +
  geom_sf(data = tahoua_polygon, fill="green") +
  geom_sf(data = tahouaville_polygon, fill="darkgreen") + theme_minimal()


