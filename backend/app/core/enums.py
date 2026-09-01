import enum


class LeadStatus(str, enum.Enum):
    NEW = "new"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    ERROR = "error"


class LeadChannel(str, enum.Enum):
    """Origem simulada do lead (SPEC.md secao 7) — decidida pelo backend, nunca pelo cliente."""

    MANUAL = "manual"
    WHATSAPP = "whatsapp"
    LANDING_PAGE = "landing_page"


class Qualification(str, enum.Enum):
    QUALIFIED = "qualified"
    MAYBE = "maybe"
    UNQUALIFIED = "unqualified"


class Intent(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RecommendedAction(str, enum.Enum):
    SCHEDULE_DEMO = "schedule_demo"
    CONTACT_SALESPERSON = "contact_salesperson"
    ASK_MORE_INFORMATION = "ask_more_information"
    NURTURING = "nurturing"
    DISCARD = "discard"


class InteractionType(str, enum.Enum):
    LEAD_CREATED = "lead_created"
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_FAILED = "analysis_failed"
    RESPONSE_GENERATED = "response_generated"
