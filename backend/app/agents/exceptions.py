class LLMAnalysisError(Exception):
    """Qualquer falha ao obter uma análise válida do LLM.

    Cobre JSON/estrutura inválida, campos ausentes, timeout, rate limit e
    indisponibilidade — a service layer trata todos os casos da mesma forma:
    marca o lead como `error` e nunca persiste uma análise parcial.
    """
