# -*- coding: utf-8 -*-
"""
Created on Mon May 17 21:07:10 2021

Código para criar jointplots (HEX) entre duas imagens no GEE usando Seaborn

@author: Fernando Basquiroto de Souza
"""

print('Inicializando...')
import ee
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

ee.Initialize()

print('Obtendo imagens..')
date1 = ee.Date('2020-01-01') 
date2 = ee.Date('2020-02-01')

limites = ee.Geometry.Point([-49.43, -28.59]).buffer(50000)

lst_mean_day = ee.ImageCollection('MODIS/006/MOD11A1')\
    .filterDate(date1, date2).select('LST_Day_1km')\
    .mean().clip(limites)

ndvi_mean = ee.ImageCollection('MODIS/006/MOD13Q1')\
    .filterDate(date1, date2).select('NDVI')\
    .mean().clip(limites)

lst_img = ee.Image.cat([lst_mean_day, ndvi_mean])

print('Contando pixels.')
count_Reducer = {'reducer': ee.Reducer.count(), 'geometry': limites,
              'scale': 1000, 'bestEffort': True}
n_pixels = lst_img.reduceRegion(**count_Reducer) 
day_pixels = n_pixels.get('LST_Day_1km').getInfo()
ndvi_pixels = n_pixels.get('NDVI').getInfo()

n_sample = min([day_pixels, ndvi_pixels])

# https://mygeoblog.com/2019/07/09/scatter-plot-in-gee/
print('Amostrando imagens.') # Com Pandas DataFrame
img_values = lst_img.sample(**{'region': limites, 
                               'scale': 1000, 
                               'numPixels': n_sample, 
                               'geometries': True}) 

df_raw = pd.DataFrame(img_values.toList(n_sample).getInfo())

# https://codereview.stackexchange.com/questions/93923/
# extracting-contents-of-dictionary-contained-in-pandas-dataframe-to-make-new-data
def unpack(df, column):
    ret = None
    ret = pd.concat([df, pd.DataFrame((d for idx, d in df[column].iteritems()))], axis=1)
    del ret[column]
    return ret

df = unpack(df_raw, 'properties')
df['LST_Day_1km'] = df['LST_Day_1km']*0.02
df['NDVI'] = df['NDVI']*0.0001

print('Gerando Jointplot')

plot = sns.jointplot(data = df, x = 'LST_Day_1km', y = 'NDVI', 
                     kind = 'hex', ylim=[0,1])
plot.set_axis_labels('LST (Dia) (K)', 'NDVI', fontsize = 14)
plt.tick_params(axis="both", labelsize=14)

plt.tight_layout()
plot.savefig('C:/Users/ferna/Desktop/TEMP/jointPlot_LSTxNDVI.png',
             dpi = 120, bbox_inches = 'tight')
plt.close()