from pydantic import BaseModel, ConfigDict


class BrandBase(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True, strict=True)


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BrandBase):
    pass


class Brand(BrandBase):
    id: int