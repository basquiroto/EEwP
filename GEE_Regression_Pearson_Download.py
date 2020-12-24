# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 15:20:12 2020

How to perform a linear regression, calculate pearson's coefficient (R2)
and to automatic download google earth engine thumbnails.

Como criar uma regressão linear, calcular coeficiente de pearson (R2)
e automatizar o download de imagens de amostra no google earth engine.

@author: Fernando Basquiroto de Souza
"""

import ee
import time
import requests
import shutil
ee.Initialize()

começo = time.time()

lim_Rect = ee.Geometry.Rectangle([-59,-6, -49, -16])
img_01 = ee.Image('MODIS/006/MOD11A1/2018_07_08')\
    .select('LST_Day_1km').clip(lim_Rect).multiply(ee.Image(0.02))
img_02 = ee.Image('MODIS/006/MOD11A1/2018_07_09')\
    .select('LST_Day_1km').clip(lim_Rect).multiply(ee.Image(0.02))

constant = ee.Image(1)
xVar = img_01
yVar = img_02
imgRegress = ee.Image.cat(constant, xVar, yVar);
regress = imgRegress.reduceRegion(
        reducer = ee.Reducer.linearRegression(
            numX = 2,
            numY = 1),
        geometry= lim_Rect, 
        scale= 1000)

intercept = list(regress.getInfo().values())[0][0][0]
slope = list(regress.getInfo().values())[0][1][0]

print('y = ', round(intercept, 4), ' + ', round(slope, 4), 'x')

min_max_01 = img_01.reduceRegion(**{'reducer': ee.Reducer.minMax(),
                                    'geometry': lim_Rect,
                                    'scale': 1000})
max_value01 = list(min_max_01.getInfo().values())[0]
min_value01 = list(min_max_01.getInfo().values())[1]

## https://towardsdatascience.com/how-to-download-an-image-using-python-38a75cfa21c
img_01_URL = img_01.getThumbURL({'min': min_value01, 'max': max_value01})
filePath = 'C:/Users/ferna/Desktop/MOD11A1_2018_07_08.png'

r = requests.get(img_01_URL, stream = True)

if r.status_code == 200:
    r.raw.decode_content = True
    
    with open(filePath,'wb') as f:
        shutil.copyfileobj(r.raw, f)
        
    print('Imagem baixada com sucesso: ', filePath.split('/')[-1])
else:
    print('Falha no download da imagem.')

fim = time.time()

print('Tempo de processamento: ', round(fim - começo, 2), ' s.')
