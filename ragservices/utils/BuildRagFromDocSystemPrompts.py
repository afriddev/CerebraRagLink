ExtractClaimsAndQuestionsFromChunkSystemPrompt = r"""
TASK
Return ONLY valid JSON per the schema for ONE input chunk.

INPUT
{ "chunk": "..." }

OUTPUT (conceptual)
{
  "response": {
    "claims": ["..."],
    "questions": ["..."],
    "chunk": "..."
  }
}

RULES
- JSON only. No markdown, no comments, no extra keys.
- Use DOUBLE QUOTES " for all keys and string values (never single quotes).
- Output must be a valid JSON object without line breaks \n or escape sequences.
- Echo the input "chunk" with whitespace normalized.
- Do NOT invent entities.
- Claims: Form ≥9 atomic, factual, standalone sentences derived from the chunk. Each claim must read as a proper statement with clear meaning, not fragments.
- Questions: Form ≥5 natural language questions that can be answered using only the current chunk.
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
      { "imageindex": "7", "description": "One clear sentence (15–30 words) explaining why the image is important and which content it relates to." }
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
- Description: one grammatical sentence (15–30 words). Must explain why the image is important and which related content it supports. Start with capital, end with period.
- Use phrasing like “This image helps ..” or “This image relates to ..”.
- Never output null, None, or "null".
"""
