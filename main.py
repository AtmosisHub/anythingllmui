from __future__ import annotations

from anyllm import generate_response, get_api_key


def run_cli() -> None:
    print("AnyLLM - Gemini API client")
    print("No local model is installed. This app uses Google Gemini via your API key.")

    try:
        api_key = get_api_key(prompt_on_missing=True)
    except ValueError:
        print("A Gemini API key is required to continue.")
        return

    while True:
        try:
            prompt = input("\nYou: ").strip()
        except EOFError:
            print("\nSession ended.")
            break

        if not prompt:
            continue
        if prompt.lower() in {"quit", "exit", "bye"}:
            print("Goodbye!")
            break

        try:
            answer = generate_response(prompt, api_key=api_key)
            print(f"\nGemini: {answer}")
        except Exception as exc:
            print(f"Error: {exc}")
            print("Please verify your Gemini API key and network access.")


if __name__ == "__main__":
    run_cli()
