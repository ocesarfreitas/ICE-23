import pandas as pd
import numpy as np
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
del indicador_pro['BAIXADOS']
del indicador_pro['NOVOS']
del indicador_pro['PENDENTES']

subdet_tempo = indicador.reset_index().merge(indicador_pro, how='inner', on='Município').set_index(['Município','UF'])
    
# ---------------------------------------------------------------------------------------------
# 2.2.2. SUBDETERMINANTE TRIBUTAÇÃO

## SINCONFI
database = database.reset_index()
database['Cod.IBGE'] = amostra['COD. MUNIC'] 

sinconfi_mun = pd.read_csv("DETERMINANTE AMBIENTE REGULATÓRIO/Sinconfi/finbra_mun.csv",
                           encoding='ISO-8859-1', sep=';', decimal=',')
sinconfi_uf = pd.read_csv("DETERMINANTE AMBIENTE REGULATÓRIO/Sinconfi/finbra_uf.csv",
                          encoding='ISO-8859-1', sep=';', decimal=',')

def sinconfi(df1,df2,imposto,var):
    df_mun = df1[df1['Conta'] == var]
    df_mun = df_mun[df_mun['Coluna'] == 'Receitas Brutas Realizadas']
    df_mun['Cod.IBGE'] = df_mun['Cod.IBGE'].astype(int).astype(str).str[2:].astype(np.int64)
    df_mun = database.merge(df_mun, how='left', on = ['Cod.IBGE','UF'])
    df_mun = df_mun[['Município','UF','Valor']]
    df_mun = df_mun[(df_mun['Município'] != 'BRASILIA')]
    
    df_uf = df2[df2['Conta'] == var]
    df_uf = df_uf[df_uf['UF'] == 'DF']
    df_uf = df_uf[df_uf['Coluna'] == 'Receitas Brutas Realizadas']
    df_uf['Município'] = ['BRASILIA']
    df_uf = df_uf[['Município','UF','Valor']]
    
    globals()[f'df_{imposto}'] = df_mun.append(df_uf).reset_index(drop=True)
    
### ICMS
sinconfi(sinconfi_mun,sinconfi_uf,imposto='ICMS',var='1.1.1.8.02.0.0 - Impostos sobre a Produção, Circulação de Mercadorias e Serviços')

### IPTU
sinconfi(sinconfi_mun,sinconfi_uf,imposto='IPTU',var='1.1.1.8.01.1.0 - Imposto sobre a Propriedade Predial e Territorial Urbana')

### ISS
sinconfi(sinconfi_mun,sinconfi_uf,imposto='ISS',var='1.1.1.8.02.3.0 - Imposto sobre Serviços de Qualquer Natureza')
# Cara alguma coisa = 0

## FIRJAN
df_firjan = pd.read_excel("DETERMINANTE AMBIENTE REGULATÓRIO/Firjan/Firjan - Evolucao por Indicador 2013 a 2020 - IFGF 2021.xlsx", usecols="B:C,AA")
df_firjan['Município'] = df_firjan['Município'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
teste = database.merge(df_firjan, how='left', on = ['Município','UF'])

# ---------------------------------------------------------------------------------------------
# 2.2.3. SUBDETERMINANTE COMPLEXIDADE BUROCRÁTICA



