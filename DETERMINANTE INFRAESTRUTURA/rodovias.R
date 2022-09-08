#
#
# SD 21 - INFRAESTRUTURA - TRANSPORTE INTERURBANO

library(tidyverse)
library(geobr)
library(sf)
# rodovias ----------------------------------------------------------------
# federais
# unzip(
#   "infraestrutura/rodovias/vw_snv_rod.zip",
#   exdir = "infraestrutura/rodovias/fedroads_shapefile",
#   junkpaths = TRUE,
#   overwrite = TRUE
# )
# 
# br <-
#   sf::st_read("infraestrutura/rodovias/fedroads_shapefile/vw_snv_rod.shp",
#               as_tibble = TRUE) %>%
#   select(codigo = Codigo_BR, geometry) %>%
#   mutate(codigo = paste0("br_", codigo))
# 
# # estaduais
# unzip(
#   "infraestrutura/rodovias/vw_cide_rod.zip",
#   exdir = "infraestrutura/rodovias/estroads_shapefile",
#   junkpaths = TRUE,
#   overwrite = TRUE
# )
# 
# er <-
#   st_read("infraestrutura/rodovias/estroads_shapefile/vw_cide_rod.shp",
#           as_tibble = T) %>%
#   select(codigo = Codigo_Rod, geometry) %>%
#   mutate(codigo = paste0("es_", codigo))
# # rodovias federais e estaduais
# roads <- bind_rows(br, er)

roads <- st_read("estroads_shapefile/SNV_202206A.shp",
as_tibble = T)

# localizao dos municipios ------------------------------------------------
municode <-
  read_csv("municode.csv") %>% select(id_municipio, sigla_uf, nome)

m <- geobr::read_municipality() %>%
  select(id_municipio = 1, geom) %>%
  right_join(municode) %>%
  select(id_municipio, sigla_uf, nome, geom) %>%
  st_as_sf()

p <- geobr::read_state() %>%
  ggplot() +
  geom_sf(
    fill = "white",
    color = "grey",
    size = .15,
    show.legend = F
  ) +
  geom_sf(data = m, fill = "#2D3E50") +
  geom_sf(data = roads %>% sample(1), color = "#FEBF57") +
  theme(
    panel.background = element_blank(),
    axis.title = element_blank(),
    axis.text = element_blank(),
    axis.ticks = element_blank()
  )

ggsave("exemplo_rodovia.png", p)

# funcoes auxiliares ------------------------------------------------------
roads_inteiras <- roads %>% split(.$vl_codigo)

passam <- function(r) {
  i <- 1:100
  muninterr <- function(i) {
    # verifica se municipio m intersecta algum trecho da rodovia r
    st_intersects(m[i, ], r, sparse = FALSE) %>% any()
  }
  i %>% map(possibly(muninterr, "erro"))
}

recebem <- roads_inteiras %>% map(passam)
# intersecao rodovias e municipios ----------------------------------------

df2 <- recebem %>% map_dfc(unlist) %>%
  #filter(!str_detect('erro', 'REVERSE')) %>% # exclui Rio Branco
  mutate(across(where(is.character), as.logical)) %>%
  rowwise() %>%
  mutate(n_estradas = sum(c_across(everything()))) %>%
  add_column(id_municipio = m$id_municipio[-2], .before = 1)

df_final1 <- df2 %>% select(1, ncol(df2)) %>%
  left_join(municode) %>%
  select(id_municipio, sigla_uf, nome, i211 = n_estradas) %>%
  add_row(
    id_municipio = 1200401,
    sigla_uf = "AC",
    nome = "Rio Branco",
    i211 = 4
  ) %>%
  add_row(
    id_municipio = 1302603,
    sigla_uf = "AM",
    nome = "Manaus",
    i211 = 3
  ) %>% drop_na()

write_csv(df, "sd22_rodovias.csv")
