import pandas as pd
import numpy as np

# 3.1. Tratamento para Indicadores com Impacto Negativo no Empreendedorismo

def negative(series):
    
    series = 1/series
    
    return series.replace(np.inf, 0)

# 3.2. Tratamento para Observações Faltantes (missing data)

def missing_data(df):
    
    ind = pd.read_excel('Arquivos ICE - 23/Ind_Originais_ICE_2022.xlsx')
    ind.columns = ind.iloc[1]
    ind.columns.values[0] = 'Município'
    ind = ind.set_index('Município')
    ind = ind.tail(101)
    
    for c in df.columns:
        if c in ind.columns:
            if df[c].isna().sum()/len(df) > 0.3:
                df[c].fillna(ind[c], inplace=True)
        
        df[c].fillna(0)
                
    return df

# 3.3. Tratamento para Valores Extremos

def extreme_values(df):
    
    for c in df.columns:
    
        top_values = [i for i in df[c] if i > df[c].quantile(0.98)]
        bottom_values = [i for i in df[c] if i < df[c].quantile(0.02)]
        removed = []

        if len(top_values) > 1:
            for i in top_values:
                nlist = [t for t in top_values if t != i]
                if i >= 5*sum(nlist)/(len(nlist)):
                    removed.append(i)

        if len(top_values) > 1:
            for j in bottom_values:
                if i <= 5*sum(top_values.remove(i))/(len(top_values)-1):
                    removed.append(j)

        for r in df.index:
            if df.loc[r,c] in removed:
                df.iat[r,c] = 0
            
    return df

# 3.4. Padronização de Indicadores

def normalize(series):
    return (series - series.mean())/series.std()

def create_subindex(df, subdet):
    
    i_name = 'Índice de '+subdet
    
    if i_name not in df.columns:
        norm_data = df.apply(lambda x: normalize(x), axis=0)
        df[i_name] = normalize(norm_data.sum(axis=1)) + 6
    
    return df

def create_detindex(df, det):
    
    d_name = 'Índice de ' + det
    det_df = pd.DataFrame()
    
    if d_name not in df.columns:
        for i in (df.columns.levels[0]):
            det_df[i] = df[i,(df[i].columns[-1])]

        det_df = det_df.apply(lambda x: normalize(x), axis=0)
        det_df[d_name] = normalize(det_df.sum(axis=1)) + 6
        df[d_name] = det_df[d_name]
    
    return df