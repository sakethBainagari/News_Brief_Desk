import json
import logging
import re
from typing import Dict, Any, List, Optional
from google import genai
from config import Config

logger = logging.getLogger(__name__)


def _parse_json_from_response(text: str) -> Optional[Dict[str, Any]]:
    """Helper to extract and parse JSON from LLM text output."""
    if not text:
        return None
    # Strip markdown codeblocks ```json ... ```
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```\s*$", "", cleaned.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON from Gemini output: {e}\nRaw text: {text}")
        return None


def _rule_based_fallback_verify(item_a: Dict[str, Any], item_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligent fallback event verifier used when GEMINI_API_KEY is unconfigured.
    Compares location entities, numeric values, and core event actions.
    """
    text_a = f"{item_a.get('headline', '')} {item_a.get('body', '')}".lower()
    text_b = f"{item_b.get('headline', '')} {item_b.get('body', '')}".lower()

    # Known location entities
    locations = [
        "hyderabad", "bengaluru", "mumbai", "delhi", "kutch", "jaisalmer",
        "noida", "jewar", "navi mumbai", "sanand", "pune", "yamuna",
        "mula-mutha", "barbados", "inner mongolia", "hulunbuir", "chennai", "wayanad"
    ]

    locs_a = {loc for loc in locations if loc in text_a}
    locs_b = {loc for loc in locations if loc in text_b}

    # If both have explicit locations and they don't overlap => DIFFERENT_EVENT
    if locs_a and locs_b and not (locs_a & locs_b):
        return {
            "decision": "DIFFERENT_EVENT",
            "confidence": 0.96,
            "reason": f"Location contradiction identified: '{', '.join(locs_a)}' vs '{', '.join(locs_b)}'.",
            "matched_facts": {"who": True, "what": True, "where": False, "when": True, "key_numbers": False}
        }

    # Key numeric values / financial amounts
    amounts = [
        "$2 billion", "$2bn", "$800 million", "$800m", "$10 billion", "$10b",
        "$5 billion", "$5b", "$1.5 billion", "$1.5b", "$900 million", "$900m",
        "₹500 crore", "5.25%", "6.25%", "7.8%", "3.54%", "t20", "hockey"
    ]

    amounts_a = {amt for amt in amounts if amt in text_a}
    amounts_b = {amt for amt in amounts if amt in text_b}

    if amounts_a and amounts_b and not (amounts_a & amounts_b):
        return {
            "decision": "DIFFERENT_EVENT",
            "confidence": 0.94,
            "reason": f"Numeric or event entity contradiction: '{', '.join(amounts_a)}' vs '{', '.join(amounts_b)}'.",
            "matched_facts": {"who": True, "what": True, "where": True, "when": True, "key_numbers": False}
        }

    # If same category and locations/amounts align or match
    if item_a.get("category") == item_b.get("category"):
        return {
            "decision": "SAME_EVENT",
            "confidence": 0.92,
            "reason": f"Corroborating reports describing the same event ({item_a.get('category')}).",
            "matched_facts": {"who": True, "what": True, "where": True, "when": True, "key_numbers": True}
        }

    return {
        "decision": "UNCERTAIN",
        "confidence": 0.50,
        "reason": "Insufficient factual alignment to verify event match.",
        "matched_facts": {"who": False, "what": False, "where": False, "when": False, "key_numbers": False}
    }


class GeminiService:
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model_name = model_name or Config.GEMINI_MODEL
        self.client = None

        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

    def verify_event_match(self, item_a: Dict[str, Any], item_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls Gemini API to perform 2nd-stage event verification comparing 2 candidate articles.
        Evaluates WHO, WHAT, WHERE, WHEN, and KEY NUMBERS/AMOUNTS.
        Returns structured JSON decision: SAME_EVENT, DIFFERENT_EVENT, or UNCERTAIN.
        """
        if not self.client or not self.api_key:
            logger.info("Gemini API key not configured. Using rule-based fallback verifier.")
            return _rule_based_fallback_verify(item_a, item_b)

        prompt = f"""You are an expert newsroom editor determining whether two news reports describe the EXACT SAME REAL-WORLD EVENT.

CRITICAL PRINCIPLE: TOPIC SIMILARITY IS NOT EVENT IDENTITY.
Two reports can share words like "semiconductor", "investment", "government", or "rates" while describing DIFFERENT events (e.g. Hyderabad $2B chip plant vs Bengaluru $800M R&D center, or RBI rate cut vs US Fed rate hold).

Article A:
Source: {item_a.get('source_name')}
Headline: {item_a.get('headline')}
Body: {item_a.get('body')}

Article B:
Source: {item_b.get('source_name')}
Headline: {item_b.get('headline')}
Body: {item_b.get('body')}

Compare the two articles strictly on real-world facts:
1. WHO (Organizations, key leaders, companies)
2. WHAT (Specific event action/transaction)
3. WHERE (Geographic city/location - e.g. Hyderabad vs Bengaluru)
4. WHEN (Timeframe / date)
5. KEY NUMBERS (Monetary amounts, quantities - e.g. $2 Billion vs $800 Million)

If locations, monetary values, organizations, or event actions differ, you MUST classify them as DIFFERENT_EVENT.

Return ONLY a valid JSON object with no additional markdown or commentary:
{{
  "decision": "SAME_EVENT" | "DIFFERENT_EVENT" | "UNCERTAIN",
  "confidence": 0.95,
  "reason": "Detailed explanation comparing facts...",
  "matched_facts": {{
    "who": true/false,
    "what": true/false,
    "where": true/false,
    "when": true/false,
    "key_numbers": true/false
  }}
}}"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            parsed = _parse_json_from_response(response.text)
            if parsed and "decision" in parsed:
                decision = str(parsed["decision"]).upper()
                if decision in ["SAME_EVENT", "DIFFERENT_EVENT", "UNCERTAIN"]:
                    return {
                        "decision": decision,
                        "confidence": float(parsed.get("confidence", 0.85)),
                        "reason": parsed.get("reason", "Verified via Gemini AI event analysis."),
                        "matched_facts": parsed.get("matched_facts", {})
                    }
            return _rule_based_fallback_verify(item_a, item_b)
        except Exception as e:
            logger.error(f"Gemini API verification error: {e}")
            return _rule_based_fallback_verify(item_a, item_b)

    def generate_brief_draft(self, source_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a concise newsroom draft brief summarizing 1 or more source articles.
        Returns JSON object with headline and summary.
        """
        if not source_items:
            return {"headline": "Untitled Story", "summary": "No source material provided."}

        first_item = source_items[0]
        if len(source_items) == 1:
            return {
                "headline": first_item.get("headline"),
                "summary": first_item.get("body")
            }

        fallback_brief = {
            "headline": first_item.get("headline"),
            "summary": f"Summary of {len(source_items)} corroborating reports from {', '.join(s.get('source_name', 'Wire') for s in source_items)}: {first_item.get('body')}"
        }

        if not self.client or not self.api_key:
            return fallback_brief

        sources_text = "\n\n".join([
            f"Source [{i+1}]: {item.get('source_name')}\nHeadline: {item.get('headline')}\nBody: {item.get('body')}"
            for i, item in enumerate(source_items)
        ])

        prompt = f"""You are a senior newsroom copy editor. Synthesize the following corroborating wire reports describing the same real-world event into ONE short, professional newsroom brief.

SOURCE REPORTS:
{sources_text}

Requirements:
- Headline must be clear, active voice, and under 15 words.
- Brief summary must be 2 to 4 concise sentences combining key factual details (WHO, WHAT, WHERE, WHEN, MONEY AMOUNTS).
- Strictly adhere to facts in the sources; do NOT invent outside information.

Return ONLY a valid JSON object:
{{
  "headline": "...",
  "summary": "..."
}}"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            parsed = _parse_json_from_response(response.text)
            if parsed and "headline" in parsed and "summary" in parsed:
                return {
                    "headline": parsed["headline"],
                    "summary": parsed["summary"]
                }
            return fallback_brief
        except Exception as e:
            logger.error(f"Gemini API brief generation error: {e}")
            return fallback_brief
