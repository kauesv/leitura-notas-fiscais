from bs4 import BeautifulSoup   #pip3 install beautifulsoup4
import re
import requests
from urls import URLS


# --------
#   
url = URLS[1]

# O headers é para evitar o erro 406
# https://airbrake.io/blog/http-errors/406-not-acceptable
# https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Status/406
headers = {'User-Agent': 'request', 'Accept': '*/*', 'content-type': 'text/html'}
response = requests.get(url, headers=headers)

# --------
#   Se a requisição for bem sucedida
if response.status_code == 200 or response.status_code == 201:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # --------
    #   HTML do estabelecimento
    try:
        html_estabelecimento = soup.find("div", class_="txtCenter")
        
        # --------
        #   nome do estabelecimento
        nome_estabelecimento = html_estabelecimento.find("div", class_="txtTopo").get_text()

        # --------
        #   Para cada class "Text" no HTML
        for text in html_estabelecimento.find_all("div", class_="text"):

            # --------
            #   Sabemos que existe apenas dois texts no HTML se for CNPJ ou não(Endereço)
            if 'CNPJ' in text.get_text():
                cnpj_estabelecimento = text.get_text()
            else:
                endereco = text.get_text()
    except:
        print("ERRO:", exc_info=True)
        raise

    # --------
    #   TRATAMENTO - HTML do estabelecimento
    cnpj_estabelecimento = cnpj_estabelecimento.replace('\t', '').replace('CNPJ:', '').strip()
    endereco = endereco.replace('\t','').replace('\n', '').replace('\r', '').replace(u'\xa0', ' ').strip()

    # --------
    #   HTML dos produtos
    try:
        html_produtos = soup.find("table", id="tabResult")

        list_produtos = []

        # --------
        #   Para cada TR(linha) de produtos
        for produto in html_produtos.find_all("tr"):

            # --------
            #   Nome do produto
            nome = produto.find("span", class_="txtTit").get_text()

            # --------
            #   Codigo do produto
            codigo = produto.find("span", class_="RCod").get_text()

            # --------
            #   Quantidade de produtos comprandos
            qtd = produto.find("span", class_="Rqtd").get_text()
            
            # --------
            #   Unidade de medida
            un = produto.find("span", class_="RUN").get_text()

            # --------
            #   preco unico do produto
            preco = produto.find("span", class_="RvlUnit").get_text()

            # --------
            #   preco total deste produto
            total = produto.find("span", class_="valor").get_text()

            # --------
            #   TRATAMENTO - HTML dos produtos
            codigo = codigo.replace('\t','').replace('(Código:', '').replace(')', '').replace('\n', '').replace('\r', '').replace(u'\xa0', ' ')
            qtd = qtd.replace('\t','').replace('Qtde.:', '').replace('\n', '').replace('\r', '').replace(u'\xa0', ' ')
            un = un.replace('\t','').replace('UN: ', '').replace('\n', '').replace('\r', '').replace(u'\xa0', ' ')
            preco = preco.replace('\t','').replace('Vl. Unit.:', '').replace('\n', '').replace('\r', '').replace(u'\xa0', ' ')
            total = total.replace('\t','').replace('\n', '').replace('\r', '').replace(u'\xa0', ' ')

            # --------
            #   Monta o dicionario
            insert = {
                "nome": nome,
                "codigo": codigo,
                "qtd": qtd,
                "unidade_medida": un,
                "preco_unitario": preco,
                "total_preco": total
            }

            # --------
            #   Adiciona na lista
            list_produtos.append(insert)
    except:
        print("ERRO:", exc_info=True)
        raise

    # --------
    #   HTML dos resultados finais da nota
    try:
        html_resultados_finais = soup.find("div", id="totalNota", class_="txtRight")
        #print(html_resultados_finais)

        # --------
        #   Quantidade diferentes de itens
        qtd_itens = html_resultados_finais.find("span", class_="totalNumb").get_text()

        # --------
        #   Quantidade total da nota
        total_nota = html_resultados_finais.find("span", class_="totalNumb txtMax").get_text()

        # --------
        #   
        forma_pagamento = html_resultados_finais.find("label", class_="tx").get_text()

        # --------
        #   Total de imposto sobre a nota
        imposto = html_resultados_finais.find("span", class_="totalNumb txtObs").get_text()
    except:
        print("ERRO no HTML de resultados finais da nota:", exc_info=True)
        raise

    # --------
    #   TRATAMENTO - HTML dos resultados finais da nota
    qtd_itens = qtd_itens.replace('\t','').replace('\n', '').replace('\r', '')
    total_nota = total_nota.replace('\t','').replace('\n', '').replace('\r', '')
    forma_pagamento = forma_pagamento.replace('\t','').replace('\n', '').replace('\r', '')
    imposto = imposto.replace('\t','').replace('\n', '').replace('\r', '')

    # --------
    #   HTML das Informações gerais da Nota
    try:
        html_info_notas = soup.find("div", id="infos", class_="txtCenter")

        cnpj_consumidor = None
        cpf = None
        nome = None

        for text in html_info_notas.find_all("li"):
            text = text.get_text().replace('\t', '')

            # --------
            #   CPF
            if 'CPF:' in text:
                cpf = text
            # --------
            #   CNPJ
            elif 'CNPJ:' in text:
                cnpj_consumidor = text
            # --------
            #   Nome
            elif 'Nome:' in text:
                nome = text
            # --------
            #   Numero
            elif 'Emissão' in text:
                numero = re.search('Número: (.+?) Série:', text).group(1).strip()
                serie = re.search('Série: (.+?) Emissão:', text).group(1).strip()
                emissao = re.search('Emissão: (.+?) [0-9]{2}:[0-9]{2}:[0-9]{2}', text).group(0).replace('Emissão:', '').strip()
                protocolo = re.search('Protocolo de Autorização: (.+?) [0-9]{2}', text).group(1).strip()

        chave_acesso = html_info_notas.find("span", class_="chave").get_text()
    except:
        print("ERRO:", exc_info=True)
        raise

    # --------
    #   TRATAMENTO - HTML das Informações gerais da Nota
    if cpf:
        cpf = cpf.replace('CPF:', '').strip()
    if cnpj_consumidor:
        cnpj_consumidor = cnpj_consumidor.replace('CNPJ:', '').strip()
    if nome:
        nome = nome.replace('Nome:', '').strip()
else:
    print("ERRO:", exc_info=True)



print('Estabelecimento: ', cnpj_estabelecimento)
print('CNPJ: ', cnpj_estabelecimento)
print('Endereço: ', endereco)


print(f'Produtos: {list_produtos}')


print('Quantidades diferentes de itens: ', qtd_itens)
print('Quantidade total da nota: ', total_nota)
print('forma pagamento: ', forma_pagamento)
print('Imposto: ', imposto)


print('Nome consumidor: ', nome)
print('cpf_consumidor: ', cpf)
print('cnpj_consumidor: ', cnpj_consumidor)


print('numero: ', numero)
print('serie: ', serie)
print('emissao: ', emissao)
print('protocolo: ', protocolo)
print('Chave de acesso: ', chave_acesso)