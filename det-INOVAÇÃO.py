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

## RAIS 2
cbo_2002 = tuple(['201105','201110','201115','201205','201210','201215','201220',
                  '201225','202105','202110','202115','202120','203005','203010',
                  '203015','203020','203025','203105','203110','203115','203120',
                  '203125','203205','203210','203215','203220','203225','203230',
                  '203305','203310','203315','203320','203405','203410','203415',
                  '203420','203505','203510','203515','203520','203525','204105',
                  '211105','211110','211115','211120','211205','211210','211215',
                  '212205','212210','212215','212305','212310','212315','212320',
                  '212405','212410','212415','212420','212425','212430','213105',
                  '213110','213115','213120','213125','213130','213135','213140',
                  '213145','213150','213155','213160','213165','213170','213175',
                  '213205','213210','213215','213305','213310','213315','213405',
                  '213410','213415','213420','213425','213430','213435','213440',
                  '214005','214010','214105','214110','214115','214120','214125',
                  '214130','214205','214210','214215','214220','214225','214230',
                  '214235','214240','214245','214250','214255','214260','214265',
                  '214270','214280','214305','214310','214315','214320','214325',
                  '214330','214335','214340','214345','214350','214360','214365',
                  '214370','214405','214410','214415','214420','214425','214430',
                  '214435','214505','214510','214515','214520','214525','214530',
                  '214535','214605','214610','214615','214705','214710','214715',
                  '214720','214725','214730','214735','214740','214745','214750',
                  '214805','214810','214905','214910','214915','214920','214925',
                  '214930','214935','214940','214945','215105','215110','215115',
                  '215120','215125','215130','215135','215140','215145','215150',
                  '215205','215210','215215','215220','215305','215310','215315',
                  '300105','300110','300305','301105','301110','301115','301205',
                  '311105','311110','311115','311205','311305','311405','311410',
                  '311505','311510','311515','311520','311605','311610','311615',
                  '311620','311625','311705','311710','311715','311720','311725',
                  '312105','312205','312210','312305','312310','312315','312320',
                  '313105','313110','313115','313120','313125','313130','313205',
                  '313210','313215','313220','313305','313310','313315','313320',
                  '313405','313410','313415','313505','314105','314110','314115',
                  '314120','314125','314205','314210','314305','314310','314315',
                  '314405','314410','314610','314615','314620','314625','314705',
                  '314710','314715','314720','314725','314730','314805','314810',
                  '314815','314825','314830','314835','314840','314845','316105',
                  '316110','316115','316120','316305','316310','316315','316320',
                  '316325','316330','316335','316340','317105','317110','317115',
                  '317120','317205','317210','318005','318010','318015','318105',
                  '318110','318115','318120','318205','318210','318215','318305',
                  '318310','318405','318410','318415','318420','318425','318430',
                  '318505','318510','318605','318610','318705','318710','318805',
                  '318810','318815','319105','319110','319205','391105','391110',
                  '391115','391120','391125','391130','391135','391140','391145',
                  '391205','391210','391215','391220','391225','391230','395105',
                  '395110','720105','720110','720115','720120','720125','720130',
                  '720135','720140','720145','720150','720155','720160','720205',
                  '720210','720215','720220','721105','721110','721115','721205',
                  '721210','721215','721220','721225','721305','721310','721315',
                  '721320','721325','721405','721410','721415','721420','721425',
                  '721430','722105','722110','722115','722205','722210','722215',
                  '722220','722225','722230','722235','722305','722310','722315',
                  '722320','722325','722330','722405','722410','722415','723105',
                  '723110','723115','723120','723125','723205','723210','723215',
                  '723220','723225','723230','723235','723240','723305','723310',
                  '723315','723320','723325','723330','724105','724110','724115',
                  '724120','724125','724130','724135','724205','724210','724215',
                  '724220','724225','724230','724305','724310','724315','724320',
                  '724325','724405','724410','724415','724420','724425','724430',
                  '724435','724440','724505','724510','724515','724605','724610',
                  '725005','725010','725015','725020','725025','725105','725205',
                  '725210','725215','725220','725225','725305','725310','725315',
                  '725320','725405','725410','725415','725420','725505','725510',
                  '725605','725610','725705','730105','731105','731110','731115',
                  '731120','731125','731130','731135','731140','731145','731150',
                  '731155','731160','731165','731170','731175','731180','731205',
                  '731305','731310','731315','731320','731325','731330','732105',
                  '732110','732115','732120','732125','732130','732135','732140'])

variaveis = ('id_municipio, count(*)')
base = '`basedosdados.br_me_rais.microdados_vinculos`'
project_id = 'double-balm-306418'
cod_ibge = tuple(database['Cod.IBGE'].astype(str))
query_1 = (f'SELECT {variaveis} AS n_cet FROM {base} WHERE ano = 2020 AND cbo_2002 IN' 
           f' {cbo_2002} AND id_municipio IN {cod_ibge} GROUP BY id_municipio')
query_2 = (f'SELECT {variaveis} AS n_trab FROM {base} WHERE ano = 2020 AND id_municipio' 
           f' IN {cod_ibge} GROUP BY id_municipio')
## Importando o data lake
df_rais_2_1 = bd.read_sql(query=query_1, billing_project_id=project_id)
df_rais_2_2 = bd.read_sql(query=query_2, billing_project_id=project_id)
df_rais_2 = df_rais_2_1.merge(df_rais_2_2, how='left',on='id_municipio') 
df_rais_2['Proporção de Funcionários em C&T'] = df_rais_2['n_cet']/df_rais_2['n_trab']

## Subdeterminante: Indicador Média de Investimentos do BNDES e da FINEP
###
df_bndes = pd.read_excel('DETERMINANTE INOVAÇÃO/naoautomaticas.xlsx', 
                         usecols='D:F,I', header=4)
df_bndes = df_bndes.rename({'Município - código':'Cod.IBGE'},axis=1).astype(str)
df_bndes = df_bndes.merge(database, how='right', on='Cod.IBGE')
df_bndes.iloc[:,3:4] = df_bndes.iloc[:,3:4].apply(pd.to_numeric)
df_bndes = df_bndes.groupby(['Município','UF','Cod.IBGE']).sum()

###
df_finep = pd.read_excel('DETERMINANTE INOVAÇÃO/19_08_2022_Contratacao.xls', 
                         usecols='E,K:M', header=5).drop([4], axis=0)
df_finep['Data Assinatura'] = pd.to_datetime(df_finep['Data Assinatura'], format='%Y-%m-%d')
df_finep = df_finep[(df_finep['Data Assinatura'] >= '2021-01-01 00:00:00') 
                     & (df_finep['Data Assinatura'] <= '2021-12-31 00:00:00')]

df_finep['Município'] = df_finep['Município'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df_finep = df_finep.groupby(['Município','UF']).sum()
df_finep = df_finep.merge(database, how='right',on=['Município','UF']).fillna(0)

df_finep_bndes = df_finep.merge(df_bndes, how='left',on=['Município','UF']).fillna(0)
df_finep_bndes = df_finep_bndes.merge(df_rais_2_1, left_on='Cod.IBGE', right_on='id_municipio')
df_finep_bndes['Média de Investimentos do BNDES e FINEP'] = (df_finep_bndes['Valor Finep'] + df_finep_bndes['Valor contratado  R$'])/df_finep_bndes['n_cet']


