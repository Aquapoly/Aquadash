# TODO: séparer et déplacer les schemas dans un dossier schema (renommer le dossier "classes")

from pydantic import BaseModel


class Prototype(BaseModel):
    prototype_id: int
    prototype_name: str

    class Config:
        from_attributes = True