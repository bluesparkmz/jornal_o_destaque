from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterIn(BaseModel): username:str=Field(min_length=3,max_length=100); email:EmailStr; password:str=Field(min_length=10,max_length=128); display_name:str|None=Field(default=None,max_length=255)
class LoginIn(BaseModel): identity:str=Field(min_length=3,max_length=255); password:str=Field(min_length=1,max_length=128)
class RefreshIn(BaseModel): refresh_token:str
class TokenOut(BaseModel): access_token:str; refresh_token:str; token_type:str="bearer"
class UserOut(BaseModel): id:int; username:str; email:EmailStr|None; display_name:str|None; role:str; is_active:bool; model_config=ConfigDict(from_attributes=True)
class CategoryIn(BaseModel): name:str=Field(min_length=1,max_length=255); slug:str=Field(min_length=1,max_length=255); description:str|None=None; parent_id:int|None=None
class TagIn(BaseModel): name:str=Field(min_length=1,max_length=255); slug:str=Field(min_length=1,max_length=255)
class CategoryOut(CategoryIn): id:int; model_config=ConfigDict(from_attributes=True)
class TagOut(TagIn): id:int; model_config=ConfigDict(from_attributes=True)
class ArticleIn(BaseModel):
    title:str=Field(min_length=1,max_length=500); slug:str=Field(min_length=1,max_length=500); excerpt:str|None=None; content:str=Field(min_length=1); content_format:Literal["markdown","html"]="markdown"; status:str="draft"; category_ids:list[int]=[]; tag_ids:list[int]=[]; featured_image_url:str|None=None; published_at:datetime|None=None
class ArticlePatch(BaseModel):
    title:str|None=Field(default=None,max_length=500); slug:str|None=Field(default=None,max_length=500); excerpt:str|None=None; content:str|None=None; content_format:Literal["markdown","html"]|None=None; status:str|None=None; category_ids:list[int]|None=None; tag_ids:list[int]|None=None; featured_image_url:str|None=None; published_at:datetime|None=None
class AuthorOut(BaseModel): id:int; username:str; display_name:str|None=None; model_config=ConfigDict(from_attributes=True)
class ArticleOut(BaseModel):
    id:int; title:str; slug:str; excerpt:str|None; content:str; content_format:Literal["markdown","html"]; status:str; views_count:int; featured_image_url:str|None; source_url:str|None; published_at:datetime|None; created_at:datetime; updated_at:datetime; author:AuthorOut|None; categories:list[CategoryOut]; tags:list[TagOut]
    model_config=ConfigDict(from_attributes=True)
class ArticlePage(BaseModel): items:list[ArticleOut]; page:int; per_page:int; total:int
class CommentIn(BaseModel): author_name:str|None=Field(default=None,max_length=255); author_email:EmailStr|None=None; body:str=Field(min_length=2,max_length=4000)
class CommentOut(BaseModel):
    id: int
    author_name: str | None
    body: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class SubscriberIn(BaseModel): email:EmailStr; name:str|None=Field(default=None,max_length=255)
class Message(BaseModel): message:str
class MediaOut(BaseModel):
    id: int
    url: str | None
    mime_type: str | None
    original_name: str | None
    alt_text: str | None
    model_config = ConfigDict(from_attributes=True)
class NewspaperIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str | None = None
    issue_number: str | None = Field(default=None, max_length=100)
    cover_url: str | None = Field(default=None, max_length=1000)
    price_cents: int = Field(ge=0)
    currency: str = Field(default="MZN", min_length=3, max_length=3)
    is_published: bool = False
class NewspaperOut(BaseModel):
    id: int; title: str; slug: str; description: str | None; issue_number: str | None
    cover_url: str | None; price_cents: int; currency: str; is_published: bool
    published_at: datetime | None; created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class PurchaseOut(BaseModel):
    id: int; newspaper_id: int; amount_cents: int; currency: str; status: str
    created_at: datetime; paid_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
class PaymentRequestIn(BaseModel):
    msisdn: str = Field(min_length=9, max_length=20, pattern=r"^[0-9+]+$")
