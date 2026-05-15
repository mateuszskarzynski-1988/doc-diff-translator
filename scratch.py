"""
v3: accept file paths as CLI arguments, so we can test any document pair.
Usage:
  python scratch.py test-documents/contract_v1.txt test-documents/contract_v2.txt
"""
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

cli = argparse.ArgumentParser(description="Compare two document versions using Claude")
cli.add_argument("old", help="Path to the OLD version of the document")
cli.add_argument("new", help="Path to the NEW version of the document")
args = cli.parse_args()

v1 = Path(args.old).read_text(encoding="utf-8")
v2 = Path(args.new).read_text(encoding="utf-8")

prompt = f"""You are comparing two versions of a legal/business document.
Identify every difference between the OLD and NEW version.

For each difference, decide:
- "semantic" — affects meaning, rights, obligations, financial terms, deadlines, scope
- "cosmetic" — pure formatting, rewording without changing meaning, renumbering, punctuation

Return ONLY valid JSON in exactly this format, no prose before or after:

{{
  "summary": "2-3 sentence high-level overview of the changes",
  "changes": [
    {{
      "section": "section number and title, e.g. '5. Termination'",
      "type": "semantic" or "cosmetic",
      "old": "exact phrase from old version (short)",
      "new": "exact phrase from new version (short)",
      "impact": "one sentence on why this matters (skip for cosmetic)"
    }}
  ],
  "stats": {{
    "semantic_count": <number>,
    "cosmetic_count": <number>
  }}
}}

=== OLD VERSION ===
{v1}

=== NEW VERSION ===
{v2}
"""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt}],
)

raw = response.content[0].text
cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

try:
    data = json.loads(cleaned)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except json.JSONDecodeError as e:
    print("=== Claude did not return valid JSON ===")
    print(raw)
    print(f"\nParse error: {e}")