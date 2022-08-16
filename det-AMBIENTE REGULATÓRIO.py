import pandas as pd
# import numpy as np
from funcs import *
import glob

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
"Eu sei que isso tá feio e ineficiente amg kkkk"

subdet = 'Tempo de processos'

def read_excel(filename):
    pd.read_excel(filename, header=1, usecols="I,R,AA,AB")

if __name__ == '__main__':
    files = glob.glob("DETERMINANTE AMBIENTE REGULATÓRIO/REDESIM/*.xlsx")
    parc_indicador = [read_excel(filename) for filename in files]
    indicador = pd.concat(parc_indicador)

def read_csv(filename):
    pd.read_csv(filename)

if __name__ == '__main__':
    files = glob.glob("DETERMINANTE AMBIENTE REGULATÓRIO/CNJ/*.csv")
    parc_indicador_temp = [read_csv(filename) for filename in files]
    indicador_tempo = pd.concat(parc_indicador)    
# ---------------------------------------------------------------------------------------------
# 2.2.2. SUBDETERMINANTE TRIBUTAÇÃO
