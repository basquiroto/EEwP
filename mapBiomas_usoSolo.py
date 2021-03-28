# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 10:09:12 2021

@author: Fernando BS

Calcula a área do uso do solo (MapBiomas) em um determinado polígono
para um intervalo de anos fornecido.
"""

import ee
import pandas as pd

ee.Initialize()

# Variáveis de Entrada

codigo = 'AREA1'
startYear = 2010
endYear = 2011
ponto = [-49.3698877,-28.684251]

ee_coord = ee.Geometry.Point(ponto)
limite = ee_coord.buffer(5000)
pixel_size = 30

mapbiomas = ee.Image('projects/mapbiomas-workspace/public/collection5/mapbiomas_collection50_integration_v1')

# Legenda Mapbiomas Coleção 5
# https://mapbiomas-br-site.s3.amazonaws.com/downloads/Códigos_das_classes_da_legenda_e_paleta_de_cores.pdf
legenda_c5 = {1: 'Floresta', 2: 'Floresta Natural', 3: 'Formação Florestal',
              4: 'Formação Savânica', 5: 'Mangue', 9: 'Floresta Plantada',
              10: 'Formação Natural não Florestal', 
              11: 'Campo Alagado ou Área Pantanosa',
              12: 'Formação Campestre', 32: 'Apicum', 29: 'Afloramento Rochoso',
              13: 'Outras Formações não Florestais', 14: 'Agropecuária',
              15: 'Pastagem', 18: 'Agricultura', 19: 'Lavoura Temporária',
              39: 'Soja', 20: 'Cana', 41: 'Outras Lavouras Temporárias',
              36: 'Lavoura Perene', 21: 'Mosaico de Agricultura e Pastagem',
              22: 'Área não Vegetada', 23: 'Praia e Duna', 
              24: 'Infraestrutura Urbana', 30: 'Mineração', 
              25: 'Outras Áreas não Vegetadas', 26: 'Corpos Dágua',
              33: 'Rio, Lago e Oceano', 31: 'Aquicultura', 27: 'Não Observado'}

us_list = []

for y in range(startYear, endYear+1):
        
    uso_solo = mapbiomas.select('classification_'+str(y)).clip(limite)
    
    ## Número de usos do solo em lim_Rect
    n_uso_solo = uso_solo.reduceRegion(**{
      "reducer": ee.Reducer.countDistinct(),
      "geometry": limite,
      "scale": pixel_size})
    classes = n_uso_solo.get('classification_' + str(y)).getInfo()
    
    print("Número de Usos do Solo ", str(y),": " + str(classes) )
    
    us_point_ee = uso_solo.reduceRegion(reducer = ee.Reducer.first(),
                                        geometry = ee_coord, scale=pixel_size)
    
    us_point = us_point_ee.get('classification_'+str(y)).getInfo()
    print('Uso do solo no ponto: ', legenda_c5.get(us_point))
    
    # Cálculo da área por classe
    # https://spatialthoughts.com/2020/06/19/calculating-area-gee/
    
    areaImage = ee.Image.pixelArea().addBands(uso_solo)
    
    area_total_ee = areaImage.reduceRegion(**{'reducer': ee.Reducer.sum(),
        'geometry': limite,
        'scale': pixel_size}); 
    areas_ee = areaImage.reduceRegion(**{'reducer': ee.Reducer.sum().group(**{
        'groupField': 1, 'groupName': 'class',}),
        'geometry': limite,
        'scale': pixel_size}); 
    
    area_total = area_total_ee.get('area').getInfo()
    areas = areas_ee.get('groups').getInfo()
    
    for i in range(0, classes):
        ID = areas[i].get('class')
        area_m2 = round(areas[i].get('sum'), 2)
        area_perc = round((area_m2 / area_total)*100, 2)
        legenda = legenda_c5.get(ID)
        
        us_list.append((y, legenda, area_m2, area_perc))

colunas = ['Ano','Uso do Solo','Área (m2)', 'Área (%)']
us_df = pd.DataFrame(us_list, columns = colunas)
print(us_df)

#us_df.to_csv(r'C:/Users/ferna/Desktop/TEMP/' + codigo + '_UsoSolo_MB.csv')