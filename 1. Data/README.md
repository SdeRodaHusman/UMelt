# Overview

The UMelt records offer surface melt information for the entire Antarctic region, covering the melt seasons from 2016 to 2021. 
The data is available at a temporal resolution of twice-daily intervals (i.e., 6 AM and 6 PM) and a spatial resolution of 500 meters. 
Additionally, we provide the 'summer melt occurrence' metric, which represents the percentage of the UMelt record indicating melt during a specific melt season (November to March).

To access the data, you have two options:

- Download the data as NetCDF files from 4TU.ResearchData.
- Import the data as assets directly into Google Earth Engine.

**1. Download NetCDFs**

You can download the NetCDFs from 4TU.ResearchData via [this link](xxxx).

**2. Download Google Earth Engine assets**

The UMelt record can be imported into Google Earth Engine per melt season:

- Melt season 2016-2017: ```ee.ImageCollection('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason1617/UMelt_AllData_MeltSeason1617')```
