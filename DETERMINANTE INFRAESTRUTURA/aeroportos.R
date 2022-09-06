###cSD21 - INFRAESTRUTURA - TRANSPORTE INTERURBANO
library(tidyverse)
# voos 2020 -------------------------------------------------------------------
# unzip os dados apenas uma vez
#unzip("infraestrutura/aeroportos/Dados_Estatisticos.zip",
# exdir = "infraestrutura/aeroportos/dados_voos",
# junkpaths = TRUE, overwrite = TRUE)
municode <- read_csv("municode.csv") %>%
  select(id_municipio, sigla_uf, nome) %>%
  mutate(nome = str_to_title(nome))
# voos no mundo
voos <- read.delim("Dados Estatísticos.csv",
                   sep = ";")
# no br
voos_br <- voos %>%
  as_tibble() %>%
  select(ANO,
         MÊS,
         contains("AEROPORTO.DE.ORIGEM"),
         GRUPO.DE.VOO,
         DECOLAGENS) %>%
  filter(ANO == 2021,
         AEROPORTO.DE.ORIGEM..PAÍS. == "BRASIL",
         GRUPO.DE.VOO == "REGULAR") %>%
  rename(sigla_aero = AEROPORTO.DE.ORIGEM..SIGLA.,
         nome = AEROPORTO.DE.ORIGEM..NOME.,
         sigla_uf = AEROPORTO.DE.ORIGEM..UF.) %>%
  mutate(nome = str_to_title(nome),
         sigla_uf = if_else(nome == "Guaíra", "PR", sigla_uf)) %>% # dados errados
  group_by(sigla_aero, sigla_uf, nome) %>%
  summarise(decolagens = sum(DECOLAGENS, na.rm = TRUE)) %>%
  ungroup()
# no br e nos 100 maiores munipios
decolagens <- voos_br %>%
  group_by(sigla_uf, nome) %>%
  summarise(decolagens = sum(decolagens, na.rm = TRUE)) %>%
  ungroup()
decolagens_100maiores <- municode %>%
  left_join(decolagens) %>%
  arrange(nome)
write_csv(decolagens_100maiores, "Decolagens.csv")
deco <- read_csv("Decolagens.csv") %>%
  arrange(id_municipio)
write_csv(deco, "Decolagens.csv")
write_csv(deco, "Decolagens.csv")