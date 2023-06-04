from schemas.common import BaseOrjsonModel


class ActualStakeDTO(BaseOrjsonModel):
    id: int
    cpm: int


class ActualStakesDTO(BaseOrjsonModel):
    stakes: list[ActualStakeDTO] | None
