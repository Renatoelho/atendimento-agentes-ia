import json
import base64
import traceback

from nifiapi.properties import PropertyDescriptor
from nifiapi.properties import StandardValidators
from nifiapi.flowfiletransform import FlowFileTransform
from nifiapi.flowfiletransform import FlowFileTransformResult


class EmailJSONToAttachment(FlowFileTransform):
    class Java:
        implements = ["org.apache.nifi.python.processor.FlowFileTransform"]

    class ProcessorDetails:
        version = "0.0.1-Python"
        description = """
        Este processador converte os anexos de um e-mail extraído pelo
        ConvertEmailToJSON de forma unitária. Para que isso funcione
        corretamente, é necessário aplicar previamente um SplitJson na
        propriedade 'anexos', de modo que cada flowfile contenha apenas
        um anexo individual.

        Atenção: a propriedade 'Max String Length' do SplitJson deve ser
        configurada para 1024 MB ou superior. Isso garante que o conteúdo
        completo do anexo em base64 seja incluído no flowfile resultante
        sem truncamentos, permitindo a conversão correta.

        Cada anexo será transformado em um flowfile com o conteúdo
        decodificado de base64 para binário. O nome do anexo convertido
        incluirá o ID do e-mail original e a posição do anexo, se
        necessário, o que permite sua identificação posterior, especialmente
        quando combinado com os atributos 'email_id', 'posicao_anexo' e
        'quantidade_anexos', herdados do flowfile original.
        """
        tags = ["Email", "Json", "Anexo", "Base64", "IMAP"]

    ADD_PREFIXO = PropertyDescriptor(
        name="Adicionar Prefixo de origem ao nome do anexo?",
        description=(
            "Adicionar email_id como prefixo no nome do anexo."
        ),
        allowable_values=["SIM", "NÃO"],
        default_value="SIM",
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        required=False
    )

    property_descriptors = [
        ADD_PREFIXO,
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
        try:
            conteudo_flowfile = flowfile.getContentsAsBytes().decode()
            anexo = json.loads(conteudo_flowfile)

            email_id = (
                flowfile
                .getAttribute("email_id")
            ) or "email_id_nao_localizado"

            index_anexo = (
                flowfile
                .getAttribute("fragment.index")
            ) or "0"

            adicionar_prefixo = (
                context
                .getProperty(self.ADD_PREFIXO)
                .evaluateAttributeExpressions(flowfile)
                .getValue()
                .strip()
            )

            nome_arquivo = anexo.get("nome", "arquivo_sem_nome_definido")
            posicao_anexo = str(int(index_anexo) + 1)

            if adicionar_prefixo == "SIM":
                nome_arquivo = (
                    f"{email_id}-anexo-{posicao_anexo}-{nome_arquivo}"
                )

            tipo_arquivo = anexo.get("tipo", "application/octet-stream")
            conteudo_base64 = anexo.get(
                "conteudo_base64",
                "QXJxdWl2byBzZW0gY29udGV1ZG8u"
            )

            content_binario = base64.b64decode(conteudo_base64)

            atributos = {
                "filename": nome_arquivo,
                "mime.type": tipo_arquivo,
                "email_id": email_id,
                "posicao_anexo": posicao_anexo
            }

            return FlowFileTransformResult(
                relationship="success",
                contents=content_binario,
                attributes=atributos
            )

        except Exception as erro:
            atributos = {
                "filename": "anexo_nao_convertido.json",
                "erro": str(erro),
                "traceback": traceback.format_exc()
            }
            return FlowFileTransformResult(
                relationship="failure",
                contents=conteudo_flowfile,
                attributes=atributos
            )
