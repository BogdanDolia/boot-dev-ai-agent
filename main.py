import os
import argparse

from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_function import available_functions, call_function


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        if response.usage_metadata is not None:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        else:
            raise RuntimeError("No usage metadata found in response.")
    if response.function_calls:
        for function_call in response.function_calls:
            # print(f"Calling function: {function_call.name}({function_call.args})")
            content = call_function(function_call, verbose=args.verbose)
            # Extract and print the result from the function response safely
            if content.parts and content.parts[0].function_response:
                fr = content.parts[0].function_response
                resp = getattr(fr, "response", None)
                if isinstance(resp, dict):
                    result = resp.get("result", "")
                else:
                    result = str(resp) if resp is not None else ""
                print(result)
            else:
                print(content)
    else:
        print(response.text)


if __name__ == "__main__":
    main()
