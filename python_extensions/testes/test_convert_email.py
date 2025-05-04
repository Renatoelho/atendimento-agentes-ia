
from convert_email import convert_email

with open('Path e arquivo de E-mail .eml', 'r', encoding='utf-8') as f:
    conteudo = f.read()

resultado = convert_email(conteudo, anexos='SIM')

email_id = f"{resultado.get('de', None)}-{resultado.get('mensagem_id', None)}"
email_origem = resultado.get("de", None)
email_destino = resultado.get("para", None)
assunto = resultado.get("assunto", None)
email_mensagem = resultado.get("conteudo", {}).get("text/plain", None)
email_mensagem_html = resultado.get("conteudo", {}).get("text/html", None)
email_data = resultado.get("data", None)
quantidade_anexos = len(resultado["anexos"])

print(email_id,"\n", email_origem,"\n", email_destino,"\n", assunto, "\n", email_mensagem,"\n","\n", email_data,"\n", quantidade_anexos)