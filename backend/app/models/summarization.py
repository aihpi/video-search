from app.models.camel_case import CamelCaseModel


class SummarizationRequest(CamelCaseModel):
    transcript_id: str


class SummarizationResponse(CamelCaseModel):
    summary: str
