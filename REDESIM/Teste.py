"""
Created on Tue Aug  9 19:56:59 2022

@author: CLIENTE
"""
import pandas as pd

sequence = list(range(1,8))
arq = 'C:/Users/CLIENTE/OneDrive/Área de Trabalho/Pesquisa - PUC Rio/ICE-23/REDESIM/'

my_dfs = {}
for x in sequence:
    my_dfs[x] = pd.read_excel(f"{arq}tempos-abertura-Brasil{x}2022.xlsx", 
                              header = None)

