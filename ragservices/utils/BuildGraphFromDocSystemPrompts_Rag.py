ExtractEntityGragSystemPrompt = r"""
TASK
Return ONLY valid JSON per the schema for ONE input chunk.

INPUT
{ "chunk": "..." }

OUTPUT (conceptual)
{
  "response": {
    "entities": ["..."],
    "relations": ["..."],
    "questions": ["..."],
    "relationshipsEntities": [["A","B"], ...],
    "chunk": "...",
    "sections": [
    ]
  }
}

RULES
- JSON only. No markdown, no comments, no extra keys.
- Echo the input "chunk" with whitespace normalized.
- Do NOT invent entities/links/images.
- Entities: concise (≤15 chars), lowercase unless proper noun; deduplicate.
- Relations: Form ≥12 relations between entities. KG-friendly style:
   • subject → predicate → object
- Questions: Form 3–7 questions per chunk, all answerable from chunk.
- Don’t drop any images (<<IMAGE-N>>) or links from the chunk.

SECTION RULES (STRICT)
- Output an "image" ONLY if the exact token <<IMAGE-N>> appears in THIS chunk.
- If no image appears in this chunk  token <<IMAGE-N>> , set sections = [].
- If an image appears on the SAME line as a section header → attach to that section.
- If an image appears AFTER a section header but BEFORE the next header → attach to that section.
- If an image appears BEFORE the FIRST subsection header (e.g., before "1.1") → attach it to the PARENT major section (e.g., "1.0"), NOT to "1.1".
- If multiple images appear, assign each to the closest correct section; no duplication.
- Never invent, move, or reassign images across chunks.



"""
