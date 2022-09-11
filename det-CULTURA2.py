import pandas as pd
import numpy as np
from funcs import *

# ---------------------------------------------------------------------------------------------
# 1. AMOSTRA

database = pd.DataFrame()
amostra = pd.read_csv('AMOSTRA/100-municipios.csv')
database['Município'] = amostra['NOME DO MUNICÍPIO']
database['UF'] = amostra['UF']
database = database.set_index(['Município', 'UF'])

# ---------------------------------------------------------------------------------------------
# 2.8. DETERMINANTE CULTURA

def save_googletrends(database, term):
    
    name = term.split(' ')[-1].replace('_', ' ')
    term = term.replace('_', ' ')
    c_name = 'Pesquisas '+term
    
    if c_name not in database.columns:
        indicador = pd.read_csv('DETERMINANTE CULTURA/geoMap-'+name+'.csv').reset_index()
        indicador = indicador.rename(columns={'index':'Município', 'Category: All categories': c_name})
        database = database.merge(indicador, how='left',on='Município').fillna(0)
        database[c_name] = database[c_name].astype(int)
    
    return database

cultura = {}

# ---------------------------------------------------------------------------------------------
# 2.8.1. SUBDETERMINANTE INICIATIVA

subdet = 'Iniciativa'

iniciativa = ['pelo Termo Empreendedor', 'pelo Termo MEI']
sub_iniciativa = pd.DataFrame(database)

sub_iniciativa = save_googletrends(sub_iniciativa, 'pelo Termo Empreendedor')
sub_iniciativa = save_googletrends(sub_iniciativa, 'pelo Termo MEI')
sub_iniciativa = sub_iniciativa.set_index('Município')

missing_data(sub_iniciativa)
extreme_values(sub_iniciativa)
create_subindex(sub_iniciativa, subdet)
cultura[subdet] = sub_iniciativa

# ---------------------------------------------------------------------------------------------
# 2.8.2. SUBDETERMINANTE INSTITUIÇÕES

subdet = 'Instituições'

instituicoes = ['por Sebrae', 'por Franquia', 'por SIMPLES_Nacional', 'por Senac']
sub_instituicoes = pd.DataFrame(database)

sub_instituicoes = save_googletrends(sub_instituicoes, 'por Sebrae')
sub_instituicoes = save_googletrends(sub_instituicoes, 'por Franquia')
sub_instituicoes = save_googletrends(sub_instituicoes, 'por SIMPLES_Nacional')
sub_instituicoes = save_googletrends(sub_instituicoes, 'por Senac')
sub_instituicoes = sub_instituicoes.set_index('Município')

missing_data(sub_instituicoes)
extreme_values(sub_instituicoes)
create_subindex(sub_instituicoes, subdet)
cultura[subdet] = sub_instituicoes

# ---------------------------------------------------------------------------------------------
cultura = pd.concat(cultura, axis=1)
cultura
create_detindex(cultura, 'Cultura')

cultura = cultura.reset_index()
cultura['UF'] = amostra['UF']
cultura = cultura.set_index(['Município', 'UF'])


cultura.to_csv('DETERMINANTES/det-CULTURA.csv')