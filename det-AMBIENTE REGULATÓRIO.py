import pandas as pd
# import numpy as np
from funcs import *

# 2.2. DETERMINANTE AMBIENTE REGULATÓRIO
database = pd.DataFrame()
df = {}

# 1. AMOSTRA

amostra = pd.read_csv('AMOSTRA/100-municipios.csv')
database['Município'] = amostra['NOME DO MUNICÍPIO']
database['UF'] = amostra['UF']
database = database.set_index(['Município', 'UF'])

# 2.2.
ambiente = {}
subdet = 'Tempo de processos'

# ---------------------------------------------------------------------------------------------
# 2.2.1. SUBDETERMINANTE TEMPO DE PROCESSOS
subdet = 'Tempo de processos'

for i in list(range(1,13)):
    globals()[f"indicador_{i}"] = pd.read_excel(f'DETERMINANTE AMBIENTE REGULATÓRIO/REDESIM/tempos-abertura-Brasil{i}2021.xlsx', 
                                                    header=1, usecols="I,R,AA,AB")
    pdList = []
    pdList.extend(value for name, value in locals().items() if name.startswith("indicador"))
    indicador = pd.concat(pdList, axis = 0)

var = ['novos','baixados','pendentes']
for i in list(range(0,3)):
    globals()[f"indicador_pro_{i}"] = pd.read_excel(f'DETERMINANTE AMBIENTE REGULATÓRIO/CNJ/{var[i]}_cnj.xlsx')
    pd_List = []
    pd_List.extend(value for name, value in locals().items() if name.startswith("indicador_pro"))
    indicador_pro = pd.concat(pdList, axis = 0)

    
# ---------------------------------------------------------------------------------------------
# 2.2.2. SUBDETERMINANTE TRIBUTAÇÃO

