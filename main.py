import os
import argparse

from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_function import available_functions, call_function


def main():
    try:
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error initializing client: {e}")
        return

    try:
        parser = argparse.ArgumentParser(description="Chatbot")
        parser.add_argument("user_prompt", type=str, help="User prompt")
        parser.add_argument(
            "--verbose", action="store_true", help="Enable verbose output"
        )
        args = parser.parse_args()
    except Exception as e:
        print(f"Error parsing arguments: {e}")
        return

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    max_turns = 20
    for turn in range(max_turns):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                ),
            )
        except Exception as e:
            print(f"Error generating content: {e}")
            break

        try:
            if args.verbose:
                if response.usage_metadata is not None:
                    print(
                        f"Turn {turn + 1}: Prompt tokens: {response.usage_metadata.prompt_token_count}"
                    )
                    print(
                        f"Turn {turn + 1}: Response tokens: {response.usage_metadata.candidates_token_count}"
                    )
                else:
                    print("Warning: No usage metadata found in response.")
        except Exception as e:
            if args.verbose:
                print(f"Error processing usage metadata: {e}")

        # Add each candidate's content to the conversation history
        try:
            if response.candidates:  # Check if candidates is not None or empty
                for candidate in response.candidates:
                    if candidate.content is not None:
                        messages.append(candidate.content)
            else:
                print("No candidates returned in the response.")
        except Exception as e:
            print(f"Error processing candidates: {e}")
            break

        # Check if the model is finished (no function calls and has text response)
        try:
            if not response.function_calls and response.text:
                print(response.text)
                break
        except Exception as e:
            print(f"Error checking response completion: {e}")
            break

        # Process function calls if present
        try:
            if response.function_calls:
                for function_call in response.function_calls:
                    try:
                        # Execute the tool and append the tool response to the transcript
                        content = call_function(function_call, verbose=args.verbose)
                        messages.append(content)
                    except Exception as e:
                        print(f"Error calling function {function_call.name}: {e}")
                        # Add error response to messages so the model knows what went wrong
                        error_content = types.Content(
                            role="tool",
                            parts=[
                                types.Part.from_function_response(
                                    name=function_call.name,
                                    response={
                                        "error": f"Function execution failed: {str(e)}"
                                    },
                                )
                            ],
                        )
                        messages.append(error_content)
            else:
                # No function calls and no text - break to avoid infinite loop
                break
        except Exception as e:
            print(f"Error processing function calls: {e}")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
