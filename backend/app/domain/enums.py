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
    TIER_1 = "1"
    TIER_2 = "2"
    TIER_3 = "3"
    TIER_4 = "4"
    TIER_5 = "5"
    TIER_6 = "6"


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
