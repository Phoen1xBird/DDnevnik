from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

EntityId = Annotated[int, Field(strict=True, gt=0)]
Name = Annotated[str, Field(min_length=1)]
ScoreValue = Annotated[int, Field(strict=True, ge=0)]
ScoreMaximum = Annotated[int, Field(strict=True, gt=0)]
Weight = Annotated[float, Field(gt=0, allow_inf_nan=False)]


class InputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Pagination(InputSchema):
    limit: Annotated[int, Field(strict=True, gt=0)] = 100
    offset: Annotated[int, Field(strict=True, ge=0)] = 0
