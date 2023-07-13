# Overview

The UMelt records offer surface melt information for the entire Antarctic region, covering the melt seasons from 2016 to 2021. 
The data is available at a temporal resolution of twice-daily intervals (i.e., 6 AM and 6 PM) and a spatial resolution of 500 meters. 
Additionally, we provide the 'summer melt occurrence' metric, which represents the percentage of the UMelt record indicating melt during a specific melt season (November to March).

To access the data, you have two options:

- Download the data as GeoTIFFs files from 4TU.ResearchData.
- Import the data as assets directly into Google Earth Engine.

**1. Download GeoTIFFs**

You can download the GeoTIFFs from 4TU.ResearchData via [this link](https://data.4tu.nl/datasets/8a8934ef-9407-406f-8bfb-573eb182ec54/1).

**2. Download Google Earth Engine assets**

The UMelt record can be imported into Google Earth Engine per melt season, the individual predictions (per 12 hours) are stored as bands:

- Melt season 2016-2017: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason1617/UMelt_AllData_MeltSeason1617')```
- Melt season 2017-2018: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason1718/UMelt_AllData_MeltSeason1718')```
- Melt season 2018-2019: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason1819/UMelt_AllData_MeltSeason1819')```
- Melt season 2019-2020: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason1920/UMelt_AllData_MeltSeason1920')```
- Melt season 2020-2021: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason2021/UMelt_AllData_MeltSeason2021')```
    
Also, a 'summer melt occurrence' image per image for each melt season can be imported: 
- Melt season 2016-2017: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason1617/UMelt_MeltFraction_MeltSeason1617')```
- Melt season 2017-2018: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason1718/UMelt_MeltFraction_MeltSeason1718')```
- Melt season 2018-2019: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason1819/UMelt_MeltFraction_MeltSeason1819')```
- Melt season 2019-2020: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason1920/UMelt_MeltFraction_MeltSeason1920')```
- Melt season 2020-2021: ```ee.Image('projects/phd-detectionsurfacemelt/assets/UMelt_Antarctica/MeltSeason2021/UMelt_MeltFraction_MeltSeason2021')```

Included in this folder is a Google Earth Engine script that demonstrates the process of importing the UMelt assets into Google Earth Engine. 
