"""Seed de dados fictícios para demonstração e testes manuais (SPEC.md secao 29).

Uso:
    python -m app.seed
"""

from app.core.db import SessionLocal
from app.core.enums import LeadChannel
from app.repositories import company_repository
from app.schemas.company import CompanyCreate
from app.schemas.lead import LandingPageLeadCreate, LeadCreate
from app.services import company_service, lead_service

COMPANY = CompanyCreate(
    name="Acme Sales",
    description="Empresa de tecnologia comercial B2B",
    product_description="Plataforma de automação comercial",
    products=[
        {"name": "Acme CRM", "description": "Gestão de funil comercial e follow-up"},
        {"name": "Acme Onboarding", "description": "Consultoria de implantação e treinamento"},
    ],
    ideal_customer_profile="Empresas B2B com 20-500 funcionários",
    average_ticket=10000,
    pain_points=["perda de leads", "follow-up manual", "baixa produtividade comercial"],
    communication_tone="professional",
)

_SCHEMA_BY_CHANNEL = {
    LeadChannel.MANUAL: LeadCreate,
    LeadChannel.LANDING_PAGE: LandingPageLeadCreate,
}

# Cada lead cobre um cenário de SPEC.md secao 29, com canal variado (manual/landing_page — o
# canal telegram não é simulado no seed, depende de mensagens reais chegando pelo bot).
LEADS: list[dict] = [
    # 1. claramente qualificado — manual
    {
        "channel": LeadChannel.MANUAL,
        "name": "Marina Alves",
        "email": "marina.alves@techcorp.com.br",
        "company_name": "TechCorp Soluções",
        "message": (
            "Olá, somos uma empresa B2B com 120 funcionários e estamos perdendo muitos leads "
            "porque o follow-up é todo manual em planilha. Gostaria de agendar uma demonstração "
            "o quanto antes, temos orçamento aprovado para esse trimestre."
        ),
    },
    # 2. claramente fora do ICP — landing page
    {
        "channel": LeadChannel.LANDING_PAGE,
        "name": "Pedro Lima",
        "email": "pedro@microloja.com",
        "message": "Oi, sou autônomo, vendo produtos artesanais sozinho, vi o anúncio de vocês. Quanto custa?",
    },
    # 3. sem informações suficientes — landing page
    {
        "channel": LeadChannel.LANDING_PAGE,
        "name": "Ana",
        "email": "ana@example.com",
        "message": "Oi, tudo bem? Queria saber mais.",
    },
    # 4. interessado mas sem urgência — manual
    {
        "channel": LeadChannel.MANUAL,
        "name": "Carlos Souza",
        "email": "carlos.souza@industriabeta.com.br",
        "company_name": "Indústria Beta",
        "message": (
            "Somos uma empresa de médio porte e estamos avaliando ferramentas de automação "
            "comercial para o próximo ano, ainda sem pressa, só pesquisando opções."
        ),
    },
    # 5. alta urgência — manual
    {
        "channel": LeadChannel.MANUAL,
        "name": "Fernanda Costa",
        "email": "fernanda@growthly.com.br",
        "company_name": "Growthly",
        "message": (
            "Precisamos resolver isso essa semana, estamos perdendo leads todos os dias por "
            "falta de organização no funil. Temos 80 funcionários, podem me ligar hoje?"
        ),
    },
    # 6. perguntando preço — landing page
    {
        "channel": LeadChannel.LANDING_PAGE,
        "name": "Rafael Nunes",
        "email": "rafael@vendasmax.com.br",
        "message": "Qual o valor da mensalidade de vocês? Quantos usuários entram no plano básico?",
    },
    # 7. pedindo demonstração — manual
    {
        "channel": LeadChannel.MANUAL,
        "name": "Juliana Prado",
        "email": "juliana.prado@b2bsolutions.com",
        "company_name": "B2B Solutions",
        "message": "Podemos agendar uma demonstração do produto para a nossa equipe comercial?",
    },
    # 8. sem informar empresa — landing page (schema não tem campo de empresa)
    {
        "channel": LeadChannel.LANDING_PAGE,
        "name": "Diego Martins",
        "email": "diego.martins@gmail.com",
        "message": "Vi vocês no LinkedIn, trabalho com vendas e queria entender melhor o produto.",
    },
    # 9. problema incompatível — landing page
    {
        "channel": LeadChannel.LANDING_PAGE,
        "name": "Larissa Melo",
        "email": "larissa@fabricadecalcados.com.br",
        "message": (
            "Estamos com problema na linha de produção, as máquinas estão quebrando muito. "
            "Vocês resolvem isso?"
        ),
    },
    # 10. ambíguo — manual
    {
        "channel": LeadChannel.MANUAL,
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
        print(f"Empresa criada: {company.name} (id={company.id}), {len(company.products)} produtos")

        for lead_data in LEADS:
            channel = lead_data["channel"]
            fields = {k: v for k, v in lead_data.items() if k != "channel"}
            schema_cls = _SCHEMA_BY_CHANNEL[channel]
            lead = lead_service.create(db, schema_cls(**fields), channel=channel)
            print(f"Lead criado: {lead.name} (canal={channel.value}, id={lead.id})")
    finally:
        db.close()


if __name__ == "__main__":
    run()
