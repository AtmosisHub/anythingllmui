from __future__ import annotations

import os
import sys

from anyllm import generate_response


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set GEMINI_API_KEY before running this verification script.")

    prompts = [
        "Say hello in one sentence.",
        "What is the capital of France?",
        "Give me a 2-bullet summary of Python.",
    ]

    for attempt in range(1, 4):
        print(f"Attempt {attempt}/3")
        for prompt in prompts:
            response = generate_response(prompt, api_key=api_key)
            if not response or not response.strip():
                raise SystemExit(f"Empty response for prompt: {prompt}")
            print(f"Prompt: {prompt}")
            print(f"Response: {response[:120]}")
            print("---")

    print("All repeated Gemini checks passed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - verification script
        print(f"Verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
