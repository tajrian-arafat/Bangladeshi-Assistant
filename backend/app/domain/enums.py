"""Domain enumerations used across the BDA backend."""

from enum import StrEnum


class ServiceStatus(StrEnum):
    ACTIVE = "ACTIVE"
    OUTDATED = "OUTDATED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFLICTED = "CONFLICTED"
    DISABLED = "DISABLED"


class ServiceCategory(StrEnum):
    IDENTITY = "IDENTITY"
    TRANSPORT = "TRANSPORT"
    TAX = "TAX"
    CIVIL_REGISTRATION = "CIVIL_REGISTRATION"
    EDUCATION = "EDUCATION"
    GOVERNMENT_DISCOVERY = "GOVERNMENT_DISCOVERY"
    OTHER = "OTHER"


class ReviewState(StrEnum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class ChecklistItemType(StrEnum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    CONDITIONAL = "CONDITIONAL"
    RECOMMENDED = "RECOMMENDED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ProcedureStepStatus(StrEnum):
    ACTIVE = "active"
    INCOMPLETE = "incomplete"
    CONFLICTED = "conflicted"


class SourceTier(StrEnum):
    """Authority tiers. Never auto-changed by LLM."""

    TIER_1 = "1"  # Official authority directly responsible
    TIER_2 = "2"  # Other official Bangladesh government source
    TIER_3 = "3"  # Official institution / public body
    TIER_4 = "4"  # Recognized institutional source
    TIER_5 = "5"  # Reliable media / professional
    TIER_6 = "6"  # Guides / blogs
    TIER_7 = "7"  # Community / social media


class ClaimPipelineStatus(StrEnum):
    """Claim lifecycle. VERIFIED ≠ 'a source was found'."""

    DISCOVERED = "DISCOVERED"
    EXTRACTED = "EXTRACTED"
    NORMALIZED = "NORMALIZED"
    CROSS_CHECKED = "CROSS_CHECKED"
    PENDING_REVIEW = "PENDING_REVIEW"
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    CONFLICTING = "CONFLICTING"
    OUTDATED = "OUTDATED"
    REJECTED = "REJECTED"
    UNVERIFIED = "UNVERIFIED"


class ClaimType(StrEnum):
    ELIGIBILITY = "eligibility"
    DOCUMENT = "document"
    CONDITIONAL_DOCUMENT = "conditional_document"
    FEE = "fee"
    PROCEDURE_STEP = "procedure_step"
    PROCESSING_TIME = "processing_time"
    APPLICATION_URL = "application_url"
    OFFICE = "office"
    PAYMENT_METHOD = "payment_method"
    DEADLINE = "deadline"
    LEGAL_BASIS = "legal_basis"
    AVAILABILITY = "availability"
    RESTRICTION = "restriction"
    PRACTICAL_TIP = "practical_tip"
    OTHER = "other"


class InformationClass(StrEnum):
    OFFICIAL = "OFFICIAL"
    PRACTICAL = "PRACTICAL"
    DISCOVERY = "DISCOVERY"


class EvidenceStrength(StrEnum):
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"


class KnowledgeGapType(StrEnum):
    MISSING_FEE_SCHEDULE = "missing_fee_schedule"
    MISSING_PROCEDURE = "missing_procedure"
    MISSING_APPLICATION_URL = "missing_application_url"
    CONFLICTING_SOURCES = "conflicting_sources"
    MISSING_LOCAL_RULE = "missing_local_government_rule"
    MISSING_PROCESSING_SLA = "missing_processing_sla"
    MISSING_DOCUMENT_MATRIX = "missing_document_matrix"
    MISSING_EVIDENCE = "missing_evidence"
    OTHER = "other"


class KnowledgeGapStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    WONT_FIX = "WONT_FIX"


class KnowledgeGapPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnswerSupportLevel(StrEnum):
    """Controls user-facing answer behavior (not always shown raw)."""

    VERIFIED = "VERIFIED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONFLICTED = "CONFLICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class CatalogueMappingType(StrEnum):
    EXISTING_SEED = "existing_seed"
    NEW_CANONICAL = "new_canonical"
    ALIAS = "alias"
    MERGE = "merge"
    DUPLICATE = "duplicate"
    RETIRED = "retired"


class CatalogueMappingReviewStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCKED = "BLOCKED"


class CatalogueMappingStatus(StrEnum):
    """Outcome of catalogue ↔ runtime synchronization."""

    EXACT_MATCH = "EXACT_MATCH"
    ALIAS_MATCH = "ALIAS_MATCH"
    MERGED_MATCH = "MERGED_MATCH"
    NEW_RUNTIME_SERVICE = "NEW_RUNTIME_SERVICE"
    UNRESOLVED = "UNRESOLVED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class LanguageCode(StrEnum):
    BN = "bn"
    EN = "en"
    BANGLISH = "banglish"
    AUTO = "auto"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class IntentType(StrEnum):
    PROCEDURE_INQUIRY = "procedure_inquiry"
    DOCUMENT_LIST = "document_list"
    FEE_INQUIRY = "fee_inquiry"
    OFFICE_LOCATOR = "office_locator"
    ELIGIBILITY = "eligibility"
    GENERAL_INFO = "general_info"
    UNSUPPORTED = "unsupported"


class FeedbackType(StrEnum):
    INCORRECT_ANSWER = "incorrect_answer"
    MISSING_INFO = "missing_info"
    OUTDATED_INFO = "outdated_info"
    HELPFUL = "helpful"
    OTHER = "other"


class ChangeImpact(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ReviewQueueStatus(StrEnum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class CrawlJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrawlAttemptStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    PUBLISH = "publish"
    APPROVE = "approve"
    REJECT = "reject"
    LOGIN = "login"
    LOGOUT = "logout"


class SeedReplacementStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    APPLIED = "APPLIED"
    ROLLED_BACK = "ROLLED_BACK"
    REJECTED = "REJECTED"


class SeedReplacementKind(StrEnum):
    FEE = "fee"
    CHECKLIST = "checklist"
    PROCEDURE_STEP = "procedure_step"


class GeographyAliasType(StrEnum):
    DISTRICT = "district"
    DIVISION = "division"
    UPAZILA = "upazila"
    AREA = "area"
    CITY = "city"


class ServiceLinkType(StrEnum):
    APPLICATION = "application"
    INFORMATION = "information"
    FORM = "form"
    PAYMENT = "payment"
    OTHER = "other"


class DocumentStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class EvaluationRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
