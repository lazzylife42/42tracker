from pydantic import BaseModel
from datetime import datetime
from models import (
	BlocEnum,
	ProjectStatusEnum
	# ...
)

# PROJECT 42
class ProjectBase(BaseModel):
	name: str
	slug: str | None = None
	xp: int
	bloc: BlocEnum
	status: ProjectStatusEnum
	mark: int | None = None
	validated: bool | None = None
	validated_at: datetime | None = None
	retriable_at: datetime | None = None
	estimated_weeks: int
	order_priority: int

	model_config = {
		"from_attributes": True,
		"json_schema_extra": {
			"examples": [
				{
					"id": 0,
					"name": "get_next_line",
					"slug":"Unix logic",
					"xp": 150,
					"bloc": "Unix logic",
					"status":"done",
					"mark": 103,
					"validated_at": "2026-06-08T15:18:00+02:00",
					"estimated_weeks": 1,
					"order_priority": 999
				}
			]
		}
	}


class ProjectResponse(ProjectBase):
	id: int
	model_config = {"from_attributes": True}
