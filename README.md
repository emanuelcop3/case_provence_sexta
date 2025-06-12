# ANBIMA XML Parser

Aplicação web para processar e visualizar arquivos XML da ANBIMA (versão 4.0.1).

## Funcionalidades

- Upload e processamento de arquivos XML da ANBIMA
- Visualização da composição da carteira por tipo de ativo
- Visualização da composição por ativo individual
- Validações automáticas:
  - Data de posição
  - Soma dos percentuais
  - Conferência do PL com valor total das posições + provisões
- Exibição de provisões e saldo em caixa

## Requisitos

- Python 3.8+
- Flask
- lxml
- pandas
- python-dateutil

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Inicie o servidor:
```bash
python app.py
```

2. Acesse a aplicação em seu navegador:
```
http://localhost:5000
```

3. Faça upload do arquivo XML da ANBIMA

## Estrutura do Projeto

- `app.py`: Aplicação principal Flask
- `templates/index.html`: Interface web
- `requirements.txt`: Dependências do projeto

## Validações

A aplicação realiza as seguintes validações:

1. Data de posição válida
2. Soma dos percentuais igual a 100%
3. Valor total das posições + provisões igual ao PL

## Contribuição

Sinta-se à vontade para contribuir com melhorias através de pull requests. 