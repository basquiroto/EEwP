# -*- coding: utf-8 -*-
"""
Created on Mon May 17 21:07:10 2021

Código para criar gráficos de dispersão entre duas imagens no GEE

@author: Fernando Basquiroto de Souza
"""

print('Inicializando...')
import ee
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

ee.Initialize()

print('Obtendo imagens..')
date1 = ee.Date('2013-05-01') 
date2 = ee.Date('2021-05-01')

landsat_coll = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')\
    .filterDate(date1, date2)\
    .filterMetadata('WRS_PATH', 'equals', 220)\
    .filterMetadata('WRS_ROW', 'equals', 80)\
    .filterMetadata('CLOUD_COVER', 'less_than', 10)
landsat_list = landsat_coll.toList(landsat_coll.size().getInfo())
landsat_img = ee.Image(landsat_list.get(0))

data = ee.Date(landsat_img.get('system:time_start').getInfo())
projection = landsat_img.projection().crs().getInfo()

scene_lim = landsat_img.geometry()
limite = scene_lim.centroid().buffer(10000)

modis_coll = ee.ImageCollection('MODIS/006/MOD09GA')\
    .filterDate(data, data.advance(1, 'day'))
modis_list = modis_coll.toList(modis_coll.size().getInfo())
modis_img = ee.Image(modis_list.get(0))\
    .reproject(crs = 'SR-ORG:6974', scale = 500)\
    .reproject(crs = projection, scale = 500)

red_L = landsat_img.select('B4')
red_M = modis_img.select('sur_refl_b01').clip(limite)
red_img = ee.Image.cat([red_L, red_M])

print('Convertendo para arrays.') # Com Numpy Arrays
red_toList = {'reducer': ee.Reducer.toList(), 'geometry': limite,
              'scale': 500, 'bestEffort': True}
img_values = red_img.reduceRegion(**red_toList) 
L_arr = np.array((ee.Array(img_values.get('B4')).getInfo()))
M_arr = np.array((ee.Array(img_values.get('sur_refl_b01')).getInfo()))

# https://mygeoblog.com/2019/07/09/scatter-plot-in-gee/
# print('Amostrando imagens.') # Com Pandas DataFrame
# n_sample = 1236
# img_list = []
# img_values = red_img.sample(**{'region': limite, 
#                                'scale': 500, 
#                                'numPixels': n_sample, 
#                                'geometries': True}) 

# df_raw = pd.DataFrame(img_values.toList(n_sample).getInfo())

# # https://codereview.stackexchange.com/questions/93923/
# # extracting-contents-of-dictionary-contained-in-pandas-dataframe-to-make-new-data
# def unpack(df, column):
#     ret = None
#     ret = pd.concat([df, pd.DataFrame((d for idx, d in df[column].iteritems()))], axis=1)
#     del ret[column]
#     return ret

# df = unpack(df_raw, 'properties')

print('Gerando gráfico de dispersão') # Com Numpy Array
fsize = 15
figd, axd = plt.subplots(figsize = (6,6))
axis_min = min([min(L_arr), min(M_arr)])*0.95
axis_max = max([max(L_arr), max(M_arr)])*1.05
plt.scatter(x = L_arr, y = M_arr, alpha=0.7, s = 48)
plt.xlim(axis_min, axis_max)
plt.ylim(axis_min, axis_max)
axd.plot([0, 1], [0, 1], color='red', linestyle=':', transform=axd.transAxes,
         linewidth=2)
plt.grid(color='#c6c6c6', linestyle=':', linewidth=0.5)
plt.title('Vermelho Landsat 8 x MODIS', fontsize = fsize)
plt.xlabel('Landsat B4 (636-673 nm)', fontsize = fsize)
plt.ylabel('MODIS B1 (620-670 nm)', fontsize = fsize)

# print('Gerando gráfico de dispersão') # Com Pandas DataFrame
# fsize = 15
# figd, axd = plt.subplots(figsize = (6,6))
# axis_min = min([min(df['B4']), min(df['sur_refl_b01'])])*0.95
# axis_max = max([max(df['B4']), max(df['sur_refl_b01'])])*1.05
# df.plot(x = 'B4', y = 'sur_refl_b01', kind='scatter', ax = axd,
#               xlim=[axis_min,axis_max], ylim=[axis_min,axis_max],
#               alpha=0.7, s = 48)
# axd.plot([0, 1], [0, 1], color='red', linestyle=':', transform=axd.transAxes,
#          linewidth=2)
# plt.grid(color='#c6c6c6', linestyle=':', linewidth=0.5)
# plt.title('Vermelho Landsat 8 x MODIS', fontsize = fsize)
# plt.xlabel('Landsat B4 (636-673 nm)', fontsize = fsize)
# plt.ylabel('MODIS B1 (620-670 nm)', fontsize = fsize)

figd.savefig('C:/Users/ferna/Desktop/TEMP/Scatterplot_Reds.png',
             dpi = 60, bbox_inches = 'tight')
plt.close()