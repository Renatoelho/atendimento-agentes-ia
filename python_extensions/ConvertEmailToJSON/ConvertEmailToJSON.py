
from nifiapi.properties import PropertyDescriptor
from nifiapi.properties import StandardValidators
from nifiapi.flowfiletransform import FlowFileTransform
from nifiapi.flowfiletransform import FlowFileTransformResult


class ConvertEmailToJSON(FlowFileTransform):
    class Java:
        implements = ["org.apache.nifi.python.processor.FlowFileTransform"]

    class ProcessorDetails:
        version = "0.0.1-Python"
        description = """
        Este processador converte e-mails capturados via IMAP em seu formato
        bruto para arquivos JSON contendo os principais atributos da mensagem.
        Os anexos podem ser incluídos no JSON, sendo armazenados em um array
        com todos os seus metadados e codificados em base64 para conversões
        futuras.
        """
        tags = ["Email", "JSON", "IMAP", "Arquivo .EML"]

    ANEXOS = PropertyDescriptor(
        name="Adiciona anexo(s) ao Json",
        description=(
            "Escolha se o e-mail convertido em "
            "JSON incluirá os anexos capturados."
        ),
        allowable_values=["NÃO", "SIM"],
        default_value="NÃO",
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        required=True
    )

    property_descriptors = [
        ANEXOS,
    ]

    def __init__(self, **kwargs):
        pass

    def getPropertyDescriptors(self):
        return self.property_descriptors

    def getDynamicPropertyDescriptor(self, propertyname):
        return PropertyDescriptor(
            name=propertyname,
            description="Uma propriedade definida pelo usuário",
            validators=[StandardValidators.NON_EMPTY_VALIDATOR],
            dynamic=True
        )

    def transform(self, context, flowfile):
        import json
        import traceback

        from convert_email import convert_email
        from hash_processamento import hash_processamento

        try:
            mime_type_para_erro = (
                flowfile
                .getAttribute("mime.type")
            )
            opcao_anexos = (
                context
                .getProperty(self.ANEXOS)
                .evaluateAttributeExpressions(flowfile)
                .getValue()
            )
            conteudo_flowfile = (
                flowfile
                .getContentsAsBytes()
                .decode()
            )

            estrutura_email = convert_email(
                conteudo_flowfile,
                anexos=opcao_anexos
            )
            email_id = (
                f"{estrutura_email.get('de', None)}-"
                f"{estrutura_email.get('mensagem_id', None)}-"
                f"{hash_processamento()}"
            )
            email_origem = str(estrutura_email.get("de", None))
            email_destino = str(estrutura_email.get("para", None))
            email_assunto = str(estrutura_email.get("assunto", None))
            email_mensagem = (
                str(
                    estrutura_email
                    .get("conteudo", {})
                    .get("text/plain", None)
                )
            )
            email_mensagem_html = (
                str(
                    estrutura_email
                    .get("conteudo", {})
                    .get("text/html", None)
                )
            )
            email_data = str(estrutura_email.get("data", None))
            quantidade_anexos = str(len(estrutura_email["anexos"]))
            conteudo_json = (
                json.dumps(estrutura_email, indent=2, ensure_ascii=False)
            )
            atributos = (
                {
                    "mime.type": "application/json",
                    "filename": f"{email_origem}.json",
                    "email_id": email_id,
                    "email_data": email_data,
                    "email_origem": email_origem,
                    "email_destino": email_destino,
                    "email_assunto": email_assunto,
                    "email_mensagem": email_mensagem,
                    "email_mensagem_html": email_mensagem_html,
                    "quantidade_anexos": quantidade_anexos
                }
            )

            return FlowFileTransformResult(
                relationship="success",
                contents=conteudo_json,
                attributes=atributos
            )

        except Exception as erro:
            atributos = (
                {
                    "mime.type": mime_type_para_erro,
                    "erro": str(erro),
                    "traceback": traceback.format_exc()
                }
            )
            return FlowFileTransformResult(
                relationship="failure",
                contents=conteudo_flowfile,
                attributes=atributos
            )
