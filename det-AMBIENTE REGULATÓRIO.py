import pandas as pd
import numpy as np
from funcs import *
from functools import reduce
import basedosdados as bd

# 2.2. DETERMINANTE AMBIENTE REGULATÓRIO
database = pd.DataFrame()
df = {}

# 1. AMOSTRA

amostra = pd.read_csv('AMOSTRA/100-municipios.csv', converters={i: str for i in range(0,101)})
amostra['Cod.IBGE'] = amostra['COD. UF'].str.cat(amostra['COD. MUNIC']).astype(np.int64)
database['Município'] = amostra['NOME DO MUNICÍPIO'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
database['UF'] = amostra['UF']
database['Cod.IBGE'] = amostra['Cod.IBGE']
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
base = '`basedosdados.br_ibge_pib.municipio`'
project_id = 'double-balm-306418'
var = ('id_municipio, pib')
cod_ibge = list(database['Cod.IBGE'])
query = f'SELECT {var}, CASE id_municipio WHEN  FROM {base} WHERE (ano = 2019)'
pib_mun = bd.read_sql(query=query,billing_project_id=project_id)

def sinconfi(df1,df2,pib,imposto,var):
    df_mun = df1[df1['Conta'] == var]
    df_mun = df_mun[df_mun['Coluna'] == 'Receitas Brutas Realizadas']
    df_mun['Cod.IBGE'] = df_mun['Cod.IBGE'].astype(np.int64)
    df_mun = database.merge(df_mun, how='left', on = ['Cod.IBGE','UF'])
    df_mun = df_mun[['Município','UF','Valor']]
    df_mun = df_mun[(df_mun['Município'] != 'BRASILIA')]
    
    df_uf = df2[df2['Conta'] == var]
    df_uf = df_uf[df_uf['UF'] == 'DF']
    df_uf = df_uf[df_uf['Coluna'] == 'Receitas Brutas Realizadas']
    df_uf['Município'] = ['BRASILIA']
    df_uf = df_uf[['Município','UF','Valor']]
    
    pib = pib.rename(columns={'id_municipio':'Cod.IBGE'}).astype(np.int64)
    pib = database.merge(pib, how='left', on=['Cod.IBGE']).set_index(['Município','UF'])
    df = df_mun.append(df_uf).merge(pib, how='left',on=['Município','UF']).reset_index(drop=True)
    df[f'Alíquota Interna do {imposto}'] = df['Valor']/df['pib']
    
    globals()[f'df_{imposto}'] = df.drop(['Valor','pib','Cod.IBGE'], axis=1)
    
### ICMS
sinconfi(sinconfi_mun,sinconfi_uf,pib_mun,imposto='ICMS',var='1.1.1.8.02.0.0 - Impostos sobre a Produção, Circulação de Mercadorias e Serviços')

### IPTU
sinconfi(sinconfi_mun,sinconfi_uf,pib_mun,imposto='IPTU',var='1.1.1.8.01.1.0 - Imposto sobre a Propriedade Predial e Territorial Urbana')

### ISS
sinconfi(sinconfi_mun,sinconfi_uf,pib_mun,imposto='ISS',var='1.1.1.8.02.3.0 - Imposto sobre Serviços de Qualquer Natureza')
df_ISS = df_ISS.fillna(0)

## FIRJAN
df_firjan = pd.read_excel("DETERMINANTE AMBIENTE REGULATÓRIO/Firjan/Firjan - Evolucao por Indicador 2013 a 2020 - IFGF 2021.xlsx", usecols="B:C,AA")
df_firjan['Município'] = df_firjan['Município'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
df_firjan = database.merge(df_firjan, how='left', on = ['Município','UF']).fillna(0)
df_firjan = df_firjan.set_index(['Município','UF'])
df_firjan = df_firjan['IFGF 2020'].to_frame()
df_firjan = df_firjan.replace(to_replace=r'nd',value=0,regex=True)
df_firjan = df_firjan.rename(columns={'IFGF 2020':'Qualidade de Gestão Fiscal'})

dfs = [df_ICMS,df_IPTU,df_ISS,df_firjan]

subdet_tri = reduce(lambda left,right: pd.merge(left, right, on=['Município','UF'], 
                                                how='outer'), dfs)

# ---------------------------------------------------------------------------------------------
# 2.2.3. SUBDETERMINANTE COMPLEXIDADE BUROCRÁTICA
### Sinconfi

tributos = ['1.1.1.2.01.0.0 - Imposto sobre a Propriedade Territorial Rural', 
            '1.1.1.3.00.0.0 - Impostos sobre a Renda e Proventos de Qualquer Natureza',
            '1.1.1.3.03.1.0 - Imposto sobre a Renda - Retido na Fonte – Trabalho',
            '1.1.1.3.03.2.0 - Imposto sobre a Renda - Retido na Fonte – Capital',
            '1.1.1.3.03.3.0 - Imposto sobre a Renda - Retido na Fonte - Remessa ao Exterior',
            '1.1.1.3.03.4.0 - Imposto sobre a Renda - Retido na Fonte - Outros Rendimentos',
            '1.1.1.8.01.1.0 - Imposto sobre a Propriedade Predial e Territorial Urbana',
            '1.1.1.8.01.4.0 - Imposto sobre Transmissão ¿Inter Vivos¿ de Bens Imóveis e de Direitos Reais sobre Imóveis',
            '1.1.1.8.02.1.0 - Imposto sobre Operações Relativas à Circulação de Mercadorias e sobre Prestações de Serviços de Transporte Interestadual e Intermunicipal e de Comunicação',
            '1.1.1.8.02.3.0 - Imposto sobre Serviços de Qualquer Natureza',
            '1.1.1.8.02.4.0 - Adicional ISS - Fundo Municipal de Combate à Pobreza',
            '1.1.1.8.02.5.0 - Imposto sobre Vendas a Varejo de Combustíveis Líquidos e Gasosos (IVVC)',
            '1.1.2.1.00.0.0 - Taxas pelo Exercício do Poder de Polícia',
            '1.1.2.1.01.0.0 - Taxas de Inspeção, Controle e Fiscalização',
            '1.1.2.1.02.0.0 - Taxas de Fiscalização das Telecomunicações',
            '1.1.2.1.03.0.0 - Taxa de Controle e Fiscalização de Produtos Químicos',
            '1.1.2.1.04.0.0 - Taxa de Controle e Fiscalização Ambiental',
            '1.1.2.1.05.0.0 - Taxa de Controle e Fiscalização da Pesca e Aquicultura',
            '1.1.2.2.01.0.0 - Taxas pela Prestação de Serviços',
            '1.1.2.2.02.0.0 - Emolumentos e Custas Judiciais',
            '1.1.3.8.00.0.0 - Contribuição de Melhoria - Específica de Estados, DF e Municípios',
            '1.2.1.0.01.0.0 - Contribuição para o Financiamento da Seguridade Social – COFINS',
            '1.2.1.0.02.0.0 - Contribuição Social sobre o Lucro Líquido – CSLL',
            '1.2.1.0.03.0.0 - Contribuições para o Regime Geral de Previdência Social – RGPS',
            '1.2.1.0.04.1.0 - Contribuição Patronal de Servidor Ativo Civil para o RPPS',
            '1.2.1.0.04.2.0 - Contribuição do Servidor Ativo Civil para o RPPS',
            '1.2.1.0.04.3.0 - Contribuição do Servidor Inativo para o RPPS',
            '1.2.1.0.04.4.0 - Contribuição do Pensionista para o RPPS',
            '1.2.1.0.04.5.0 - Contribuição Patronal para o RPPS Oriunda de Sentenças Judiciais',
            '1.2.1.0.04.6.0 - Contribuição do Servidor Ativo ao RPPS Oriunda de Sentenças Judiciais',
            '1.2.1.0.04.7.0 - Contribuição do Servidor Inativo ao RPPS Oriunda de Sentenças Judiciais',
            '1.2.1.0.04.8.0 - Contribuição do Pensionista ao RPPS Oriunda de Sentenças Judiciais',
            '1.2.1.0.06.1.0 - Contribuição para os Fundos de Assistência Médica - Policiais Militares',
            '1.2.1.0.06.2.0 - Contribuição para os Fundos de Assistência Médica dos Bombeiros Militares',
            '1.2.1.0.06.3.0 - Contribuição para os Fundos de Assistência Médica dos Servidores Civis',
            '1.2.1.0.06.9.0 - Contribuição para os Fundos de Assistência Médica de Outros Beneficiários',
            '1.2.1.0.09.0.0 - Contribuição para os Programas de Integração Social e de Formação do Patrimônio do Servidor Público - PIS e PASEP',
            '1.2.1.0.10.0.0 - Cota-Parte da Contribuição Sindical',
            '1.2.1.0.11.0.0 - Contribuições Referentes ao Fundo de Garantia do Tempo de Serviço – FGTS',
            '1.2.1.0.12.0.0 - Contribuição Social do Salário-Educação',
            '1.2.1.0.99.0.0 - Outras Contribuições Sociais',
            '1.2.1.8.01.1.0 - Contribuição Previdenciária para Amortização do Déficit Atuarial',
            '1.2.1.8.01.2.0 - Contribuição Patronal dos Servidores Civis Inativos',
            '1.2.1.8.01.3.0 - Contribuição Patronal dos Pensionistas Civis',
            '1.2.1.8.02.2.0 - Contribuição do Militar Ativo',
            '1.2.1.8.02.3.0 - Contribuição do Militar Inativo',
            '1.2.2.8.00.0.0 - Contribuições Econômicas Específicas de EST/DF/MUN',
            '1.2.3.0.00.0.0 - Contribuições para Entidades Privadas de Serviço Social e de Formação Profissional',
            '1.2.4.0.00.0.0 - Contribuição para o Custeio do Serviço de Iluminação Pública',
            '1.1.1.0.00.0.0 - Impostos',
            '1.1.2.0.00.0.0 - Taxas',
            '1.2.0.0.00.0.0 - Contribuições']

iv = ['1.1.1.2.01.0.0 - Imposto sobre a Propriedade Territorial Rural',
      '1.1.1.3.03.0.0 - Imposto sobre a Renda - Retido na Fonte',
      '1.1.1.8.01.1.0 - Imposto sobre a Propriedade Predial e Territorial Urbana',
      '1.1.1.8.01.4.0 - Imposto sobre Transmissão ¿Inter Vivos¿ de Bens Imóveis e de Direitos Reais sobre Imóveis',
      '1.1.1.0.00.0.0 - Impostos',
      '1.1.2.0.00.0.0 - Taxas',
      '1.2.0.0.00.0.0 - Contribuições']

def sinconfi_ihh(df1,df2):
    df_mun = df1.query('Conta in @tributos')
    df_mun['Cod.IBGE'] = df_mun['Cod.IBGE'].astype(np.int64)
    df_mun = database.merge(df_mun, how='left', on = ['Cod.IBGE','UF'])
    df_mun = df_mun[['Município','UF','Conta','Valor']]
    
    df_uf = df2.query('Conta in @tributos')
    df_uf = df_uf[df_uf['UF'] == 'DF']
    df_uf['Município'] = ['BRASILIA'] * len(df_uf)
    df_uf = df_uf[['Município','UF','Conta','Valor']]
    
    df_ihh = df_mun.append(df_uf).reset_index(drop=True)
    df_ihh = df_ihh.pivot_table(index=['Município','UF'], columns='Conta', values='Valor',
                                aggfunc=np.sum,fill_value=0)
    
    df_ihh['Total I + T + C'] = df_ihh['1.1.1.0.00.0.0 - Impostos'] + df_ihh['1.1.2.0.00.0.0 - Taxas'] + df_ihh['1.2.0.0.00.0.0 - Contribuições']
    del df_ihh['1.1.1.0.00.0.0 - Impostos']
    del df_ihh['1.1.2.0.00.0.0 - Taxas']
    del df_ihh['1.2.0.0.00.0.0 - Contribuições']
    df_ihh = df_ihh.apply(lambda x: x/df_ihh['Total I + T + C'])
    df_ihh = df_ihh.apply(np.square)
    del df_ihh['Total I + T + C']
    df_ihh['IHH'] = df_ihh.sum(axis=1)
      
    globals()['df_ihh'] = df_ihh['IHH'].to_frame()
    
sinconfi_ihh(sinconfi_mun, sinconfi_uf)

def sinconfi_iv(df1,df2):
    df1 = df1.query('Conta in @iv')
    df1 = df1[df1['Coluna'] == 'Receitas Brutas Realizadas']
    df1['Cod.IBGE'] = df1['Cod.IBGE'].astype(np.int64)
    df1 = database.merge(df1, how='left', on = ['Cod.IBGE','UF'])
    df1 = df1[['Município','UF','Conta','Valor']].dropna()

    df2 = df2.query('Conta in @iv')
    df2 = df2[df2['Coluna'] == 'Receitas Brutas Realizadas']
    df2 = df2[df2['UF'] == 'DF']
    df2['Município'] = ['BRASILIA'] * len(df2)
    df2 = df2[['Município','UF','Conta','Valor']]

    df3 = df1.append(df2).reset_index(drop=True)
    df3 = df3.pivot_table(index=['Município','UF'], columns='Conta', values='Valor',
                          fill_value=0, aggfunc=np.sum)
    df3['Total Impostos'] = df3['1.1.1.2.01.0.0 - Imposto sobre a Propriedade Territorial Rural'] + df3['1.1.1.3.03.0.0 - Imposto sobre a Renda - Retido na Fonte'] + df3['1.1.1.8.01.1.0 - Imposto sobre a Propriedade Predial e Territorial Urbana'] + df3['1.1.1.8.01.4.0 - Imposto sobre Transmissão ¿Inter Vivos¿ de Bens Imóveis e de Direitos Reais sobre Imóveis']
    del df3['1.1.1.2.01.0.0 - Imposto sobre a Propriedade Territorial Rural']
    del df3['1.1.1.3.03.0.0 - Imposto sobre a Renda - Retido na Fonte']
    del df3['1.1.1.8.01.1.0 - Imposto sobre a Propriedade Predial e Territorial Urbana'] 
    del df3['1.1.1.8.01.4.0 - Imposto sobre Transmissão ¿Inter Vivos¿ de Bens Imóveis e de Direitos Reais sobre Imóveis']
    df3['Total I + T + C'] = df3['1.1.1.0.00.0.0 - Impostos'] + df3['1.1.2.0.00.0.0 - Taxas'] + df3['1.2.0.0.00.0.0 - Contribuições']
    del df3['1.1.1.0.00.0.0 - Impostos']
    del df3['1.1.2.0.00.0.0 - Taxas']
    del df3['1.2.0.0.00.0.0 - Contribuições']
    df3['ind_v'] = df3['Total Impostos']/df3['Total I + T + C']
    
    globals()['df_iv'] = df3['ind_v'].to_frame()
    
sinconfi_iv(sinconfi_mun, sinconfi_uf)

ind_simpli_tri = df_ihh.merge(df_iv, how='left', on=['Município','UF'])

ind_simpli_tri['Simplicidade Tributária'] = ind_simpli_tri['IHH']*ind_simpli_tri['ind_v']



