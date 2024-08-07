from langchain_core.pydantic_v1 import BaseModel, Field

class GradeID(BaseModel):
    """The product ID is in the user's question."""
    ID: str = Field(description="ID of the product, just give the number")


class GradeReWrite(BaseModel):
    """Viết lại câu hỏi của người dùng dựa trên câu hỏi và lịch sử."""
    rewrite: str = Field(description="Chỉ cần hỏi lại câu hỏi và vui lòng sử dụng tiếng Việt để trả lời.")