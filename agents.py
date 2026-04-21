"""
Generator and Reviewer AI Agents for educational content.

Uses Google Gemini API to generate and review grade-appropriate
educational content with structured JSON output.
"""

import json
import os
import re

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash"


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response text, handling markdown fences."""
    # Try to find JSON inside ```json ... ``` blocks
    match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


class GeneratorAgent:
    """
    Generates draft educational content for a given grade and topic.

    Input:  {"grade": int, "topic": str}
    Output: {"explanation": str, "mcqs": [{"question": str, "options": list, "answer": str}]}
    """

    SYSTEM_PROMPT = (
        "You are an expert educational content writer. "
        "You create clear, accurate, and age-appropriate learning material.\n\n"
        "RULES:\n"
        "1. The explanation must use language appropriate for the given grade level.\n"
        "2. All concepts must be factually correct.\n"
        "3. Generate exactly 4 multiple-choice questions, each with 4 options (A, B, C, D).\n"
        "4. Respond with ONLY valid JSON — no markdown, no commentary.\n\n"
        "OUTPUT FORMAT (strict JSON):\n"
        '{\n'
        '  "explanation": "...",\n'
        '  "mcqs": [\n'
        '    {"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A"}\n'
        '  ]\n'
        '}'
    )

    def run(self, grade: int, topic: str, feedback: list[str] | None = None) -> dict:
        """Generate educational content. Optionally incorporate reviewer feedback."""
        user_msg = f"Grade: {grade}\nTopic: {topic}"

        if feedback:
            user_msg += (
                "\n\nA reviewer found issues with your previous attempt. "
                "Please fix the following problems:\n"
                + "\n".join(f"- {f}" for f in feedback)
            )

        response = client.models.generate_content(
            model=MODEL,
            contents=user_msg,
            config={
                "system_instruction": self.SYSTEM_PROMPT,
                "temperature": 0.7,
            },
        )

        return _extract_json(response.text)


class ReviewerAgent:
    """
    Evaluates Generator output for age-appropriateness, correctness, and clarity.

    Input:  Content JSON from GeneratorAgent + grade level
    Output: {"status": "pass" | "fail", "feedback": [str]}
    """

    SYSTEM_PROMPT = (
        "You are a strict educational content reviewer. "
        "You evaluate learning material for quality and appropriateness.\n\n"
        "EVALUATION CRITERIA:\n"
        "1. Age appropriateness — language complexity must match the grade level.\n"
        "2. Conceptual correctness — all facts and answers must be accurate.\n"
        "3. Clarity — explanations must be easy to understand for the target grade.\n"
        "4. MCQ quality — questions must test concepts from the explanation, "
        "options must be plausible, and the correct answer must be right.\n\n"
        "RULES:\n"
        '- Set status to "pass" ONLY if ALL criteria are fully met.\n'
        '- Set status to "fail" if ANY issue is found.\n'
        "- Each feedback item should be a specific, actionable criticism.\n"
        "- Respond with ONLY valid JSON — no markdown, no commentary.\n\n"
        "OUTPUT FORMAT (strict JSON):\n"
        '{\n'
        '  "status": "pass or fail",\n'
        '  "feedback": ["specific issue 1", "specific issue 2"]\n'
        '}'
    )

    def run(self, content: dict, grade: int) -> dict:
        """Review generated content against quality criteria."""
        user_msg = (
            f"Grade level: {grade}\n\n"
            f"Content to review:\n{json.dumps(content, indent=2)}"
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=user_msg,
            config={
                "system_instruction": self.SYSTEM_PROMPT,
                "temperature": 0.3,
            },
        )

        return _extract_json(response.text)


def run_pipeline(grade: int, topic: str) -> dict:
    """
    Run the full Generator → Reviewer → (optional Refinement) pipeline.

    Returns a dict with all stages:
    {
        "generated": {...},
        "review": {...},
        "refined": {...} | None
    }
    """
    generator = GeneratorAgent()
    reviewer = ReviewerAgent()

    # Step 1: Generate initial content
    generated = generator.run(grade, topic)

    # Step 2: Review the content
    review = reviewer.run(generated, grade)

    result = {
        "generated": generated,
        "review": review,
        "refined": None,
    }

    # Step 3: If review fails, refine once with feedback
    if review.get("status") == "fail":
        refined = generator.run(grade, topic, feedback=review.get("feedback", []))
        refined_review = reviewer.run(refined, grade)
        result["refined"] = refined
        result["refined_review"] = refined_review

    return result
