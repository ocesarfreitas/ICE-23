import pandas as pd
import numpy as np
from funcs import *

# 2.2. DETERMINANTE AMBIENTE REGULATÓRIO

# ---------------------------------------------------------------------------------------------
# 2.2.1. SUBDETERMINANTE TEMPO DE PROCESSOS
subdet = 'Tempo de processos'

def read_excel(filenames):
    return pd.read_excel(filenames, header = 1, usecols = "I,R,AA")
    
if __name__ == "__main__":
    files = glob.glob("DETERMINANTE AMBIENTE REGULATÓRIO/REDESIM/*.xlsx")

    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        data = pool.map(read_excel, files)
        sub_tempo_pro = pd.concat(data)

# ---------------------------------------------------------------------------------------------
# 2.2.2. SUBDETERMINANTE TRIBUTAÇÃO
