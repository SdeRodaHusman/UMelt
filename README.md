# UMelt

## Author
**Sophie de Roda Husman** 

PhD candidate at Geoscience and Remote Sensing, Delft University of Technology

* 📧: S.deRodaHusman@tudelft.nl
* 🐦: https://twitter.com/SdeRodaHusman
* 🐱: https://www.tiktok.com/@zuidpool_sophie


## Overview
This repository provides material used for the paper: XXXXX. The paper offers an elaborate exposition of the model development. 

Within this GitHub repository, you will find the following components:

**1. Data** :bar_chart:

The repository includes the UMelt record, which can be accessed through Google Earth Engine as assets or as GeoTIFFs via 4TU.ResearchData. Additionally, a set of simple scripts are provided to aid in the retrieval of the data. The UMelt record is available in two formats: either as a twice-daily resolution or as one product per season, representing the summer melt occurrence.

**2. Scripts** :page_with_curl:

These scripts were instrumental in the creation of the UMelt model. The folder contains four scripts that were used to create the UMelt model. _Script 1_ preprocesses the training, validation, and testing data and exports it as TensorFlow record format in a Google Cloud Bucket. _Script 2_ develops and trains the U-Net model. _Script 3_ enables the deployment of the trained TensorFlow model in Google Earth Engine. _Script 4_ generates UMelt predictions using the trained U-Net model. These scripts collectively provide the necessary functionality for data preprocessing, model development, deployment, and prediction generation in the UMelt model pipeline.

**3. Figures** :milky_way:

This repository includes all the figures featured in the paper, including both the main figures and the supplementary figures.



