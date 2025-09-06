from pydantic import BaseModel, ConfigDict


class OctaneBase(BaseModel):
    grade: int
    
    model_config = ConfigDict(from_attributes=True, strict=True)


class OctaneCreate(OctaneBase):
    pass


class OctaneUpdate(OctaneBase):
    pass


class Octane(OctaneBase):
    id: int