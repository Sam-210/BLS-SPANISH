from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class SystemStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class LogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class AppointmentStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    FAILED = "failed"
    PENDING = "pending"

class VisaType(str, Enum):
    TOURIST = "Tourist Visa"
    BUSINESS = "Business Visa"
    STUDENT = "Student Visa"
    WORK = "Work Visa"
    FAMILY_REUNION = "Family Reunion Visa"

class VisaSubType(str, Enum):
    # Tourist/Business/Student subtypes
    SHORT_STAY = "Short Stay"
    LONG_STAY = "Long Stay"
    # Work subtypes  
    TEMPORARY_WORK = "Temporary Work"
    PERMANENT_WORK = "Permanent Work"
    # Family subtypes
    SPOUSE_VISA = "Spouse Visa"
    CHILD_VISA = "Child Visa"

class AppointmentType(str, Enum):
    INDIVIDUAL = "Individual"
    FAMILY = "Family"

# Database Models
class SystemLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: LogLevel
    message: str
    details: Optional[Dict[str, Any]] = None
    step: Optional[str] = None

class AppointmentSlot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    found_at: datetime = Field(default_factory=datetime.utcnow)
    appointment_date: str
    appointment_time: str
    visa_type: str
    visa_category: str
    location: str
    available_slots: int
    status: AppointmentStatus = AppointmentStatus.AVAILABLE
    booking_details: Optional[Dict[str, Any]] = None

class SystemConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: SystemStatus = SystemStatus.STOPPED
    check_interval_minutes: int = 2
    visa_type: VisaType = VisaType.TOURIST
    visa_subtype: VisaSubType = VisaSubType.SHORT_STAY
    appointment_type: AppointmentType = AppointmentType.INDIVIDUAL
    number_of_members: int = 1
    last_check: Optional[datetime] = None
    total_checks: int = 0
    slots_found: int = 0
    successful_bookings: int = 0
    error_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email_notifications: bool = True
    notification_email: str = "nomadsam6@gmail.com"
    notify_on_slots_found: bool = True
    notify_on_booking_success: bool = True
    notify_on_errors: bool = True

# API Request/Response Models
class StartSystemRequest(BaseModel):
    check_interval_minutes: Optional[int] = 2
    visa_type: Optional[VisaType] = VisaType.TOURIST
    visa_subtype: Optional[VisaSubType] = VisaSubType.SHORT_STAY
    appointment_type: Optional[AppointmentType] = AppointmentType.INDIVIDUAL
    number_of_members: Optional[int] = 1

class SystemStatusResponse(BaseModel):
    status: SystemStatus
    last_check: Optional[datetime]
    total_checks: int
    slots_found: int
    successful_bookings: int
    error_count: int
    uptime_minutes: Optional[int] = None

class AppointmentChoice(BaseModel):
    slot_id: str
    confirm_booking: bool = False

class LogsResponse(BaseModel):
    logs: List[SystemLog]
    total_count: int

class AvailableSlotsResponse(BaseModel):
    slots: List[AppointmentSlot]
    total_count: int

# New Models for User Features

class ApplicantInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    passport_number: str
    nationality: str
    phone_number: str
    email: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    visa_type_preference: Optional[VisaType] = None
    notes: Optional[str] = None
    is_primary: bool = False  # For family applications
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LoginCredentials(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    credential_name: str  # Friendly name for the credential set
    email: str
    password: str  # In production, this should be encrypted
    is_active: bool = True
    is_primary: bool = False  # Primary credential to use by default
    last_used: Optional[datetime] = None
    success_rate: Optional[float] = 0.0  # Track success rate for this credential
    total_attempts: int = 0
    successful_attempts: int = 0
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# API Request/Response Models for new features

class CreateApplicantRequest(BaseModel):
    first_name: str
    last_name: str
    passport_number: str
    nationality: str
    phone_number: str
    email: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    visa_type_preference: Optional[VisaType] = None
    notes: Optional[str] = None
    is_primary: bool = False

class UpdateApplicantRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    passport_number: Optional[str] = None
    nationality: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    visa_type_preference: Optional[VisaType] = None
    notes: Optional[str] = None
    is_primary: Optional[bool] = None

class ApplicantsResponse(BaseModel):
    applicants: List[ApplicantInfo]
    total_count: int

class CreateCredentialRequest(BaseModel):
    credential_name: str
    email: str
    password: str
    is_primary: bool = False
    notes: Optional[str] = None

class UpdateCredentialRequest(BaseModel):
    credential_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None
    notes: Optional[str] = None

class CredentialsResponse(BaseModel):
    credentials: List[LoginCredentials]
    total_count: int

class TestCredentialRequest(BaseModel):
    credential_id: str

class TestCredentialResponse(BaseModel):
    success: bool
    message: str
    response_time_ms: Optional[int] = None