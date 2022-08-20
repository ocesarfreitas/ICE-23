"""
Created on Thu Aug 18 16:50:42 2022

@author: CLIENTE
"""

import pandas as pd
#import numpy as np
from funcs import *
#from functools import reduce
import basedosdados as bd

# 2.2. DETERMINANTE AMBIENTE REGULATÓRIO
database = pd.DataFrame()
df = {}

# 1. AMOSTRA

amostra = pd.read_csv('AMOSTRA/100-municipios.csv', converters={i: str for i in range(0,101)})
amostra['Cod.IBGE'] = amostra['COD. UF'] + amostra['COD. MUNIC']
database['Município'] = amostra['NOME DO MUNICÍPIO'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
database['UF'] = amostra['UF']
database['Cod.IBGE'] = amostra['Cod.IBGE']
database = database.set_index(['Município', 'UF'])

# 2.5.
## 2.5.1. e 2.5.3.
variaveis = ('COUNT(quantidade_vinculos_ativos), id_municipio')
base = '`basedosdados.br_me_rais.microdados_estabelecimentos`'
project_id = 'double-balm-306418'
cod_ibge = tuple(database['Cod.IBGE'].astype(str))
query = f"SELECT {variaveis} FROM {base} WHERE ano = 2020 AND quantidade_vinculos_ativos > 0 GROUP BY id_municipio"

## Importando o data lake
df_rais = bd.read_sql(query=query, billing_project_id=project_id)
df_rais = df_rais.rename(columns={'id_municipio':'Cod.IBGE'}).set_index('Cod.IBGE')
df_rais = database.merge(df_rais,how='left',on='Cod.IBGE')
df_rais['mil_emp'] = df_rais['f0_']/1000
## 
df_capes = pd.read_excel('DETERMINANTE INOVAÇÃO/br-capes-colsucup-discentes-2020-2021-11-10.xlsx', usecols='D,P,Q,AD')
df_capes['Município'] = df_capes['NM_MUNICIPIO_PROGRAMA_IES'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df_capes = database.merge(df_capes, how='left',on='Município')

areas = ['astronomia / física', 'biotecnologia', 'ciência da computação', 
         'ciência de alimentos', 'ciências agrárias I', 'ciências ambientais', 
         'ciências biológicas I', 'ciências biológicas II', 'ciências biológicas III', 
         'engenharias I', 'engenharias II', 'engenharias III', 'engenharias IV', 
         'farmácia', 'geociências', 'matemática / probabilidade', 'estatística', 
         'materiais e química']
areas = [x.upper() for x in areas]

df_capes = df_capes[df_capes['NM_SITUACAO_DISCENTE'] == 'TITULADO']
df_capes = df_capes.query('NM_AREA_AVALIACAO in @areas')
df_capes = df_capes.groupby(['Município','Cod.IBGE']).count()
df_capes = df_rais.merge(df_capes, how='left', on='Cod.IBGE').fillna(0)
df_capes['Proporção de Mestres e Doutores em C&T'] = df_capes['NM_AREA_AVALIACAO']/df_capes['mil_emp']
