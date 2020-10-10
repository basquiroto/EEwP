# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 13:15:41 2020

@author: Fernando Basquiroto de Souza
"""

import ee
# ee.Authenticate() # Descomentar se não foi feito a autenticação ainda
ee.Initialize()

import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

def ymdList(imgcol):
    def iter_func(image, newlist):
        date = ee.Number.parse(image.date().format("YYYYMMdd"));
        newlist = ee.List(newlist);
        return ee.List(newlist.add(date).sort())
    ymd = imgcol.iterate(iter_func, ee.List([]))
    return list(ee.List(ymd).reduce(ee.Reducer.frequencyHistogram()).getInfo().keys())

ee_coord = ee.Geometry.Point([-49.4548067,-28.5375093])
startDate = '2013-06-01'
endDate = '2020-06-01'

ref_coll = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")\
    .filterBounds(ee_coord)

ref_date = ref_coll.filterDate(startDate, endDate)

dt_0 = ymdList(ref_date)
dates = [dt_0[i][0:4]+'-'+dt_0[i][4:6]+'-'+dt_0[i][6:8] for i in range(len(dt_0))]
date_list = ee.List(dates).map(lambda d: ee.Date(d).millis())

MODIS_coll = ee.ImageCollection("MODIS/006/MOD11A1")\
    .select("LST_Day_1km")\

coll = MODIS_coll.filter(ee.Filter.inList("system:time_start", date_list))

def get_point_coll(img_coll, coord, escala):
    num_img = img_coll.size().getInfo()
    coll_list = img_coll.toList(num_img)
    values_output = []
    
    for i in range(0, num_img, 1):
        img_temp = ee.Image(coll_list.get(i))
        
        tmstpA = ee.Date(img_temp.get('system:time_start'))
        tmstpB = tmstpA.getInfo()['value']/1000
        tmstpC = dt.datetime.utcfromtimestamp(tmstpB).strftime('%Y-%m-%d')

        eeDict_value = img_temp.reduceRegion(reducer = ee.Reducer.first(), 
                                             geometry = coord, scale = escala)
        value_pixel = list(eeDict_value.getInfo().values())[0]
        
        values_output.append((tmstpC, value_pixel))
    
    return values_output

tabela = get_point_coll(coll, ee_coord, 1000)

df_cols = ['Data', 'LST_K']
df = pd.DataFrame(tabela, columns = df_cols).dropna()
df['LST_K'] = 0.02*df['LST_K'] # Converte valores MODIS para K

grafico = df.plot(kind = 'line', x = 'Data', y = 'LST_K', color = 'darksalmon', rot = 90, 
                  ylim = (round((min(df['LST_K'])*0.95),0), round((max(df['LST_K'])*1.05),0)),
                  grid = True, marker = '.', label='LST (K)')
grafico.set_ylabel('Temperatura (K)')
grafico.grid(linestyle='dotted')
grafico.set_axisbelow(True)
plt.show()

df.to_csv(r'C:\Users\ferna\Desktop\dados_point.csv')