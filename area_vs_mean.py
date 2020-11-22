# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 20:55:21 2020

@author: Fernando Basquiroto de Souza

Código para testar influência do tamanho da área na média
da temperatura de superficie das imagens MODIS
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ee
ee.Initialize()

ponto = [-50.8472518, -26.9704873]
ee_ponto = ee.Geometry.Point(ponto)

media = []
buffer_list = np.linspace(0.01, 5.00, 30)

for i in range(len(buffer_list)):
    Rect = [(ponto[0]+buffer_list[i]),(ponto[1]-buffer_list[i]),
            (ponto[0]-buffer_list[i]),(ponto[1]+buffer_list[i])]
    lim_Rect = ee.Geometry.Rectangle(Rect)
    
    # 2014_10_27 e 2014_09_25
    img = ee.Image('MODIS/006/MOD11A1/2010_01_01').select('LST_Day_1km')\
        .clip(lim_Rect).multiply(ee.Image(0.02))
    
    media_temp_raw = img.reduceRegion(**{'reducer': ee.Reducer.mean(),
                                     'geometry': lim_Rect,
                                     'scale': 1000})
    media_temp = list(media_temp_raw.getInfo().values())[0]
    media.append((round(buffer_list[i], 2), media_temp))
    
mean_df = pd.DataFrame(media, columns = ['Buffer', 'Média'])

grafico = mean_df.plot(x = 'Buffer', y = 'Média')
plt.show()