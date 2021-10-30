# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 14:38:22 2021

@author: Fernando Basquiroto de Souza
"""
import ee
ee.Initialize()

def get_pv_coll(img, coord, band):
    def get_pv(img):
        
        img_reproj = img.reproject(crs = 'EPSG:4326', scale = 30)
        pv_dict = img_reproj.reduceRegion(ee.Reducer.first(), coord, 30);
        
        return ee.Feature(None, pv_dict)
    
    fc = img.filterBounds(coord).map(get_pv).getInfo()
    size = len(fc['features'])
    pv_list = []
    
    for i in range(size):
        date_temp = fc['features'][i]['id'][-8:]
        value_temp = fc['features'][i]['properties'][band]
        pv_list.append([date_temp, value_temp])
    
    return pv_list
    
point_coord = ee.Geometry.Point([-49.3858,-28.6907])
img_coll = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')\
    .filterBounds(point_coord)\
    .filterDate('2018-01-01', '2018-06-01')
    
teste = get_pv_coll(img_coll, point_coord, "ST_B10")

import pandas as pd

df = pd.DataFrame(teste, columns = ['Date', 'LST_Raw'])
df['LST_K'] = (df['LST_Raw']*0.00341802)+149