library("data.table")
library("tidyverse")
library("psych")

det <- c("ACESSO A CAPITAL","AMBIENTE REGULATÓRIO","CAPITAL HUMANO","CULTURA",
         "INFRAESTRUTURA","INOVACAO","MERCADO")
det_s <- c("ACESSO_CAPITAL","AMBIENTE_REGULATORIO","CAPITAL_HUMANO","CULTURA",
           "INFRAESTRUTURA","INOVACAO","MERCADO")
last_col <- c(7,16,13,12,12,14,11)

arq <- list()
names <- list()
df <- list()

for(i in 1:7){
  # Importando a base
  arq[i] <- paste0("DETERMINANTES/det-",det[i],".csv")
  names[i] <- paste0("det_",det_s[i])
  df[[i]] <- assign(paste0("det_",det_s[i]), drop_na(fread(arq[[i]],select = c(1:2,last_col[i]),encoding = 'UTF-8')))
}

determinantes <- df %>% 
  reduce(full_join, by=c('V1','V2'))

colnames(determinantes)[1:2] <- c("Município","UF")

S <- cov(determinantes[,3:9])
S.eigen <- eigen(S)
S.eigen$values
plot(S.eigen$values, xlab = 'Eigenvalue Number', ylab = 'Eigenvalue Size', main = 'Scree Graph', type = 'b', xaxt = 'n')
axis(1, at = seq(1, 7, by = 1))

root.fa.covar <- principal(determinantes[,3:9], nfactors = 3, rotate = 'none', covar = TRUE)
root.fa.covar