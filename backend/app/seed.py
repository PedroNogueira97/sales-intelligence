"""Seed de dados fictícios para demonstração e testes manuais (SPEC.md secao 26).

Uso:
    python -m app.seed
"""

from app.core.db import SessionLocal
from app.repositories import company_repository
from app.schemas.company import CompanyCreate
from app.schemas.lead import LeadCreate
from app.services import company_service, lead_service

COMPANY = CompanyCreate(
    name="Acme Sales",
    description="Empresa de tecnologia comercial B2B",
    product_description="Plataforma de automação comercial",
    ideal_customer_profile="Empresas B2B com 20-500 funcionários",
    average_ticket=10000,
    pain_points=["perda de leads", "follow-up manual", "baixa produtividade comercial"],
    communication_tone="professional",
)

# Cada lead cobre um cenário de SPEC.md secao 26.
LEADS: list[dict] = [
    # 1. claramente qualificado
    {
        "name": "Marina Alves",
        "email": "marina.alves@techcorp.com.br",
        "company_name": "TechCorp Soluções",
        "message": (
            "Olá, somos uma empresa B2B com 120 funcionários e estamos perdendo muitos leads "
            "porque o follow-up é todo manual em planilha. Gostaria de agendar uma demonstração "
            "o quanto antes, temos orçamento aprovado para esse trimestre."
        ),
    },
    # 2. claramente fora do ICP
    {
        "name": "Pedro Lima",
        "email": "pedro@microloja.com",
        "company_name": "Microloja do Pedro",
        "message": "Oi, sou autônomo, vendo produtos artesanais sozinho, vi o anúncio de vocês. Quanto custa?",
    },
    # 3. sem informações suficientes
    {
        "name": "Ana",
        "email": "ana@example.com",
        "company_name": None,
        "message": "Oi, tudo bem? Queria saber mais.",
    },
    # 4. interessado mas sem urgência
    {
        "name": "Carlos Souza",
        "email": "carlos.souza@industriabeta.com.br",
        "company_name": "Indústria Beta",
        "message": (
            "Somos uma empresa de médio porte e estamos avaliando ferramentas de automação "
            "comercial para o próximo ano, ainda sem pressa, só pesquisando opções."
        ),
    },
    # 5. alta urgência
    {
        "name": "Fernanda Costa",
        "email": "fernanda@growthly.com.br",
        "company_name": "Growthly",
        "message": (
            "Precisamos resolver isso essa semana, estamos perdendo leads todos os dias por "
            "falta de organização no funil. Temos 80 funcionários, podem me ligar hoje?"
        ),
    },
    # 6. perguntando preço
    {
        "name": "Rafael Nunes",
        "email": "rafael@vendasmax.com.br",
        "company_name": "VendasMax",
        "message": "Qual o valor da mensalidade de vocês? Quantos usuários entram no plano básico?",
    },
    # 7. pedindo demonstração
    {
        "name": "Juliana Prado",
        "email": "juliana.prado@b2bsolutions.com",
        "company_name": "B2B Solutions",
        "message": "Podemos agendar uma demonstração do produto para a nossa equipe comercial?",
    },
    # 8. sem informar empresa
    {
        "name": "Diego Martins",
        "email": "diego.martins@gmail.com",
        "company_name": None,
        "message": "Vi vocês no LinkedIn, trabalho com vendas e queria entender melhor o produto.",
    },
    # 9. problema incompatível
    {
        "name": "Larissa Melo",
        "email": "larissa@fabricadecalcados.com.br",
        "company_name": "Fábrica de Calçados Melo",
        "message": (
            "Estamos com problema na linha de produção, as máquinas estão quebrando muito. "
            "Vocês resolvem isso?"
        ),
    },
    # 10. ambíguo
    {
        "name": "Bruno Teixeira",
        "email": "bruno.teixeira@empresaxyz.com",
        "company_name": "Empresa XYZ",
        "message": "Interessante o que vocês fazem. Pode ser que a gente precise disso, vamos ver.",
    },
]


def run() -> None:
    db = SessionLocal()
    try:
        existing = company_repository.get_singleton(db)
        if existing is not None:
            print(f"Empresa '{existing.name}' já configurada (id={existing.id}), pulando seed.")
            return

        company = company_service.create(db, COMPANY)
        print(f"Empresa criada: {company.name} (id={company.id})")

        for lead_data in LEADS:
            lead = lead_service.create(db, LeadCreate(**lead_data))
            print(f"Lead criado: {lead.name} (id={lead.id}, status={lead.status.value})")
    finally:
        db.close()


if __name__ == "__main__":
    run()
