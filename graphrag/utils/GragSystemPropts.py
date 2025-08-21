ExtractEntityGragSystemPrompt = r"""
TASK
Return ONLY valid JSON per the schema for ONE input chunk.

INPUT
{ "chunk": "..." }

OUTPUT (conceptual)
{
  "response": {
    "entities": ["..."],
    "relations": ["..."],   // short declarative KG-style relations
    "relationshipsEntities": [["A","B"], ...],
    "chunk": "..."
  }
}

RULES
- JSON only. No markdown, no comments, no extra keys.
- Echo the input "chunk" with whitespace normalized.
- Do NOT invent entities/links/images.
- Entities: concise (≤24 chars), lowercase unless proper noun; deduplicate.
- Relations: 12–15 when possible; deduplicate; must be short factual statements (no questions).
- Relations should follow a KG-friendly style:
   • subject → predicate → object
   • Example: "doctors update patient records"
   • Not: "How do doctors update patient records?"
Dont remove any images (<<IMAGE-N>>) or links from the chunk.
---

EXAMPLE

INPUT
{ "chunk": "1.2.3 Patient Records <<image-1>> The system allows doctors to update patient history and medications." }

OUTPUT
{
  "response": {
    "entities": ["patient records", "doctors", "patient history", "medications"],
    "relations": [
      "doctors update patient records",
      "patient records include patient history",
      "patient records include medications",
      "patient history belongs to patient records",
      "medications are stored in patient records",
      "doctors use patient records for treatment",
      "patient records support treatment decisions"
    ],
    "relationshipsEntities": [
      ["doctors", "patient records"],
      ["patient records", "patient history"],
      ["patient records", "medications"],
      ["patient history", "patient records"],
      ["medications", "patient records"]
    ],
    "chunk": "1.2.3 Patient Records <<image-1>> The system allows doctors to update patient history and medications"
  }
}
"""
