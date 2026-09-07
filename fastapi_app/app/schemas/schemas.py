import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.utils.validators import is_safe_avatar_url


class LanguageEnum(str, Enum):
    TJ = "tj"
    RU = "ru"
    EN = "en"


class VerdictEnum(str, Enum):
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"
    PENDING = "pending"
    JUDGING = "judging"


class ProgrammingLanguageEnum(str, Enum):
    PYTHON3 = "python3"
    CPP17 = "cpp17"
    JAVA11 = "java11"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("username may only contain letters, digits, underscores and hyphens")
        if not (3 <= len(v) <= 50):
            raise ValueError("username length must be between 3 and 50")
        return v


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    login: str
    password: str


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_verified: bool
    is_active: bool
    rating: int
    solved_count: int
    attempt_count: int
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        if v and not is_safe_avatar_url(v):
            return "default.svg"
        return v


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    receiver_id: Optional[int] = None
    chat_id: Optional[int] = None


class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: Optional[int]
    chat_id: Optional[int]
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatBase(BaseModel):
    name: Optional[str] = None
    is_group: bool = False


class ChatCreate(ChatBase):
    member_ids: Optional[List[int]] = None


class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    updated_at: datetime
    members: List[UserResponse] = []
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0

    model_config = {"from_attributes": True}


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProblemTranslationBase(BaseModel):
    language: LanguageEnum
    title: str
    statement: str
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    notes: Optional[str] = None


class ProblemTranslationCreate(ProblemTranslationBase):
    problem_id: int


class ProblemTranslationResponse(ProblemTranslationBase):
    id: int
    problem_id: int

    model_config = {"from_attributes": True}


class TestCaseBase(BaseModel):
    test_order: int
    input_data: str
    expected_output: str
    is_sample: bool = False


class TestCaseCreate(TestCaseBase):
    problem_id: int


class TestCaseResponse(TestCaseBase):
    id: int
    problem_id: int

    model_config = {"from_attributes": True}


class ProblemBase(BaseModel):
    title: str
    difficulty: str = "easy"
    time_limit: float = 1.0
    memory_limit: int = 256
    category: Optional[str] = None


class ProblemCreate(ProblemBase):
    translations: List[ProblemTranslationBase] = []
    test_cases: List[TestCaseBase] = []


class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit: Optional[float] = None
    memory_limit: Optional[int] = None
    category: Optional[str] = None
    is_published: Optional[bool] = None


class ProblemResponse(ProblemBase):
    id: int
    is_published: bool
    author_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    solved_count: int = 0
    translations: List[ProblemTranslationResponse] = []
    test_cases: List[TestCaseResponse] = []

    model_config = {"from_attributes": True}


class ProblemDetailResponse(ProblemResponse):
    statement: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    notes: Optional[str] = None
    language: Optional[str] = None


class SubmissionBase(BaseModel):
    code: str
    language: ProgrammingLanguageEnum


class SubmissionCreate(SubmissionBase):
    problem_id: int


class SubmissionResponse(SubmissionBase):
    id: int
    user_id: int
    problem_id: int
    verdict: VerdictEnum
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    test_passed: int = 0
    test_total: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    judged_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SubmissionFeedEntry(BaseModel):
    id: int
    submission_id: int
    user_id: int
    username: str
    problem_id: int
    problem_title: str
    verdict: VerdictEnum
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    language: ProgrammingLanguageEnum
    created_at: datetime

    model_config = {"from_attributes": True}


class ContestProblemBase(BaseModel):
    problem_id: int
    position: Optional[int] = None
    points: Optional[int] = 1


class ContestBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    contest_type: str = "standard"


class ContestCreate(ContestBase):
    problem_ids: List[int] = []
    is_published: bool = False


class ContestResponse(ContestBase):
    id: int
    is_published: bool
    owner_id: Optional[int] = None
    created_at: datetime
    problems: List[ContestProblemBase] = []

    model_config = {"from_attributes": True}


class FriendshipResponse(BaseModel):
    id: int
    user_id: int
    friend_id: int
    friend_username: str
    friend_avatar: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NewsBase(BaseModel):
    title: str
    content: str


class NewsCreate(NewsBase):
    pass


class NewsResponse(NewsBase):
    id: int
    author_id: Optional[int] = None
    author_username: Optional[str] = None
    is_published: bool
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    code: Optional[str] = None


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    rating: int
    solved_count: int
    attempt_count: int


class DashboardStats(BaseModel):
    total_users: int
    total_problems: int
    total_submissions: int
    total_solved: int
    accepted_rate: float
    recent_feed: List[SubmissionFeedEntry] = []
    top_users: List[LeaderboardEntry] = []
