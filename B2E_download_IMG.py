# -*- coding: utf-8 -*-
"""
Código da postagem do Blog 2 Engenheiros
Code of the Blog 2 Engenheiros' post
"""

import ee
#ee.Authenticate()
ee.Initialize()

area_estudo = ee.Geometry.Rectangle([-49.7, -28.3, -49.3, -28.7])
img_landsat = ee.Image('LANDSAT/LC08/C01/T1/LC08_220080_20200420')\
    .select(['B2','B3','B4']).clip(area_estudo)

# print(img_landsat.reduceRegion(reducer = ee.Reducer.minMax()).getInfo())

# print(img_landsat.getThumbURL({'min': 5000, 'max': 23000}))

# task = ee.batch.Export.image.toDrive(**{
#     'image': img_landsat,
#     'description': 'img_B2E',
#     'folder': 'EE_Output',
#     'scale': 30,
#     'region': area_estudo.getInfo()['coordinates']
#     })
# task.start()

# import time
# while task.active():
#     print('Salvando a imagem (id: {}).'.format(task.id))
#     time.sleep(5)
    
download_url = img_landsat.getDownloadURL({
    'image': img_landsat,
    'region': area_estudo,
    'name': 'img_B2E_down',
})

print(download_url)