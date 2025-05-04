import re


def limpar_texto_plain(texto_completo: str) -> str:
    texto_sem_links = re.sub(r'https?://\S+', '', texto_completo)
    texto_plain = re.sub(r'\n+|\s+', ' ', texto_sem_links)

    return texto_plain.strip()


def limpar_texto_html(texto_completo: str) -> str:
    texto_html = re.sub(r'\n+|\s+', ' ', texto_completo)

    return texto_html.strip()
