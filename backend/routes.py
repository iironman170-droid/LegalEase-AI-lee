from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator,
)


router = APIRouter()


# =========================================================
# Request model
# =========================================================

class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=5000,
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=10000,
    )

    dates: str = Field(
        ...,
        min_length=2,
        max_length=500,
    )

    jurisdiction: Optional[str] = Field(
        default=None,
        max_length=300,
    )


# =========================================================
# Response model
# =========================================================

class DocumentResponse(BaseModel):

    document_type: str

    content: str

    disclaimer: str


# =========================================================
# Generate document
# =========================================================

@router.post(
    "/generate",
    response_model=DocumentResponse,
)
def generate_document(
    request: DocumentRequest,
):

    try:

        generator = GeminiDocumentGenerator()

        document = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
            jurisdiction=request.jurisdiction,
        )

        return DocumentResponse(
            document_type=request.document_type,
            content=document,
            disclaimer=(
                "This document is an AI-generated draft "
                "for informational purposes only. It is "
                "not legal advice. Please have the document "
                "reviewed by a qualified legal professional "
                "before signing or using it."
            ),
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Document generation failed: "
                f"{str(error)}"
            ),
        )
