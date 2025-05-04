# Potencialize seu atendimento com agentes de IA personalizados

<p align="center">
  <img src="https://raw.githubusercontent.com/Renatoelho/nifi-python-email-processadores/main/imagens/visao-geral.png" alt="Visão Geral do Projeto">
</p>

Este projeto foi desenvolvido com o objetivo de oferecer um atendimento **inteligente**, **automatizado** e **escalável**, capaz de reconhecer e tratar diferentes níveis de complexidade em solicitações recebidas por canais digitais. O processo se inicia com a identificação do perfil do solicitante, direcionando automaticamente clientes para uma triagem que classifica o atendimento como **nível básico (N1)** **intermediário (N2)** ou **avançado (3)**. Com base no histórico e no contexto da solicitação, o sistema decide se o caso pode ser tratado de forma automatizada ou se requer intervenção humana. Situações críticas ou que exigem maior atenção passam por uma camada de avaliação adicional, garantindo **precisão** e **segurança** na tomada de decisão. Caso uma classificação inicial não esteja adequada, o processo prevê **reclassificação automática** com base em nova análise. Todo o fluxo é projetado para oferecer respostas **rápidas**, **precisas** e **alinhadas** com a experiência anterior do usuário, garantindo agilidade, personalização e efetividade na resolução das demandas.


>> **OBS.**: Até o momento, o projeto está operando com interações provenientes de contatos por e-mail, mas em futuras atualizações serão adicionados outros canais, como WhatsApp e outras redes.


## Apresentação em Vídeo

[... Em desenvolvimento (Aproveite e acesse meu canal no YouTube, lá tem muito conteúdo interessante.) ...](https://youtube.com/@renato-coelho)

<!-- 
<p align="center">
  <a href="https://youtu.be/xxxxxxxxx" target="_blank"><img src="imagens/thumbnail/thumbnail-emails-nifi-python.png" alt="Vídeo de apresentação"></a>
</p>

![YouTube Video Views](https://img.shields.io/youtube/views/xxxxxxxxx)
![YouTube Video Likes](https://img.shields.io/youtube/likes/xxxxxxxxx)
-->

## Requisitos

+ ![Docker](https://img.shields.io/badge/Docker-27.4.1-E3E3E3)
+ ![Docker-compose](https://img.shields.io/badge/Docker--compose-1.25.0-E3E3E3)
+ ![Git](https://img.shields.io/badge/Git-2.25.1%2B-E3E3E3)
+ ![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%2B-E3E3E3)


# Visão Técnica do Projeto

<p align="center">
  <img src="https://raw.githubusercontent.com/Renatoelho/nifi-python-email-processadores/main/imagens/visao-tecnica.png" alt="Visão Técnica do Projeto">
</p>

A arquitetura técnica do projeto é baseada na orquestração de eventos por meio do **Apache NiFi**, responsável por receber e normalizar os contatos provenientes de múltiplos canais, como **e-mail** e **WhatsApp**. A primeira etapa envolve a identificação do cliente, com validação em um banco de dados **MySQL**. Após essa verificação, os dados estruturados seguem para o **Agente de Classificação**, que utiliza um modelo **LLM** (Large Language Model) aliado a uma consulta de contexto e histórico armazenado no **Elasticsearch** para definir o nível do atendimento (**N1**, **N2** ou **N3**). Esse módulo de classificação é desacoplado e utiliza processamento assíncrono para permitir escalabilidade horizontal. Para casos classificados como críticos (N1 ou N2), há uma etapa adicional de validação com um **Agente Crítico**, que também opera com um modelo LLM para decisões mais refinadas. Se a classificação for **N3**, o fluxo é encaminhado diretamente para uma célula de atendimento **humano**.

A classificação passa por uma validação lógica que, se aprovada, dispara a execução da tratativa por agentes especializados (**Agentes Executores**), que seguem instruções orientadas por IA e novamente se beneficiam da consulta ao Elasticsearch para tomada de decisão. Se a classificação inicial não for válida, entra em ação o **Agente de Reclassificação**, que reavalia o caso com base em novas inferências do modelo LLM, podendo reclassificar o atendimento. O sistema prevê mecanismos de upgrade automático para atendimento humano (N3) caso o novo contexto justifique. Todas as interações, decisões e reclassificações são monitoradas via **dashboards** no Kibana, garantindo visibilidade em tempo real, rastreabilidade e base para auditoria. O uso de containers permite independência entre módulos, com foco em resiliência, escalabilidade e facilidade de manutenção.


## 📨 ConvertEmailToJSON

Este processador foi criado para ser utilizado dentro do Apache NiFi 2.0 e tem como função converter e-mails capturados em seu formato bruto (.eml) em arquivos JSON estruturados. Ele extrai os seguintes dados principais:

+ Remetente (From)
+ Destinatários (To, Cc, Bcc)
+ Assunto
+ Data da mensagem
+ Corpo do e-mail (texto simples ou HTML)
+ Anexos (opcional)

### Destaques:

+ Os anexos são incluídos no JSON como objetos contendo metadados (nome e tipo) e o conteúdo em base64, facilitando o transporte e análise posterior.

+ Ideal para cenários onde é necessário processar os anexos posteriormente, como envio para LLMs ou arquivamento inteligente.

+ Possui uma propriedade configurável para incluir ou não os anexos no JSON ```Adiciona anexo(s) ao Json```.

Exemplo de Json Estruturado a partir de uma e-mail

```json
{
  "assunto": "Teste conversão de Anexos",
  "de": "*********@origem.com",
  "para": "*********@destino.com.br",
  "cc": "",
  "data": "2025-04-24 23:53:03",
  "mensagem_id": "<**********@mail.com>",
  "resposta_para": "",
  "conteudo": {
    "text/plain": "Segue em anexo.",
    "text/html": "<div>Segue em anexo.</div>"
  },
  "anexos": [
    {
      "nome": "teste.txt",
      "tipo": "text/plain",
      "conteudo_base64": "********"
    }
  ]
}
```

## 📎 EmailJSONToAttachment

Este processador faz o caminho inverso: ele recebe os arquivos JSON gerados pelo ConvertEmailToJSON.py (após passar por um SplitJson no array de anexos), e converte novamente os anexos que estão codificados em base64 de volta para seus arquivos originais.

### Funcionalidade:

+ Recria um flowfile para cada anexo.

+ O conteúdo é decodificado do **base64** e o arquivo original é restaurado com os metadados preservados.

+ Permite o reaproveitamento do conteúdo extraído do e-mail, seja para armazenamento, análise ou envio para outros sistemas.

### Observações importantes:

+ Exige que um SplitJson seja aplicado antes, para que cada flowfile contenha apenas um anexo por vez.

+ A propriedade ```Max String Length``` do **SplitJson** deve ser configurada para pelo menos **1024 MB**, garantindo que o conteúdo base64 completo do anexo não seja truncado.

## Deploy 

### Clonando e Acessando o Repositório do Projeto

```bash
git clone https://github.com/Renatoelho/nifi-python-email-processadores.git nifi-python-email-processadores
```

```bash
cd nifi-python-email-processadores
```

### Ativando a Infra no Docker via Docker Compose

```bash
docker compose -p nifi-python-email -f docker-compose.yaml up -d
```

### Implementação dos processadores

```bash
docker cp ConvertEmailToJSON/ apache-nifi:/opt/nifi/nifi-current/python_extensions
```

```bash
docker logs -f apache-nifi | grep -Ei ConvertEmailToJSON
```

```bash
docker cp EmailJSONToAttachment.py apache-nifi:/opt/nifi/nifi-current/python_extensions
```

```bash
docker logs -f apache-nifi | grep -Ei EmailJSONToAttachment
```

## Credenciais de Acessos

### Apache Nifi

- **Url**: https://localhost:8443/nifi/
- **Usuário**: nifi
- **Senha**: HGd15bvfv8744ghbdhgdv7895agqERAo

### MySQL

- **Host Externo**: localhost
- **Host Interno**: mysql
- **Usuário**: root
- **Senha**: W45uE75hQ15Oa
- **Porta**: 3306

### Elasticsearch

- **Ulr Externa**: http://localhost:9200
- **Url Interna**: http://elasticsearch:9200
- **Usuário**: elastic
- **Senha**: nY5AQz37ZZIfMev9nY5AQz37ZZIfMev9

### MinIO/S3

- **Url**: http://localhost:9001/login
- **Usuário**: admin
- **Senha**: eO3RNPcKgWInlzPJuI08

- **Url API Interna**: http://minio-s3:9000
- **Porta API Interna**: 9000

### Kibana

- **Url**: http://localhost:5601/login
- **Usuário**: elastic
- **Senha**: nY5AQz37ZZIfMev9nY5AQz37ZZIfMev9

## Referências

Multiple flowfiles as output for Python Processors, **issues.apache.org** Disponível em: <https://issues.apache.org/jira/browse/NIFI-13402>. Acesso em: 17 Abr. 2025.

NiFi Python Developer’s Guide, **nifi.apache.org** Disponível em: <https://nifi.apache.org/nifi-docs/python-developer-guide.html>. Acesso em: 17 Abr. 2025.

python extension generate multiple flowfiles from bytes input, **Cloudera Community** Disponível em: <https://community.cloudera.com/t5/Support-Questions/python-extension-generate-multiple-flowfiles-from-bytes/m-p/383095>. Acesso em: 17 Abr. 2025.

nifi-python-extensions, **Apache NiFi Python Extensions** Disponível em: <https://github.com/apache/nifi-python-extensions>. Acesso em: 17 Abr. 2025.

O que são modelos de base?, **AWS**. Disponível em: <https://aws.amazon.com/what-is/foundation-models/>. Acesso em: 30  Abr. 2025.

O Que São Large Language Models (LLMs)? **Data Science Academy**. Disponível em: <https://blog.dsacademy.com.br/o-que-sao-large-language-models-llms/>. Acesso em: 29 Abr. 2025.

Suporte N1 x N2 x N3: o que é e conheça as diferenças, **Desk Manager**. Disponível em: <https://deskmanager.com.br/blog/suporte-n1/>. Acesso em: 25 Abr. 2025.

Introducing the Model Context Protocol. **Anthropic**. Disponível em: <https://www.anthropic.com/news/model-context-protocol>. Acesso em:  29 Abr. 2025.

O que são agentes de IA? **IBM**. Disponível em: <https://www.ibm.com/br-pt/think/topics/ai-agents>. Acesso em: 28 Abr. 2025.

A2A Protocol, **Google**. Disponível em: <https://google.github.io/A2A/>. Acesso em: 01 Mai. 2025.
