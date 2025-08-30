ExtractRealtionsAndQuestionsFromChunkSystemPrompt_Rag = r"""
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
    "chunk": "..."
  }
}

RULES
- JSON only. No markdown, no comments, no extra keys.
- Use DOUBLE QUOTES " for all keys and string values (never single quotes).
- Output must be a valid JSON object without line breaks \n or escape sequences.
- No special characters outside valid JSON.
- Echo the input "chunk" with whitespace normalized.
- Do NOT invent entities.
- Entities: concise (≤15 chars), lowercase unless proper noun; deduplicate.
- Relations: Form ≥12 natural language sentences that clearly express how the entities are related. Each relation must read as a proper sentence including the entities.
- relationshipsEntities MUST be the same length as relations; for the i-th relation, relationshipsEntities[i] MUST be a two-item array [subject, object] using exact strings from entities.
- If a relation cannot be mapped to a [subject, object], DROP that relation so lengths stay equal.
- Questions: Form 3–7 questions per chunk, all answerable from chunk.
- relations length and relationshipsEntities must be equal 

"""


ExtractImageIndexFromChunkSystemPrompt_Rag = r"""
TASK
Return ONLY valid JSON per the schema for ONE mainchunk (with optional previouschunk and nextchunk for context).

INPUT
{ "mainchunk": "...", "previouschunk": "...", "nextchunk": "..." }

OUTPUT (conceptual)
{
  "response": {
    "sections": [
      { "imageindex": "7", "description": "One clear sentence (25–40 words) explaining why the image is important and which content it relates to." }
    ]
  }
}

RULES
- JSON only. Double quotes only. No markdown, no extra text, no \n or escapes.
- Detect tokens STRICTLY by regex: (?i)<<\s*image-(\d+)\s*>> . Extract only the digit group as imageindex.
- Use ONLY tokens from mainchunk. Ignore any tokens in previouschunk or nextchunk (they will already be removed).
- Description must come from text immediately after the image token in mainchunk.
- If no text follows the token in mainchunk, use:
  • previouschunk for short heading/context.  
  • nextchunk for continuation text.  
- If multiple tokens exist in mainchunk, output one item per token in original order; no duplicates, no inventions.
- If NO token matches, return exactly: {"response":{"sections":[{"imageindex":"","description":""}]}} .
- Description: one grammatical sentence (25–40 words). Must explain why the image is important and which related content it supports. Start with capital, end with period.
- Use phrasing like “This image helps the doctor by …” or “This image relates to … and allows the user to …”.
- Never output null, None, or "null".
"""
