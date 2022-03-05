# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 12:46:05 2022

@author: Fernando Basquiroto de Souza
Convertion of Ujaval Ghandhi javascript code to python (Sentinel's example'): 
Source: spatialthoughts.com/2021/11/08/temporal-interpolation-gee/

"""

import ee

# ee.Authenticate()
ee.Initialize()

geometry = ee.Geometry.Polygon([[
  [82.60642647743225, 27.16350437805251],
  [82.60984897613525, 27.1618529901377],
  [82.61088967323303, 27.163695288375266],
  [82.60757446289062, 27.16517483230927]
]])

s2 = ee.ImageCollection("COPERNICUS/S2_SR")
filtered = s2.filter(ee.Filter.date('2019-01-01', '2020-01-01'))\
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))\
            .filter(ee.Filter.bounds(geometry))

# Write a function for Cloud masking
def maskCloudAndShadowsSR(image):
  cloudProb = image.select('MSK_CLDPRB');
  snowProb = image.select('MSK_SNWPRB');
  cloud = cloudProb.lt(5);
  snow = snowProb.lt(5);
  scl = image.select('SCL'); 
  shadow = scl.eq(3); # 3 = cloud shadow
  cirrus = scl.eq(10); # 10 = cirrus
  # Cloud probability less than 5% or cloud shadow classification
  mask = (cloud.And(snow)).And(cirrus.neq(1)).And(shadow.neq(1));
  
  return image.updateMask(mask).divide(10000)\
      .select("B.*")\
      .copyProperties(image, ["system:time_start"])

filtered = filtered.map(maskCloudAndShadowsSR)

def timeImage(image):
  timeImage = image.metadata('system:time_start').rename('timestamp')
  timeImageMasked = timeImage.updateMask(image.mask().select(0))
  
  return image.addBands(timeImageMasked)

filtered = filtered.map(timeImage)

days = 30
millis = ee.Number(days).multiply(1000*60*60*24)

maxDiffFilter = ee.Filter.maxDifference(**{
  'difference': millis,
  'leftField': 'system:time_start',
  'rightField': 'system:time_start'
})
lessEqFilter = ee.Filter.lessThanOrEquals(**{
  'leftField': 'system:time_start',
  'rightField': 'system:time_start'
})
greaterEqFilter = ee.Filter.greaterThanOrEquals(**{
  'leftField': 'system:time_start',
  'rightField': 'system:time_start'
})

filter1 = ee.Filter.And(maxDiffFilter, lessEqFilter)
 
join1 = ee.Join.saveAll(**{
  'matchesKey': 'after',
  'ordering': 'system:time_start',
  'ascending': False})
   
join1Result = join1.apply(**{
  'primary': filtered,
  'secondary': filtered,
  'condition': filter1
})

filter2 = ee.Filter.And(maxDiffFilter, greaterEqFilter)
 
join2 = ee.Join.saveAll(**{
  'matchesKey': 'before',
  'ordering': 'system:time_start',
  'ascending': True})
   
join2Result = join2.apply(**{
  'primary': join1Result,
  'secondary': join1Result,
  'condition': filter2
})

# Tip (by Ujaval Ghandhi):
# If you wanted a simple average of before and after images, 
# you can set the value of timeRatio to 0.5.

def interpolateImages(image):
  image = ee.Image(image)
  
  # We get the list of before and after images from the image property
  # Mosaic the images so we a before and after image with the closest unmasked pixel
  beforeImages = ee.List(image.get('before'))
  beforeMosaic = ee.ImageCollection.fromImages(beforeImages).mosaic()
  afterImages = ee.List(image.get('after'))
  afterMosaic = ee.ImageCollection.fromImages(afterImages).mosaic()
  
  # Get image with before and after times
  t1 = beforeMosaic.select('timestamp').rename('t1')
  t2 = afterMosaic.select('timestamp').rename('t2')
  t = image.metadata('system:time_start').rename('t')
  timeImage = ee.Image.cat([t1, t2, t])
  timeRatio = timeImage.expression('(t - t1) / (t2 - t1)', {
    't': timeImage.select('t'),
    't1': timeImage.select('t1'),
    't2': timeImage.select('t2'),
  })
  
  # Compute an image with the interpolated image y
  interpolated = beforeMosaic\
    .add((afterMosaic.subtract(beforeMosaic).multiply(timeRatio)))
  
  # Replace the masked pixels in the current image with the average value
  result = image.unmask(interpolated)
  return result.copyProperties(image, ['system:time_start'])

interpolatedCol = ee.ImageCollection(join2Result.map(interpolateImages))

# Let's visualize the NDVI time-series
def addNDVI(image):
  ndvi = image.normalizedDifference(['B8', 'B4']).rename('ndvi');
  return image.addBands(ndvi);

ndviVis = {'min':0, 'max': 0.9, 'bands': 'ndvi', 'palette': [
    'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901',
    '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01',
    '012E01', '011D01', '011301'
  ]}

def visualizeImage(image):
  return image.select('ndvi').visualize(**ndviVis).clip(geometry)

visCollectionOriginal = filtered.map(addNDVI).map(visualizeImage)
visCollectionInterpolated = interpolatedCol.map(addNDVI).map(visualizeImage)

videoArgs = {
  'dimensions': 400,
  'region': geometry,
  'framesPerSecond': 1,
  'crs': 'EPSG:3857',
}

print('Original NDVI Images', visCollectionOriginal.getVideoThumbURL(videoArgs))
print('Gap Filled NDVI Images', visCollectionInterpolated.getVideoThumbURL(videoArgs)) 