"""Prompts enviados ao modelo em cada etapa do loop.

Os guard rails do canary_agent_instructions.md estão embutidos no system
prompt: citar sempre, `not_found` explícito, comparação texto-com-texto,
critérios de `review`, e nenhum aconselhamento jurídico.

A extração é feita em LOTE: um bloco de categorias por chamada, em vez de
uma chamada por categoria. Ver README, seção "Processamento em lote".
"""

SYSTEM_PROMPT = """\
Você é o Agente de Extração do sistema Canary Deal Terms. Você processa
documentos de deals assinados (SPA, IRA, Certificate of Incorporation etc.)
e produz rascunhos de extração de termos para revisão humana.

Regras invioláveis (do documento de instruções da Canary):

1. NUNCA afirme sem citar. Todo valor extraído vem acompanhado da fonte
   exata: documento + seção/página. Sem citação rastreável, não produza a
   afirmação.
2. Ausência é resposta válida. Termo não encontrado = "not_found" explícito,
   nunca campo vazio, nunca preenchido por inferência ou pelo que seria
   "razoável esperar".
3. Compare texto com texto. "Padrão Canary" só existe comparando o trecho do
   documento com o trecho equivalente do material de referência fornecido
   (templates + precedentes), ambos citados. Sem referência interna para
   comparar, não julgue "padrão de mercado" de memória.
4. Sinalize incerteza como "review" (nunca "high_confidence") quando houver:
   linguagem ambígua/não-padrão sem paralelo no material de referência;
   termo referenciado mas não definido no documento; mais de uma
   interpretação plausível; ou indício de que o documento não é a versão
   final assinada. Sempre com uma frase curta explicando o motivo.
5. Você propõe; humano decide. Sua saída é rascunho — nada do que você
   produz é dado oficial.
6. Sem aconselhamento jurídico. Descreva o que o documento diz e como se
   compara às referências internas; não opine se um termo é bom ou ruim.
7. Nunca combine informação de dois documentos num único campo sem citar
   ambos separadamente.

Ao receber várias categorias numa mesma solicitação, trate cada uma com o
mesmo cuidado que daria se fosse a única: localize o trecho, cite a seção
exata e compare com a referência daquela categoria especificamente. Nunca
reaproveite a citação de uma categoria em outra.

Responda sempre no formato JSON solicitado.
"""

CLASSIFY_INSTRUCTIONS = """\
Classifique o documento abaixo.

Tarefas:
1. Identifique o tipo de documento (ex.: SPA, IRA, Certificate of
   Incorporation, Voting Agreement, ROFR, Side Letter). Se não for possível
   identificar com confiança, retorne document_type = "not_classified" e
   confident = false — não chute.
2. Verifique indícios de que NÃO é a versão final assinada: ausência de
   bloco/página de assinaturas, texto marcado como draft/redline, campos em
   branco a preencher. Liste cada indício encontrado (o nome do arquivo já
   foi verificado separadamente pelo código).

ATENÇÃO: para esta etapa você pode receber apenas o INÍCIO e o FIM do
documento, com o miolo omitido e marcado como tal. Isso é intencional e
não é um defeito do documento — NÃO liste o corte como indício de versão
não-final. O início traz o tipo do documento e o fim traz o bloco de
assinaturas, que é o que esta etapa precisa. A extração dos termos usa o
texto completo, em outra chamada.

Nome do arquivo: {file_name}

Texto do documento:
<document>
{document_text}
</document>
"""

EXTRACT_BATCH_INSTRUCTIONS = """\
Extraia os termos das categorias listadas abaixo do documento
"{file_name}" (tipo: {document_type}), já fornecido acima.

Alertas sobre a versão do documento (considere ao atribuir confiança):
{version_flags}

Categorias a extrair nesta solicitação, cada uma com seu material de
referência da Canary (abas `Templates` e `Dicionario_Termos`) e os
precedentes de deals já aprovados (aba `Terms`):

{category_blocks}

Regras da resposta:
- Devolva EXATAMENTE um item por categoria listada acima — nem mais, nem
  menos. O campo `category` de cada item deve repetir literalmente o nome
  da categoria como foi escrito acima.
- Para cada categoria, nesta ordem:
  a. Localize o trecho relevante no documento.
  b. Se o termo NÃO existir no documento, retorne found = false e
     value = "not_found", com source_section descrevendo o escopo
     verificado (ex.: "documento completo — cláusula não localizada").
     Não deixe nada em branco e não invente um valor.
  c. Se existir: extraia o valor, um resumo em linguagem simples (1-2
     frases, sem juridiquês), e a citação exata (seção/cláusula/página).
  d. Compare o trecho extraído com o material de referência daquela
     categoria e escreva uma nota de comparação curta citando os dois
     lados. Se não houver material de referência aplicável, diga isso na
     nota — não julgue de memória.
  e. Atribua confiança: "high_confidence" ou "review" (critérios do system
     prompt). Se "review", explique o motivo em flag_reason.
"""


def format_reference(reference: dict) -> str:
    lines = []
    for row in reference.get("dictionary", []):
        lines.append(f"[Dicionario_Termos] {row}")
    for row in reference.get("templates", []):
        lines.append(f"[Templates] {row}")
    return "\n".join(lines) if lines else "(nenhuma referência encontrada para esta categoria)"


def format_precedents(precedents: list) -> str:
    if not precedents:
        return "(nenhum precedente encontrado para esta categoria)"
    return "\n".join(f"[Terms] {row}" for row in precedents)


def format_category_block(category: str, reference: dict, precedents: list) -> str:
    """Bloco de uma categoria dentro do prompt de extração em lote."""
    return (
        f"### Categoria: {category}\n"
        f"<reference>\n{format_reference(reference)}\n</reference>\n"
        f"<precedents>\n{format_precedents(precedents)}\n</precedents>"
    )


CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "document_type": {
            "type": "string",
            "description": "Tipo do documento, ou 'not_classified' se incerto.",
        },
        "confident": {
            "type": "boolean",
            "description": "true apenas se a classificação for confiável.",
        },
        "final_version_concerns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Indícios de que não é a versão final assinada (vazio se nenhum).",
        },
        "reasoning": {"type": "string"},
    },
    "required": ["document_type", "confident", "final_version_concerns", "reasoning"],
    "additionalProperties": False,
}

_TERM_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "description": "Nome da categoria, repetido literalmente como foi solicitado.",
        },
        "found": {"type": "boolean"},
        "term": {"type": "string", "description": "Nome do termo extraído."},
        "value": {
            "type": "string",
            "description": "Valor extraído, ou 'not_found' quando found = false.",
        },
        "summary": {
            "type": "string",
            "description": "Resumo em linguagem simples (1-2 frases).",
        },
        "source_section": {
            "type": "string",
            "description": (
                "Citação exata: seção/cláusula/página. Para not_found, o escopo "
                "verificado (ex.: 'documento completo — cláusula não localizada')."
            ),
        },
        "confidence": {"type": "string", "enum": ["high_confidence", "review"]},
        "flag_reason": {
            "type": "string",
            "description": "Obrigatório quando confidence = 'review'; senão string vazia.",
        },
        "comparison_note": {
            "type": "string",
            "description": (
                "Comparação texto-com-texto com o material de referência desta "
                "categoria, citando os dois lados."
            ),
        },
        "precedent_used": {"type": "boolean"},
    },
    "required": [
        "category",
        "found",
        "term",
        "value",
        "summary",
        "source_section",
        "confidence",
        "flag_reason",
        "comparison_note",
        "precedent_used",
    ],
    "additionalProperties": False,
}

EXTRACT_BATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "terms": {
            "type": "array",
            "items": _TERM_ITEM_SCHEMA,
            "description": "Um item por categoria solicitada, na mesma ordem.",
        }
    },
    "required": ["terms"],
    "additionalProperties": False,
}
