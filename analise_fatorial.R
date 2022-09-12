# Bibliotecas utilizadas no R
library("data.table")
library("tidyverse")
library("psych")
install.packages(psych)

#-------------------------------------------------------------------------------
# Criando looping para importar os indicadores padronizados
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

#-------------------------------------------------------------------------------
## AnÃ¡lise fatorial: fatores e autovalores

S <- cov(determinantes[,3:9])
S.eigen <- eigen(S)
S.eigen$values
plot(S.eigen$values, xlab = 'Fatores', ylab = 'Eigenvalue', type = 'b', xaxt = 'n',
     main='Eigenvalues X Fatores')
axis(1, at = seq(1, 7, by = 1))

# Criando tabela com a AnÃ¡lise dos Principais Componentes 
root.fa.covar <- principal(determinantes[,3:9], nfactors =3, rotate = 'none', covar = TRUE)
root.fa.covar$uniquenesses
root.fa.covar$rot.mat
root.fa.covar

# Criando tabela com a AnÃ¡lise dos Principais Componentes 
root.fa.covar <- principal(determinantes[,3:9], nfactors =3, rotate = 'quartimax', covar = TRUE)
root.fa.covar$uniquenesses
root.fa.covar$rot.mat
root.fa.covar

# ICE 23: soma os scores para os trÃªs fatores gerados pela anÃ¡lise fatorial
scores.ICE <- as.data.frame(psych::predict.psych(root.fa.covar, determinantes[,3:9]))
scores.ICE$`Município` <- determinantes$Município
scores.ICE$UF <- determinantes$UF
scores.ICE <- scores.ICE %>%
  mutate(ICE = RC1 + RC2 + RC3,
         ICE = (ICE - mean(ICE))/sd(ICE) + 6)

write.csv(scores.ICE, 'DETERMINANTES/scores-ICE-23.csv')

ICE_23 <- cbind(determinantes,scores.ICE[,6])
names(ICE_23)[10] <- 'Índice Cidades Empreendendoras 2023'

ICE_23$`Rank ICE 23` <- frankv(ICE_23, cols='Índice Cidades Empreendendoras 2023', order=-1)
ICE_23$`Rank Acesso a Capital` <- frankv(ICE_23, cols='Índice de Acesso a Capital', order=-1)
ICE_23$`Rank Ambiente RegulatÃ³rio` <- frankv(ICE_23, cols='Índice de Ambiente Regulatório', order=-1)
ICE_23$`Rank Capital Humano` <- frankv(ICE_23, cols='Índice de Capital Humano', order=-1)
ICE_23$`Rank Cultura` <- frankv(ICE_23, cols='Índice de Cultura', order=-1,ties.method = "max")
ICE_23$`Rank Infraestrutura` <- frankv(ICE_23, cols='Índice de Infraestrutura', order=-1)
ICE_23$`Rank InovaÃ§Ã£o` <- frankv(ICE_23, cols='Índice de Inovação', order=-1)
ICE_23$`Rank Mercado` <- frankv(ICE_23, cols='Índice de Mercado', order=-1)

ICE_23 <- ICE_23[, c(1:3,12,4,13,5,14,6,15,7,16,8,17,9,18,10,11)]

write.csv(ICE_23, 'DETERMINANTES/ICE-2023.csv')

# Teste KMO
kmo <- KMO(determinantes[,3:9])
kmo

