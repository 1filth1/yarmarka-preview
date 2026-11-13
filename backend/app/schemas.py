from pydantic import BaseModel, ConfigDict, Field

class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=2, max_length=160)

class LoginIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    department: str | None
    status: str
    model_config = ConfigDict(from_attributes=True)

class TicketIn(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=10000)
    client_name: str = Field(default="", max_length=160)

class TicketAssignIn(BaseModel):
    assigned_to: int

class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    client_name: str
    status: str
    assigned_to: int | None
    created_by: int
    model_config = ConfigDict(from_attributes=True)
