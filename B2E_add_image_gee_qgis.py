import ee
from ee_plugin import Map
 
# ee.Authenticate()
# ee.Initialize()

def maskL8SR(imagem):
    '''Filtro para remover nuvens e sombras
    das imagens LANDSAT 8 com buffer de 100m'''
     
    cloudShadowBitmask = int(2**3)
    cloudBitmask = int(2**5)
    qa = imagem.select('pixel_qa')
    mask = qa.bitwiseAnd(cloudShadowBitmask).eq(0).And(\
           qa.bitwiseAnd(cloudBitmask).eq(0))\
        .focal_min(radius = 100, units = 'meters')
     
    return imagem.updateMask(mask)
 
def maskL5SR(imagem):
    '''Filtro para remover nuvens e sombras
    das imagens LANDSAT 5 com buffer de 100m'''
     
    qa = imagem.select('pixel_qa')
    cloud = qa.bitwiseAnd(int(2**5)).And(qa.bitwiseAnd(int(2**7)))\
        .Or(qa.bitwiseAnd(2**3)).focal_max(radius = 100, units = 'meters')
         
    mask2 = imagem.mask().reduce(ee.Reducer.min())
     
    return imagem.updateMask(cloud.Not()).updateMask(mask2)
  
coordenadas = [[-49.45, -28.58], [-49.40, -28.58], [-49.40, -28.60], [-49.45, -28.60], [-49.45, -28.58]]
ee_pol = ee.Geometry.Polygon(coordenadas)
 
img_1990 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')\
    .filterDate('1989-01-01', '1991-12-31')\
    .filterBounds(ee_pol)\
    .map(maskL5SR)\
    .mean()
     
visParams5 = {'bands': ['B3', 'B2', 'B1'], 'min': 0, 'max': 3000, 'gamma': 1.4}
 
Map.addLayer(img_1990, visParams5, 'IMG_1990')
 
img_2020 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')\
    .filterDate('2020-01-01', '2020-12-31')\
    .filterBounds(ee_pol)\
    .map(maskL8SR)\
    .median()
     
visParams8 = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.4}
 
Map.addLayer(img_2020, visParams8, 'IMG_2020')
