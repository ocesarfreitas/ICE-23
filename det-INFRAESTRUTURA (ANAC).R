library(data.table)
library(tidyverse)

df_anac <- data.table::fread(file='DETERMINANTE INFRAESTRUTURA/Dados_Estatisticos.csv',
                             skip=1,header=T,sep=';')

voos_br <- df_anac %>%
  as_tibble() %>%
  select(ANO, MES, contains("AEROPORTO_DE_ORIGEM"), GRUPO_DE_VOO, DECOLAGENS) %>%
  filter(ANO == 2021, AEROPORTO_DE_ORIGEM_PAIS == "BRASIL",
         GRUPO_DE_VOO == "REGULAR") %>%
  rename(sigla_aero = AEROPORTO_DE_ORIGEM_SIGLA, nome = AEROPORTO_DE_ORIGEM_NOME,
         sigla_uf = AEROPORTO_DE_ORIGEM_UF) %>%
  mutate(nome = str_to_title(nome)) %>%
  group_by(sigla_aero, sigla_uf, nome) %>%
  summarise(decolagens = sum(DECOLAGENS, na.rm = TRUE)) %>%
  ungroup()

data.table::fwrite(voos_br,'DETERMINANTE INFRAESTRUTURA/voos_brasil.csv')
