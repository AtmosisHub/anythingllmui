# Issues, fixes, and lessons learned

## 1. Local model installation temptation
Issue:
The original prompt emphasized avoiding local model downloads, but the first instinct is often to install a model package or a library that expects local weights.

Fix:
This project is designed to use the remote Gemini API only. The Python SDK is used to connect to Gemini over the network, which matches the requirement.

Lesson:
Remote APIs are safer and lighter than local LLM deployment. They also avoid GPU and disk issues.

## 2. Missing API key handling
Issue:
The app can fail if `GEMINI_API_KEY` is not available in the environment.

Fix:
The application checks for the environment variable first and then asks the user to paste the Gemini API key interactively when running the CLI.

Lesson:
Always validate configuration before making API requests.

## 3. Empty prompts
Issue:
An empty prompt caused invalid requests or confusing server output.

Fix:
The app validates prompt text and rejects blank input before sending anything to Gemini.

Lesson:
Fail fast on invalid user input.

## 4. Flask route assumptions
Issue:
A simple web app can break if it assumes the environment variable exists or if the frontend is not configured correctly.

Fix:
The API endpoint validates input and returns a 400 error with a clear message when the key is missing.

Lesson:
User-facing validation should be explicit and easy to understand.

## 5. Avoiding repeated mistakes
Approach used here:
- keep all external configuration in one place
- validate inputs early
- not install models locally
- prompt users for the API key instead of assuming local setup
- document the issue/fix pattern so it is easier to prevent regressions

This keeps the project predictable and aligned with the original requirement: no local model installation, only Gemini API access using the user's key.
