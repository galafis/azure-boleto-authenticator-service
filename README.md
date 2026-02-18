# Servico Autenticador de Boletos Bancarios com Azure Functions

## Sobre o Projeto

Este projeto implementa um servico serverless para verificacao e autenticacao de boletos bancarios utilizando Azure Functions. O objetivo e garantir a validade das informacoes contidas nos codigos de barras dos boletos, incluindo validacao de digitos verificadores, identificacao de bancos emissores e decodificacao de informacoes como valor e data de vencimento.

## Arquitetura da Solucao

```
[Cliente/UI] --> [Azure Functions HTTP Trigger]
                        |
            +-----------+-----------+
            |                       |
    [fnValidaBoleto]      [fnGeradorBoletos]
            |                       |
    - Decodifica barcode    - Gera boleto teste
    - Valida digitos        - Encode codigo barras
    - Retorna dados         - Retorna boleto
```

### Componentes Principais

1. **fnValidaBoleto** - Azure Function responsavel por receber o codigo de barras, decodificar e validar as informacoes do boleto
2. **fnGeradorBoletos** - Azure Function para geracao de boletos de teste para validacao do servico
3. **Front-end (UI)** - Interface web para interacao com o usuario, permitindo entrada do codigo e visualizacao dos resultados

## Tecnologias Utilizadas

| Tecnologia | Finalidade |
|---|---|
| Azure Functions | Computacao serverless para processamento dos boletos |
| C# / .NET 8 | Linguagem e framework para as Azure Functions |
| HTML/CSS/JS | Interface do usuario (camada de UI) |
| Azure Portal | Gerenciamento e monitoramento dos recursos |

## Funcionalidades

- Validacao do codigo de barras de boletos bancarios (47 digitos)
- Decodificacao do campo livre para extrair informacoes do banco emissor
- Calculo e verificacao do digito verificador (modulo 10 e modulo 11)
- Identificacao do banco emissor pelo codigo (001-BB, 033-Santander, 104-CEF, 237-Bradesco, 341-Itau, etc.)
- Extracao do valor do boleto a partir do codigo de barras
- Extracao da data de vencimento (fator de vencimento)
- Interface web intuitiva para entrada do codigo e exibicao dos resultados
- API REST via HTTP Trigger para integracao com outros sistemas

## Estrutura do Projeto

```
azure-boleto-authenticator-service/
|-- fnGeradorBoletos/
|   |-- fnGeradorBoletos/       # Function para geracao de boletos
|   |   |-- Function1.cs
|   |   |-- Program.cs
|   |   |-- host.json
|   |-- fnValidaBoleto/         # Function para validacao de boletos
|   |   |-- Function1.cs
|   |   |-- Program.cs
|   |   |-- host.json
|   |-- fnGeradorBoletos.sln    # Solution .NET
|-- Front/                      # Interface do usuario
|   |-- index.html
|   |-- style.css
|   |-- script.js
|-- README.md
```

## Como Executar

### Pre-requisitos
- .NET 8 SDK
- Azure Functions Core Tools v4
- Visual Studio 2022 ou VS Code com extensao Azure Functions
- Conta no Azure (para deploy)

### Execucao Local

```bash
# Clonar o repositorio
git clone https://github.com/galafis/azure-boleto-authenticator-service.git
cd azure-boleto-authenticator-service

# Restaurar dependencias e executar
cd fnGeradorBoletos
dotnet restore
func start
```

### Deploy no Azure

```bash
# Login no Azure
az login

# Criar resource group
az group create --name rg-boleto-auth --location brazilsouth

# Criar storage account
az storage account create --name stboletofunc --resource-group rg-boleto-auth --location brazilsouth --sku Standard_LRS

# Criar function app
az functionapp create --name fn-boleto-authenticator --resource-group rg-boleto-auth --storage-account stboletofunc --consumption-plan-location brazilsouth --runtime dotnet-isolated --functions-version 4

# Deploy
func azure functionapp publish fn-boleto-authenticator
```

## Insights e Aprendizados

- **Serverless Architecture**: Azure Functions no plano de consumo escala automaticamente para zero quando nao ha requisicoes, reduzindo custos drasticamente
- **HTTP Triggers**: Permitem expor as functions como APIs REST, facilitando integracao com front-end e sistemas externos
- **Managed Identity**: Possibilita conexao segura entre functions e outros servicos Azure sem necessidade de gerenciar credenciais
- **Modulo 10 e 11**: Algoritmos fundamentais para validacao de boletos bancarios no Brasil, garantindo integridade dos dados
- **Cold Start**: No plano de consumo, a primeira requisicao pode ter latencia maior devido ao cold start - para aplicacoes criticas, considerar plano Premium

## Referencia

- [Repositorio Original DIO](https://github.com/digitalinnovationone/Microsoft_Application_Platform)
- [Documentacao Azure Functions](https://learn.microsoft.com/azure/azure-functions/)
- [Especificacao Boleto Bancario - FEBRABAN](https://portal.febraban.org.br/)

## Autor

Desenvolvido como parte do bootcamp **Microsoft Azure Cloud Native** na [DIO](https://www.dio.me/).
