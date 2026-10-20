from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class StayType(str, Enum):
    BEACH = "en bord de mer, à la plage"
    COUNTRYSIDE = "à la campagne"
    MOUNTAINS = "à la montagne"
    CITY = "en ville"
    SPORT = "activités sportives"
    RELAX = "détente"
    ACCESS = "accessibilité pour personne handicapée ou à mobilité réduite"

    @classmethod
    def infos(cls) -> str:
        return ", ".join(stay.value for stay in cls)

class CriterionOpinion(BaseModel):
    """Avis exprimé par l'utilisateur ou détecté selon ses préférences de destination et d'activité."""

    criterion: StayType = Field(description="Type de séjour concerné.")
    avis: Optional[bool] = Field(
        default=None,
        description="True si un avis positif est détecté, False s'il est négatif, None si non mentionné."
    )
    justification: Optional[str] = Field(
        default=None,
        description="Justification brève et informelle de ton positionnement"
    )

class CriteriaIdentificationResult(BaseModel):
    """Critères de séjour identifiés dans le message de l'utilisateur."""

    criteria: Optional[list[CriterionOpinion]] = Field(
        default=None,
        description="Un élément pour chaque type de séjour détecté.",
    )

    @property
    def details_identified(self) -> bool:
        if not self.criteria:
            return False
        return any(c.avis is not None for c in self.criteria)

    def as_dict(self) -> dict[StayType, dict]:
        if not self.criteria:
            return {}
        return {c.criterion: {"avis": c.avis, "justification": c.justification} for c in self.criteria}


class State(MessagesState):
    # Contient messages par héritage
    criteria: CriteriaIdentificationResult
    request: str
    answer: str