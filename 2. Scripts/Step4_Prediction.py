
#############################################################################
# General information
#############################################################################

# This scripts allows to make predictions with the trained U-Net model. 
# The current scripts is used to make predictions for melt season 2016-2017 on the Shackleton Ice Shelf.
# However the POI (period of interest) and ROI (region of interest) can be adapted if needed.

# Scripts for Step 1 (preproccesing), Step 2 (training U-Net), and Step 3 (employ U-Net) were made in Google Colab.
# Running the predictions was done in Spyder, because the run time takes some time, and Google Colab would sometimes disconnect.

# Any questions? Happy to hear! You can reach me at S.deRodaHusman@tudelft.nl

#############################################################################
# Initialize GEE
#############################################################################


import ee
ee.Initialize()


#############################################################################
# Set variables
#############################################################################

# Specify variables regarding observation time of the satellite imagery, 
# thresholds for melt detection and additional parameters requiered for the CNN model preparation.

# Select period of interest 
start_poi = ee.Date('2016-12-22')
end_poi = ee.Date('2017-04-01')

# Period of interest for Sentinel-1 monthly average
start_clim = ee.Date('2016-01-01')
end_clim = ee.Date('2021-04-01')

# Winter months
winter_start = 6
winter_end = 8

# Thresholds
threshold_s0_dB = 3
threshold_s0_float = ee.Number(10).pow(ee.Number(-3).multiply(0.1))
threshold_Tb_K = 30

# Additional parameters
scale_spatialres = 500
crs_3031 = 'epsg:3031'
kernel_size = 64

# Select region of interest (for example: Shackleton Ice Shelf, or one of the four regions on Shackleton Ice Shelf)
Shackleton = ee.Geometry.Polygon(
        [[[93.7864621358891, -64.79842784125249],
          [93.7864621358891, -67.0125458953563],
          [105.7615597921391, -67.0125458953563],
          [105.7615597921391, -64.79842784125249]]])

R1 = ee.FeatureCollection("users/sophiederoda/UNet_SpatialPredictiveAnalyses/Region1_clipped").geometry()
R2 = ee.FeatureCollection("users/sophiederoda/UNet_SpatialPredictiveAnalyses/Region2_clipped").geometry()
R3 = ee.FeatureCollection("users/sophiederoda/UNet_SpatialPredictiveAnalyses/Region3_clipped").geometry()
R4 = ee.FeatureCollection("users/sophiederoda/UNet_SpatialPredictiveAnalyses/Region4_clipped").geometry()

ROI = Shackleton

#############################################################################
# Prepare satellite data
#############################################################################
# The input features are preprocessed.

# Import ctive and passive microwave data
S1_collection = ee.ImageCollection("COPERNICUS/S1_GRD_FLOAT")

ascat_collection_1 = ee.ImageCollection("users/aardmapp/Antarctica/ascat")
ascat_collection_2 = ee.ImageCollection("users/sderodahusman2/ascat")

SSMIS_2016 = ee.ImageCollection("users/sderodahusman/SSMIS_F17_19H_2016")
SSMIS_2017 = ee.ImageCollection("users/sderodahusman/SSMIS_F17_19H_2017")

# Import REMA mosaic (for elevation input)
REMA = ee.Image("users/sophiederoda/GeneralAntarcticData/REMA_200m_dem_filled").rename('elevation')
REMA = REMA.reproject(**{'crs': crs_3031, 'scale': scale_spatialres})

# Reproject DEM 
DEM = REMA.reproject(**{'crs': crs_3031, 'scale': scale_spatialres})



#############################################################################
# Sentinel-1: preprocessing
#############################################################################

# Fuction to add local overpass time time to properties 
def localTime(img):
    geometry_centr = ee.Feature(img.geometry()).centroid()
    centroidInfo = img.int().reduceToVectors(**{'geometry': geometry_centr.geometry(), 'scale': 10, 'maxPixels': 1e10, 'geometryType': "centroid", 'tileScale': 16})
    lon = centroidInfo.geometry().coordinates().get(0)
    localtime = img.date().advance(ee.Number(lon).divide(15), 'hour')
    localtime_millis = ee.Date(localtime).millis()
    return img.set('LocalTime',localtime_millis)

# Function to compute area of footprint (to later remove areas having a footprint < 100 km2, 
# since these are 'slice' images that give errors when computing coordinates in 'localTime' function)
def areaFootprint(img):
    area = img.geometry().area().divide(1000 * 1000)
    return img.set('area', area)

# Remove border noise (clip outer 500 m of each image)
def removeBorderNoise(img):
    return img.clip(img.geometry().buffer(-2000))

# Preprocessed Sentinel-1 image collection
S1 = S1_collection \
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'HH')) \
    .select('HH') \
    .filterDate(start_clim, end_clim) \
    .filterBounds(ROI) \
    .map(localTime) \
    .map(areaFootprint) \
    .filterMetadata('area','greater_than', 100) \
    .map(removeBorderNoise)


#############################################################################
# Sentinel-1: melt computation
#############################################################################

S1_base = S1

# Select winter months for each year of interest
S1_2017_winter = S1_base.filterDate('2016-06-01', '2016-08-31')
S1_2018_winter = S1_base.filterDate('2017-06-01', '2017-08-31')
S1_2019_winter = S1_base.filterDate('2018-06-01', '2018-08-31')
S1_2020_winter = S1_base.filterDate('2019-06-01', '2019-08-31')
S1_2021_winter = S1_base.filterDate('2020-06-01', '2020-08-31')

# Extract available orbits (in winter months)
S1_2017_orbits = ee.Dictionary(S1_2017_winter.aggregate_histogram('relativeOrbitNumber_start')).keys()
S1_2018_orbits = ee.Dictionary(S1_2018_winter.aggregate_histogram('relativeOrbitNumber_start')).keys()
S1_2019_orbits = ee.Dictionary(S1_2019_winter.aggregate_histogram('relativeOrbitNumber_start')).keys()
S1_2020_orbits = ee.Dictionary(S1_2020_winter.aggregate_histogram('relativeOrbitNumber_start')).keys()
S1_2021_orbits = ee.Dictionary(S1_2021_winter.aggregate_histogram('relativeOrbitNumber_start')).keys()

# Melt years (defined from April-1 year N - March-31 year N+1)
S1_2017_year = S1_base.filterDate('2016-04-01', '2017-03-31')
S1_2018_year = S1_base.filterDate('2017-04-01', '2018-03-31')
S1_2019_year = S1_base.filterDate('2018-04-01', '2019-03-31')
S1_2020_year = S1_base.filterDate('2019-04-01', '2020-03-31')
S1_2021_year = S1_base.filterDate('2020-04-01', '2021-03-31')

# Functions for melt computations, per year and per orbit
def meltComputationS1_2017(orbit): #yearOfInterest
    S1_m = S1_2017_year.filter(ee.Filter.eq('relativeOrbitNumber_start', ee.Number.parse(orbit).toInt()))
    S1_w = S1_m.filter(ee.Filter.calendarRange(winter_start,winter_end,'month')).mean().min(ee.Image(5));
    S1_c = S1_m.map(lambda img: img.addBands(img.lt(S1_w.multiply(threshold_s0_float)).toFloat().rename('melt')))
    return S1_c.toList(S1_c.size())

S1_2017_melt = ee.ImageCollection.fromImages(S1_2017_orbits.map(meltComputationS1_2017).flatten()).select('melt')

def meltComputationS1_2018(orbit): #yearOfInterest
    S1_m = S1_2018_year.filter(ee.Filter.eq('relativeOrbitNumber_start', ee.Number.parse(orbit).toInt()))
    S1_w = S1_m.filter(ee.Filter.calendarRange(winter_start,winter_end,'month')).mean().min(ee.Image(5));
    S1_c = S1_m.map(lambda img: img.addBands(img.lt(S1_w.multiply(threshold_s0_float)).toFloat().rename('melt')))
    return S1_c.toList(S1_c.size())

S1_2018_melt = ee.ImageCollection.fromImages(S1_2018_orbits.map(meltComputationS1_2018).flatten()).select('melt')

def meltComputationS1_2019(orbit): #yearOfInterest
    S1_m = S1_2019_year.filter(ee.Filter.eq('relativeOrbitNumber_start', ee.Number.parse(orbit).toInt()))
    S1_w = S1_m.filter(ee.Filter.calendarRange(winter_start,winter_end,'month')).mean().min(ee.Image(5));
    S1_c = S1_m.map(lambda img: img.addBands(img.lt(S1_w.multiply(threshold_s0_float)).toFloat().rename('melt')))
    return S1_c.toList(S1_c.size())

S1_2019_melt = ee.ImageCollection.fromImages(S1_2019_orbits.map(meltComputationS1_2019).flatten()).select('melt')

def meltComputationS1_2020(orbit): #yearOfInterest
    S1_m = S1_2020_year.filter(ee.Filter.eq('relativeOrbitNumber_start', ee.Number.parse(orbit).toInt()))
    S1_w = S1_m.filter(ee.Filter.calendarRange(winter_start,winter_end,'month')).mean().min(ee.Image(5));
    S1_c = S1_m.map(lambda img: img.addBands(img.lt(S1_w.multiply(threshold_s0_float)).toFloat().rename('melt')))
    return S1_c.toList(S1_c.size())

S1_2020_melt = ee.ImageCollection.fromImages(S1_2020_orbits.map(meltComputationS1_2020).flatten()).select('melt')

def meltComputationS1_2021(orbit): #yearOfInterest
    S1_m = S1_2021_year.filter(ee.Filter.eq('relativeOrbitNumber_start', ee.Number.parse(orbit).toInt()))
    S1_w = S1_m.filter(ee.Filter.calendarRange(winter_start,winter_end,'month')).mean().min(ee.Image(5));
    S1_c = S1_m.map(lambda img: img.addBands(img.lt(S1_w.multiply(threshold_s0_float)).toFloat().rename('melt')))
    return S1_c.toList(S1_c.size())

S1_2021_melt = ee.ImageCollection.fromImages(S1_2021_orbits.map(meltComputationS1_2021).flatten()).select('melt')

# Merge all files
S1_melt = S1_2017_melt \
          .merge(S1_2018_melt) \
          .merge(S1_2019_melt) \
          .merge(S1_2020_melt) \
          .merge(S1_2021_melt)
                
S1_melt = S1_melt.select('melt')

# Only select dates in which melt is expected (Nov - March, Antarctic summer months)
S1_melt = S1_melt.filter(ee.Filter.calendarRange(11, 3 ,'month'))

#############################################################################
# Sentinel-1: reprojection
#############################################################################

# Reduce Sentinel-1 resoltuion to 1 km and reproject to EPGS:3031.
def reduceResolutionS1(feature):
  return feature.reproject(**{'crs': crs_3031, 'scale': scale_spatialres}).toInt();  
S1_melt = S1_melt.map(reduceResolutionS1)


#############################################################################
# ASCAT: preprocessing
#############################################################################

# Add date field (format: YMD)
def addDate(img):
  return img.set('DateYMD',ee.Date(img.get('system:time_start')).format("yyyy-MM-dd-hh-mm"))

# Normalize the 8-bit images (from -32 to 0 dB) 
def normalizeAscatRaw(img):
    scaledImage = img.multiply(32.0/255.0).subtract(32)
    return scaledImage.double().copyProperties(img, ["system:time_start", "hour"])

# Transfer dB values to float(10^(x*0.1))
def dBtoFloat(img): 
    floatImage = ee.Image(10).pow(img.multiply(0.1))
    return floatImage.copyProperties(img, ["system:time_start", "hour"])

# Preprocessed ASCAT image collection
ascat = ascat_collection_1.merge(ascat_collection_2) \
                                .map(normalizeAscatRaw) \
                                .map(dBtoFloat) 



# Start and end dates that are used for interpolation of ASCAT data
startDate_morning_ascat = ee.Date('2016-01-01T06:00')
endDate_morning_ascat = ee.Date('2017-04-01T06:00')
startDate_evening_ascat = ee.Date('2016-01-01T18:00')
endDate_evening_ascat =  ee.Date('2017-04-01T18:00')

# Merge ASCAT morning and evening image collections
ascat_morning = ascat \
            .sort('system:time_start') \
            .filterDate(startDate_morning_ascat, endDate_morning_ascat) \
            .filterMetadata('hour','equals',6)

ascat_evening = ascat \
            .sort('system:time_start') \
            .filterDate(startDate_evening_ascat, endDate_evening_ascat) \
            .filterMetadata('hour','equals',18)

# Rename band
def renameBand(img):
  return img.rename('sigma0')

ascat_morning = ascat_morning.map(renameBand)
ascat_evening = ascat_evening.map(renameBand)


# Create list of missing dates on alternate dates
missingDates_morning = ee.List.sequence(startDate_morning_ascat.advance(1, 'days').millis(), endDate_morning_ascat.millis(), 2*24*60*60*1000)
missingDates_evening = ee.List.sequence(startDate_evening_ascat.advance(1, 'days').millis(), endDate_evening_ascat.millis(), 2*24*60*60*1000)

def DateToMillis(dateMillis):
  return ee.Date(dateMillis)

missingDates_morning = missingDates_morning.map(DateToMillis)
missingDates_evening = missingDates_evening.map(DateToMillis)

n_morning = missingDates_morning.size().getInfo()
n_evening = missingDates_evening.size().getInfo()

list_morning = ee.List.sequence(0, n_morning-2)
list_evening = ee.List.sequence(0, n_evening-2)

def maskedImageCol_morning(i):
  return ee.Image(0).selfMask() \
      .rename('sigma0') \
      .set('system:time_start',ee.Date(missingDates_morning.get(i)).millis()) \
      
def maskedImageCol_evening(i):
  return ee.Image(0).selfMask() \
      .rename('sigma0') \
      .set('system:time_start',ee.Date(missingDates_evening.get(i)).millis()) \
      
emptyCol_morning = list_morning.map(maskedImageCol_morning)
emptyCol_evening = list_evening.map(maskedImageCol_evening)

emptyCol_morning = ee.ImageCollection(emptyCol_morning)
emptyCol_evening = ee.ImageCollection(emptyCol_evening)

# Peform temporal interpolation
mergedCol_morning = ascat_morning.merge(emptyCol_morning)
mergedCol_evening = ascat_evening.merge(emptyCol_evening)

# Add date field (format: YMD)
def addDateYMD(i):
  return i.set('DateYMD',ee.Date(i.get('system:time_start')).format("yyyy-MM-dd-kk")).rename('sigma0')

mergedCol_morning = mergedCol_morning.map(addDateYMD).sort('DateYMD')
mergedCol_evening = mergedCol_evening.map(addDateYMD).sort('DateYMD')

# Replace masked pixels by the mean of the previous and next days
def temporalInterpolation_morning(image):
  currentDate = ee.Date(image.get('system:time_start'))
  interpolatedImage = mergedCol_morning.filterDate(currentDate.advance(-2, 'days'), currentDate.advance(2, 'days')).mean()
  return interpolatedImage.where(image, image).copyProperties(image, ['system:time_start', 'DateYMD'])

def temporalInterpolation_evening(image):
  currentDate = ee.Date(image.get('system:time_start'))
  interpolatedImage = mergedCol_evening.filterDate(currentDate.advance(-2, 'days'), currentDate.advance(2, 'days')).mean()
  return interpolatedImage.where(image, image).copyProperties(image, ['system:time_start', 'DateYMD'])

ascat_morning_all = mergedCol_morning.map(temporalInterpolation_morning)
ascat_evening_all = mergedCol_evening.map(temporalInterpolation_evening)

ascat_tempint = ascat_morning_all.merge(ascat_evening_all)


#############################################################################
# ASCAT: interpolation and continuous melt computation
#############################################################################

# Compute winter mean per year
ascat_2016_winter = ascat_tempint.filterDate('2016-06-01', '2016-08-31').mean()

# Melt years (defined from April-1 year N - March-31 year N+1)
ascat_2016_year = ascat_tempint.filterDate('2016-04-01', '2017-03-31')


# Functions for melt computations, per year 
def meltComputationAscat_2016(img): 
  return img.addBands(img.subtract(ascat_2016_winter).toFloat().rename(['melt'])).copyProperties(img, ["system:time_start"])
ascat_2016_melt = ascat_2016_year.map(meltComputationAscat_2016)


# Merge all files
ascat_melt = ascat_2016_melt

ascat_melt = ascat_melt.select('melt')

# Only select dates in which melt is expected (Nov - March, Antarctic summer months)
ascat_melt = ascat_melt.filter(ee.Filter.calendarRange(11, 3 ,'month'))


ascat_melt = ascat_melt.map(addDate)
        
#############################################################################
# ASCAT: normalization
#############################################################################

ascat_melt_min = -0.93
ascat_melt_max = 0.38

# Normalize each ASCAT image based on minumum and maximum values
def normalizeASCAT(img):
  return img.unitScale(ascat_melt_min, ascat_melt_max).copyProperties(img, ["system:time_start"])

ascat_melt = ascat_melt.map(normalizeASCAT)

#############################################################################
# ASCAT: reprojection
#############################################################################"    
        
# Rescale ASCAT at same resolution and projection as Sentinel-1.
def reduceResolutionAscat(feature):
  return feature.reproject(**{'crs': crs_3031, 'scale': scale_spatialres});  

ascat_melt = ascat_melt.map(reduceResolutionAscat)

#############################################################################
# SSMIS: preprocessing
#############################################################################

# Merge SSMIS images
SSMIS = SSMIS_2016 \
        .merge(SSMIS_2017) \

 
SSMIS = SSMIS.select('b1')

# Convert Brightness Temperature to Kelvin (scale factor: 0.01)
def scaleSSMIS(img):
    scaledImage = img.divide(100);
    return scaledImage.double().copyProperties(img, ["system:time_start"]).copyProperties(img, ["overpass"])

SSMIS = SSMIS.map(scaleSSMIS) 


#############################################################################
# SSMIS: continuous melt computation
#############################################################################


# Compute winter mean per year
SSMIS_2016_winter = SSMIS.filterDate('2016-06-01', '2016-08-31').mean()

# Melt years (defined from April-1 year N - March-31 year N+1)
SSMIS_2016_year = SSMIS.filterDate('2016-04-01', '2017-03-31')


# Functions for melt computations, per year 
def meltComputationSSMIS_2016(img): 
    return img.addBands(img.subtract(SSMIS_2016_winter).toFloat().rename(['melt'])).copyProperties(img, ["system:time_start"])
SSMIS_2016_melt = SSMIS_2016_year.map(meltComputationSSMIS_2016)

# Merge all files
SSMIS_melt = SSMIS_2016_melt

SSMIS_melt = SSMIS_melt.select('melt')

# Only select dates in which melt is expected (Nov - March, Antarctic summer months)
SSMIS_melt = SSMIS_melt.filter(ee.Filter.calendarRange(11, 3 ,'month'))

#############################################################################
# SSMIS: normalization
#############################################################################

SSMIS_melt_min = -91
SSMIS_melt_max = 84

# Normalize each SSMIS image based on minumum and maximum values
def normalizeSSMIS(img):
  return img.unitScale(SSMIS_melt_min, SSMIS_melt_max).copyProperties(img, ["system:time_start"])

SSMIS_melt = SSMIS_melt.map(normalizeSSMIS)

#############################################################################
# SSMIS: reprojection
#############################################################################


# Rescale SSMIS at same resolution and projection as Sentinel-1.
def reduceResolutionSSMIS(feature):
  return feature.reproject(**{'crs': crs_3031, 'scale': scale_spatialres});  

SSMIS_melt = SSMIS_melt.map(reduceResolutionSSMIS)

#############################################################################
# Combine satellite images
#############################################################################
# Join Sentinel-1, ASCAT, SSMIS

# Rename bands and add LocalTime date field to ASCAT and SSMIS
def renameBandS1(img):
  return img.rename('melt_S1')
S1_melt = S1_melt.map(renameBandS1)

def renameBandAddLocalTimeAscat(img):
  return img.rename('melt_ascat').set('LocalTime',ee.Date(img.get('system:time_start')).millis())
ascat_melt = ascat_melt.map(renameBandAddLocalTimeAscat)

def renameBandAddLocalTimeSSMIS(img):
  return img.rename('melt_SSMIS').set('LocalTime',ee.Date(img.get('system:time_start')).millis())
SSMIS_melt = SSMIS_melt.map(renameBandAddLocalTimeSSMIS)

# Create copy of Sentinel-1 image collection for Sentinel-1 climatology computation in next step
S1_melt_all = S1_melt

# Define a max difference filter to compare timestamps
maxDiffFilter = ee.Filter.maxDifference(**{
  'difference': 2 * 60 * 60 * 1000, # max. 2 hours difference
  'leftField': 'LocalTime',
  'rightField': 'LocalTime'
});

# Define the joins (S1-ASCAT, S1-SSMIS)
saveBestJoin_ascat = ee.Join.saveBest(**{
  'matchKey': 'bestImage_ascat',
  'measureKey': 'timeDiff'});
  
saveBestJoin_SSMIS = ee.Join.saveBest(**{
  'matchKey': 'bestImage_SSMIS',
  'measureKey': 'timeDiff'});

# Apply the join: S1 and ASCAT.
bestJoin_ascat = saveBestJoin_ascat.apply(SSMIS_melt, ascat_melt, maxDiffFilter)
bestJoin_ascat = ee.ImageCollection(bestJoin_ascat)

# Apply the join: S1 and SSMIS.
bestJoin_SSMIS_ascat = saveBestJoin_SSMIS.apply(bestJoin_ascat, SSMIS_melt, maxDiffFilter)
bestJoin_SSMIS_ascat = ee.ImageCollection(bestJoin_SSMIS_ascat)

def getBandAscat(img):
  return img.get('bestImage_ascat')
ascat_melt_match = bestJoin_SSMIS_ascat.map(getBandAscat)

def getBandSSMIS(img):
  return img.get('bestImage_SSMIS')
SSMIS_melt_match = bestJoin_SSMIS_ascat.map(getBandSSMIS)

# Combined image collection: S1, ASCAT and SSMIS
melt_all = ascat_melt_match.combine(SSMIS_melt_match)


#############################################################################
# Sentinel-1 monthly average: preprocessing
#############################################################################

# Create lists of months
months = ee.List.sequence(1, 12);

# Compute Sentinel-1 climatology per month, exclude one year at a time 
def computeS1ClimatologyExcluding2016(m):
    return S1_melt_all.filter(ee.Filter.calendarRange(2016, 2016, 'year').Not()) \
            .filter(ee.Filter.calendarRange(m, m, 'month')) \
            .mean() \
            .rename('melt_S1_climatology') \
            .set('month', m).set('year', 2016)
S1climatology2016 = ee.ImageCollection.fromImages(months.map(computeS1ClimatologyExcluding2016).flatten())

def computeS1ClimatologyExcluding2017(m):
    return S1_melt_all.filter(ee.Filter.calendarRange(2017, 2017, 'year').Not()) \
            .filter(ee.Filter.calendarRange(m, m, 'month')) \
            .mean() \
            .rename('melt_S1_climatology') \
            .set('month', m).set('year', 2017)
S1climatology2017 = ee.ImageCollection.fromImages(months.map(computeS1ClimatologyExcluding2017).flatten())


# Combine all Sentinel-1 climatologies
S1climatology = S1climatology2016.merge(S1climatology2017)

# Add month and year to property
def addMonthToProperties(img):
  return img.set('month_meltAll', ee.Number.parse(ee.Date(img.get('system:time_start')).format("MM")))
def addYearToProperties(img):
  return img.set('year_meltAll', ee.Number.parse(ee.Date(img.get('system:time_start')).format("yyyy")))
melt_all = melt_all \
          .map(addMonthToProperties) \
          .map(addYearToProperties)


#############################################################################
# Sentinel-1 monthly average: reprojection
#############################################################################

# Rescale SSMIS at same resolution and projection as Sentinel-1.
def reduceResolutionS1climatology(feature):
  return feature.reproject(**{'crs': crs_3031, 'scale': scale_spatialres});  

S1climatology = S1climatology.map(reduceResolutionS1climatology)


#############################################################################
# Sentinel-1 monthly average: add to rest of input features
#############################################################################

# Add monthly climatology band to each image in 'melt_all' image collection
def addS1ClimatologyBand(img):
  matchingClimatology = S1climatology \
                        .filterMetadata('month','equals',img.get('month_meltAll')) \
                        .filterMetadata('year','equals',img.get('year_meltAll')) \
                        .first()
  matchingClimatology = ee.Image(matchingClimatology)
  return img.addBands(matchingClimatology)

melt_all = melt_all.map(addS1ClimatologyBand)

#############################################################################
# Elevation: preprocessing
#############################################################################

# Add normalized elevation band to each image in 'melt_all' image collection
normElevation = DEM.unitScale(0, 1700)
normElevation_melt = normElevation.reproject(**{'crs': crs_3031, 'scale': scale_spatialres})

def addElevationBand(img):
    return img.addBands(normElevation_melt)

melt_all = melt_all.map(addElevationBand)

#############################################################################
# Merging and re-ordering all input features
#############################################################################

# Clip images to ROI

def cliptoROI(img):
  return img.clip(ROI)

melt_all = melt_all.map(cliptoROI)

# Rearrange order of bands to get them in the same order as when the U-Net was trained
# 1: Elevation; 2: S1 climatology; 3: SSMIS; : ASCAT

def reorderBands(img):
  band4 = img.select('melt_ascat') 
  band3 = img.select('melt_SSMIS')
  band2 =  img.select('melt_S1_climatology')
  band1 = img.select('elevation')

  comb = band1.addBands(band2).addBands(band3).addBands(band4)
  return comb


melt_all = melt_all.map(reorderBands)

# Select between time period of interest
melt_all = melt_all.filterDate(start_poi, end_poi)

#############################################################################
# Import U-Net model
#############################################################################

# Set some ee.Model parameters
PROJECT = 'ee-iceshelf-gee4geo'
MODEL_NAME = 'AttUnet_500mShackletonTrained_'
VERSION_NAME = 'v0'
EEFIED_DIR = 'gs://ee-surfacemelt/Models/' + MODEL_NAME

# Load the trained model and use it for prediction.
model = ee.Model.fromAiPlatformPredictor(**{
    'projectName': PROJECT,
    'modelName': MODEL_NAME,
    'inputTileSize': [48,48],
    'inputShapes': {'array':[4]},
    'inputOverlapSize': [8,8],
    'proj': ee.Projection('EPSG:3031').atScale(scale_spatialres),
    'fixInputProj': True,
    'outputBands': {'output': {'type': ee.PixelType.float()}}})


#############################################################################
# Prediction using trained U-Net model
#############################################################################

# Function to predict the labels as (1) percentags (0-100) and (2) binary (0: no melt, 1: melt)
def predictLabel(img):

  # Make float of input bands
  inputs = img.float()

  # Run the predictions
  predictions = model.predictImage(inputs.toArray()).rename('prediction')
  predictions_rounded = predictions.toArray().arrayGet([0]).round().rename('prediction_rounded')

  return img.addBands(predictions).addBands(predictions_rounded)

predictedCol = melt_all.map(predictLabel).select('prediction')


#############################################################################
# Exporting to Asset
#############################################################################

# Create list of collection
collectionList = predictedCol.toList(predictedCol.size());
n = collectionList.size().getInfo();
print('Number of images to upload to GEE:', n)

# Create list of time (so it can be added to image name)
localtimeList = predictedCol.aggregate_array('LocalTime')

  
# Export images to Asset
for i in range(0, n, 1):

  # Select image of interest
  export_img = ee.Image(collectionList.get(i)) 

  # Get time of image to use as image name
  localtime = localtimeList.get(i).getInfo() 

  # Export the image to an Earth Engine asset.
  task = ee.batch.Export.image.toAsset(**{
  'image': export_img,
  'description': 'DownloadImageToAsset',
  'assetId': 'users/sophiederoda/UNetResults/FeatureImportance/Predictions_NoASCAT_v2/Prediction_' + str(localtime),
  'scale': 500,
  'region': ROI.bounds().getInfo()['coordinates']})
  task.start()
  

