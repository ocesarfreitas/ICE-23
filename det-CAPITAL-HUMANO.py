"""
Created on Thu Aug 18 16:50:42 2022

@author: CLIENTE
"""

import pandas as pd
import numpy as np
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

## 2.7.1. Subdeterminante Acesso e Qualidade da Mão de Obra Básica
### 2.7.1.1. Indicador nota ideb
"Mesmo do ano passada porque é uma prova bianual"

### 2.7.1.2. Indicador proporção de adultos com pelo menos o ensino médio completo
df_enem = pd.read_csv('DETERMINANTE CAPITAL HUMANO/ENEM_2021_100mun.csv')
 
alvo = ['E','F','M']

pai_EM,mae_EM,num_inscritos = pd.DataFrame(),pd.DataFrame(),pd.DataFrame()

num_inscritos['n_inscritos'] = df_enem.groupby('CO_MUNICIPIO_ESC').size()
pai_EM['pai_EM'] = df_enem[df_enem['Q001'].isin(alvo)].groupby('CO_MUNICIPIO_ESC').size()
mae_EM['mae_EM'] = df_enem[df_enem['Q002'].isin(alvo)].groupby('CO_MUNICIPIO_ESC').size()

pai_mae_EM = pai_EM.merge(mae_EM, how='inner', on='CO_MUNICIPIO_ESC')
pai_mae_EM = pai_mae_EM.merge(num_inscritos, how='inner', on='CO_MUNICIPIO_ESC')

pai_mae_EM['prop_pai_EM'] = pai_mae_EM['pai_EM']/pai_mae_EM['n_inscritos']
pai_mae_EM['prop_mae_EM'] = pai_mae_EM['mae_EM']/pai_mae_EM['n_inscritos']
pai_mae_EM['Proporção de Adultos com pelo menos o Ensino Médio Completo'] = (pai_mae_EM['prop_pai_EM']+pai_mae_EM['prop_mae_EM'])/2
 
### 2.7.1.3. Indicador Taxa Líquida de Matrícula no Ensino Médio
df_ce_2021 = pd.read_csv('DETERMINANTE CAPITAL HUMANO/CE_2021_100mun.csv',
                         sep=',', encoding='latin-1')
df_ce_2021 = df_ce_2021[['CO_ENTIDADE','CO_MUNICIPIO','QT_MAT_MED','QT_MAT_BAS_0_3',
                         'QT_MAT_BAS_4_5','QT_MAT_BAS_6_10','QT_MAT_BAS_11_14',
                         'QT_MAT_BAS_15_17','QT_MAT_BAS_18_MAIS']].dropna()
df_ce_2021 = df_ce_2021[df_ce_2021['QT_MAT_MED'] != 0]
df_ce_2021 = df_ce_2021[df_ce_2021['QT_MAT_BAS_15_17'] != 0]

base = '`basedosdados.br_ibge_populacao.municipio`'
project_id = 'double-balm-306418'
cod_ibge = tuple(database['Cod.IBGE'].astype(str))
query = (f'SELECT * FROM {base} WHERE id_municipio IN {cod_ibge} AND ano = 2010')
df_censo = bd.read_sql(query=query, billing_project_id=project_id)

### 2.7.1.4. Indicador Nota Média no Enem
nota_enem = df_enem[['CO_MUNICIPIO_ESC','NU_NOTA_CH','NU_NOTA_CN',
                     'NU_NOTA_LC','NU_NOTA_MT','NU_NOTA_REDACAO']].dropna()
nota_enem = nota_enem.groupby('CO_MUNICIPIO_ESC').mean()
nota_enem['NOTA_ENEM'] = nota_enem.mean(axis=1)

### 2.7.1.5. Indicador Proporção de Matriculados no Ensino Técnico e Profissionalizante

## 2.7.2. Subdeterminante Acesso e Qualidade da Mão de Obra Qualificada
### 2.7.2.1. Indicador Proporção de Adultos com Pelo Menos o Ensino Superior Completo
alvo = ['F','G']

pai_SUP,mae_SUP = pd.DataFrame(),pd.DataFrame()

pai_SUP['pai_SUP'] = df_enem[df_enem['Q001'].isin(alvo)].groupby('CO_MUNICIPIO_ESC').size()
mae_SUP['mae_SUP'] = df_enem[df_enem['Q002'].isin(alvo)].groupby('CO_MUNICIPIO_ESC').size()

pai_mae_SUP = pai_SUP.merge(mae_SUP, how='inner', on='CO_MUNICIPIO_ESC')
pai_mae_SUP = pai_mae_SUP.merge(num_inscritos, how='inner', on='CO_MUNICIPIO_ESC')

pai_mae_SUP['prop_pai_SUP'] = pai_mae_SUP['pai_SUP']/pai_mae_EM['n_inscritos']
pai_mae_SUP['prop_mae_SUP'] = pai_mae_SUP['mae_SUP']/pai_mae_EM['n_inscritos']
pai_mae_SUP['Proporção de Adultos com pelo menos o Superior Completo'] = (pai_mae_SUP['prop_pai_SUP']+pai_mae_SUP['prop_mae_SUP'])/2

### 2.7.2.2. Indicador Proporção de Alunos Concluintes em Cursos de Alta Qualidade
"Mesmo do ano passada porque é uma prova bianual"

### Indicador Custo Médio de Salários de Dirigentes
cbo_2002 = tuple(['121005','121010','122105','122110','122115','122120','122205',
                  '122305','122405','122505','122510','122515','122520','122605',
                  '122610','122615','122620','122705','122710','122715','122720',
                  '122725','122730','122735','122740','122745','122750','122755',
                  '123105','123110','123115','123205','123210','123305','123310',
                  '123405','123410','123605','123705','123805','131105','131110',
                  '131115','131120','131205','131210','131215','131220','131225',
                  '131305','131310','131315','131320','141105','141110','141115',
                  '141120','141205','141305','141405','141410','141415','141420',
                  '141505','141510','141515','141520','141525','141605','141610',
                  '141615','141705','141710','141715','141720','141725','141730',
                  '141735','141805','141810','141815','141820','141825','141830',
                  '142105','142110','142115','142120','142125','142130','142205',
                  '142210','142305','142310','142315','142320','142325','142330',
                  '142335','142340','142345','142350','142405','142410','142415',
                  '142505','142510','142515','142520','142525','142530','142535',
                  '142605','142610','142705','142710'])

variaveis = 'valor_remuneracao_media,id_municipio'
base = '`basedosdados.br_me_rais.microdados_vinculos`'
project_id = 'double-balm-306418'
cod_ibge = tuple(database['Cod.IBGE'].astype(str))
query = (f'SELECT {variaveis} FROM {base} WHERE ano = 2019 AND cbo_2002 IN {cbo_2002}'
         f' AND id_municipio IN {cod_ibge}')

df_rais = bd.read_sql(query=query, billing_project_id=project_id)
df_rais = df_rais.groupby('id_municipio').agg(['count','sum'])
df_rais['Custo Médio de Salários de Dirigentes'] = df_rais.iloc[:,1]/df_rais.iloc[:,0] 















