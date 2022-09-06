#SD22 - PRECO DO METRO QUADRADO ------------------------------------------
  # bibliotecas -------------------------------------------------------------
library(httr)
library(tidyverse)
library(basedosdados)
library(abjutils)
# funcao para baixar dados do site ----------------------------------------
get_muni <- function(uf, muni) {
  # import data-----------------------------------------------------------------
  u <- "https://glue-api.zapimoveis.com.br/v2/listings"
  query <- list(
    business = "SALE",
    categoryPage = "RESULT",
    includeFields = "search",
    listingType = "USED",
    addressState = uf,
    addressCity = muni,
    portal = "ZAP",
    addressType = "city",
    size = "350"
  )
  
  h <- httr::add_headers("X-domain" = "www.zapimoveis.com.br")
  resultado <- GET(u, query = query, h) %>%
    content() %>%
    pluck("search", "result", "listings")
  # explore -----------------------------------------------------------------
  # substitui NULL (ausencia de dado) por NA (indica que nao ha dado)
  nullToNA <- function(x) {
    x[unlist(map(x, is.null))] <- NA
    return(x)
  }
  area <- resultado %>%
    map( ~ pluck(., "listing", "usableAreas")) %>%
    nullToNA() %>%
    unlist() %>%
    as.numeric()
  endereco <- resultado %>%
    map( ~ pluck(., "listing", "address", "locationId")) %>%
    nullToNA() %>%
    unlist()
  # pre?os
  get_price <- function(x) {
    unlist(price[[x]])['price']
  }
  price <- resultado %>%
    map( ~ pluck(., "listing", "pricingInfos")) %>%
    nullToNA()
  pricef <- seq_along(price) %>% map(get_price) %>%
    unlist() %>%
    as.numeric()
  # tudo junto
  imoveis <-
    tibble(endereco = endereco,
           price = pricef,
           area = area)
  imoveis
}
# importa dados dos municipios --------------------------------------------
set_billing_id("double-balm-306418")
nome_uf <- read_sql(
  "SELECT id_municipio, nome_uf
FROM `basedosdados.br_bd_diretorios_brasil.municipio`"
  
)
municode <- read_csv("municode.csv") %>%
  mutate(id_municipio = as.character(id_municipio)) %>%
  left_join(nome_uf) %>%
  select(id_municipio, nome_uf, nome)
# raspa os dados para cada municipio --------------------------------------
terrenos <- map2_dfr(municode$nome_uf, municode$nome, get_muni)
# organiza e exclui dados faltanes
terrenos_final <- terrenos %>%
  filter(area != 0 & !is.na(area)) %>%
  separate(
    endereco,
    sep = ">",
    into = c("pa?s", "nome_uf", "NULL", "nome", "bairro"),
    extra = "merge"
  ) %>%
  select(nome_uf, nome, bairro, price, area)
gabarito <- terrenos_final %>%
  mutate(`m^2` = price / area) %>%
  arrange(-`m^2`)
df <- terrenos_final %>%
  mutate(m2 = price / area) %>%
  filter(between(m2, 100, 20000)) %>%
  group_by(nome_uf, nome) %>%
  summarise(
    price_total = sum(price, na.rm = TRUE),
    area_total = sum(area),
    amostra = n(),
    m2 = price_total / area_total
  )
df_final <- municode %>%
  mutate(across(everything(), rm_accent)) %>%
  left_join(df) %>%
  mutate(s22_m2 = 1 / m2)
write_excel_csv(df_final, "infraestrutura/terrenos/sd22_m2_completo.xlsx")
terrenos <- read_excel("infraestrutura/terrenos/sd22_m2_completo.xlsx")%>%
  mutate(m2 = as.double(m2),
         s22_m2 = as.double(s22_m2)) %>%
  rename(i222 = s22_m2)

i222_completo <- municode %>%
  select(id_municipio,sigla_uf) %>%
  left_join(terrenos) %>%
  select(-nome_uf) %>%
  arrange(id_municipio)
write_csv(i222_completo, "infraestrutura/i222.csv")
i222_completo %>% select(1:3,8) %>%
  write_csv("dados_finais/i222.csv")