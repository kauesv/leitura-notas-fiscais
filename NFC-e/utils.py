import re

def valida_nfce(link):
    """
    Exemplo de url: https://www.nfce.fazenda.sp.gov.br/
    """
    padrao_url = re.compile('(http(s)?://)?(www.)?nfce.fazenda.sp.gov.br/')
    match = padrao_url.match(link)

    # --------
    #   Retorna o resultado
    if not match:
        return False
    else:
        return True