library(data.table)
library(tidyverse)

municode <- read_csv("municode.csv") %>%
  select(id_municipio, sigla_uf, nome) %>%
  mutate(nome = str_to_title(nome))

df_anac <- data.table::fread(file='Dados_Estatisticos.csv',sep=';') #%>% filter(ANO == 2021, AEROPORTO_DE_ORIGEM_PAIS == "BRASIL", AEROPORTO_DE_ORIGEM_SIGLA == 'SBBH')

voos_br <- df_anac %>%
  as_tibble() %>%
  select(ANO, MES, contains("AEROPORTO_DE_ORIGEM"), GRUPO_DE_VOO, DECOLAGENS) %>%
  filter(ANO == 2020, AEROPORTO_DE_ORIGEM_PAIS == "BRASIL",
         GRUPO_DE_VOO == "REGULAR") %>%
  rename(sigla_aero = AEROPORTO_DE_ORIGEM_SIGLA, nome = AEROPORTO_DE_ORIGEM_NOME,
         sigla_uf = AEROPORTO_DE_ORIGEM_UF) %>%
  mutate(nome = str_to_title(nome)) %>%
  group_by(sigla_aero, sigla_uf, nome) %>%
  summarise(decolagens = sum(DECOLAGENS, na.rm = TRUE)) %>%
  ungroup()

data.table::fwrite(voos_br,'voos_brasil.csv')
