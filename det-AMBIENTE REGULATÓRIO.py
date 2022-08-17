import pandas as pd
# import numpy as np
from funcs import *

# 2.2. DETERMINANTE AMBIENTE REGULATÓRIO
database = pd.DataFrame()
df = {}

# 1. AMOSTRA

amostra = pd.read_csv('AMOSTRA/100-municipios.csv')
database['Município'] = amostra['NOME DO MUNICÍPIO'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
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

indicador['Município'] = indicador['MUNICÍPIO'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
indicador = database.merge(indicador, how='left', on=['Município', 'UF'])
indicador['Tempo de Viabilidade de Localização'] = indicador['QTDE.  HH VIABILIDADE END']
indicador['Tempo de Registro de Localização'] = indicador['QTDE. HH. LIBERAÇÃO DBE']
indicador = indicador.groupby(['Município','UF']).mean()
indicador = indicador.fillna(0)

del indicador['MUNICÍPIO']
del indicador['QTDE.  HH VIABILIDADE END']
del indicador['QTDE. HH. LIBERAÇÃO DBE']

var = ['novos','baixados','pendentes']
for i in list(range(0,3)):
    globals()[f"indicador_pro_{i}"] = pd.read_excel(f'DETERMINANTE AMBIENTE REGULATÓRIO/CNJ/{var[i]}_cnj.xlsx')
    pd_List = []
    pd_List.extend(value for name, value in locals().items() if name.startswith("indicador_pro_"))
    indicador_pro = pd.concat(pd_List, axis = 0)

indicador_pro['Município'] = indicador_pro['Tribunal município'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
indicador_pro = database.merge(indicador_pro, how='left',on='Município')
indicador_pro = indicador_pro.pivot_table(index='Município', columns='Tipo variável', values='Indicador Valor')
indicador_pro['Taxa de Congestionamento em Tribunais'] = (1-(indicador_pro['BAIXADOS']/(indicador_pro['NOVOS']+indicador_pro['PENDENTES'])))

del indicador_pro['Justiça']
del indicador_pro['Tribunal município']
    
# ---------------------------------------------------------------------------------------------
# 2.2.2. SUBDETERMINANTE TRIBUTAÇÃO

