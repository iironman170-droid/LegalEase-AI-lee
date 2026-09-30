import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load .env
load_dotenv()


class GeminiDocumentGenerator:

    def __init__(self):

        self.api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        if not self.api_key:

            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Please add it to your .env file."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )


    # =====================================================
    # Generate document
    # =====================================================

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        jurisdiction: str | None = None,
    ) -> str:

        if not jurisdiction:
            jurisdiction = "Not specified"


        prompt = f"""
You are LegalEase, an AI-powered legal document
drafting assistant.

Create a professional, structured and editable
FIRST DRAFT of the requested legal document.

IMPORTANT RULES:

1. Do not provide legal advice.

2. Do not claim that the generated document is
   legally valid or legally enforceable.

3. Do not invent important facts.

4. Do not invent names, addresses, amounts,
   dates, laws or court information.

5. If important information is missing, write:

   [TO BE COMPLETED]

6. Preserve all information supplied by the user.

7. Use professional and readable legal language.

8. Organize the document using numbered sections.

9. Include signature sections at the end.

10. Do not use Markdown code fences.

11. Return only the legal document.

--------------------------------------------------
DOCUMENT INFORMATION
--------------------------------------------------

Document Type:
{document_type}

Parties:
{parties}

Effective Date:
{dates}

Jurisdiction:
{jurisdiction}

Terms and Conditions:
{terms}

--------------------------------------------------
DOCUMENT STRUCTURE
--------------------------------------------------

Create an appropriate legal document.

Depending on the document type, use relevant
sections such as:

1. Title
2. Parties
3. Purpose
4. Definitions
5. Scope
6. Responsibilities
7. Payment
8. Confidentiality
9. Intellectual Property
10. Term and Termination
11. Representations
12. Dispute Resolution
13. Governing Law
14. Notices
15. Entire Agreement
16. Amendments
17. Severability
18. Signatures

Only include sections relevant to the requested
document.

Do not invent information.

If information is required but not provided,
use:

[TO BE COMPLETED]

--------------------------------------------------

Generate the complete professional draft now.
"""


        response = self.client.models.generate_content(

            model=self.model_name,

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.2,

                max_output_tokens=12000,
            ),
        )


        result = response.text


        if not result:

            raise RuntimeError(
                "Gemini returned an empty response."
            )


        return self.clean_text(result)


    # =====================================================
    # Clean generated text
    # =====================================================

    @staticmethod
    def clean_text(text: str) -> str:

        replacements = {

            "\u2018": "'",

            "\u2019": "'",

            "\u201c": '"',

            "\u201d": '"',

            "\u2013": "-",

            "\u2014": "-",

            "\u2026": "...",

            "\u00a0": " ",
        }


        for old, new in replacements.items():

            text = text.replace(
                old,
                new,
            )


        return text.strip()