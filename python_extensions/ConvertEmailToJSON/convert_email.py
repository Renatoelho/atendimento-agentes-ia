import re
import base64
from io import BytesIO
from email import policy
from datetime import datetime
from zoneinfo import ZoneInfo
from email.parser import BytesParser

from limpar_texto import limpar_texto_plain
from limpar_texto import limpar_texto_html


regexp_email = (
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*"
)


def convert_email(
    conteudo_email: str,
    anexos: str = 'NÃO'
) -> dict:
    try:
        bytes_eml = conteudo_email.encode('utf-8')
        msg = BytesParser(policy=policy.default).parse(BytesIO(bytes_eml))

        data_formatada = datetime.strptime(
            msg['date'],
            "%a, %d %b %Y %H:%M:%S %z"
        )
        data_formatada = data_formatada.astimezone(
            ZoneInfo("America/Sao_Paulo")
        )
        data_formatada = data_formatada.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        email_de = re.findall(regexp_email, msg.get('from', 'N/D'))[0]
        emails_para = ','.join(re.findall(regexp_email, msg.get('to', '')))
        emails_copia = ','.join(re.findall(regexp_email, msg.get('cc', '')))

        resposta_para_match = re.findall(regexp_email, msg.get('reply-to', ''))
        resposta_para = resposta_para_match[0] if resposta_para_match else ""

        assunto = str(msg['subject']).strip()

        mensagem_id = re.sub(r"\s+", "", str(msg['message-id']).strip())

        resultado = {
            "assunto": assunto,
            "de": email_de,
            "para": emails_para,
            "cc": emails_copia,
            "data": data_formatada,
            "mensagem_id": mensagem_id,
            "resposta_para": resposta_para,
            "conteudo": {
                "text/plain": None,
                "text/html": None
            },
            "anexos": []
        }

        for parte in msg.walk():
            cont_type = parte.get_content_type()
            cont_disp = parte.get("Content-Disposition", "").lower()

            if cont_type == "text/plain" and "attachment" not in cont_disp:
                resultado["conteudo"]["text/plain"] = (
                    limpar_texto_plain(parte.get_content())
                )
            elif cont_type == "text/html" and "attachment" not in cont_disp:
                resultado["conteudo"]["text/html"] = (
                    limpar_texto_html(parte.get_content())
                )
            elif "attachment" in cont_disp and anexos.upper() == 'SIM':
                nome = parte.get_filename()
                dados = parte.get_payload(decode=True)
                base64_conteudo = (
                    base64.b64encode(dados).decode('utf-8') if dados else ''
                )
                resultado["anexos"].append({
                    "nome": nome,
                    "tipo": cont_type,
                    "conteudo_base64": base64_conteudo
                })

        return resultado
    except Exception as erro:
        resultado_erro = {
            "erro": str(erro)
        }
        return resultado_erro
