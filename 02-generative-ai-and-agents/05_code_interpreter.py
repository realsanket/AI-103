"""Built-in Code Interpreter — model writes + executes Python in an isolated sandbox.

Prints both the code the model wrote and the answer that came back — so you can
see the difference between "described the math" and "did the math".
"""
from _shared.openai_client import openai_client
from _shared.config import settings


def main() -> None:
    client = openai_client()
    response = client.responses.create(
        model=settings().default_model,
        instructions="You are a data analyst. Use Python to calculate precisely.",
        input="What is the compound interest on $10,000 at 5 percent annual rate over 10 years?",
        tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    )
    for item in response.output:
        if item.type == "code_interpreter_call":
            print("=== Python Code the Model Wrote ===")
            print(item.code)
            print("\n=== Output from Execution ===")
            print(item.outputs)
        elif item.type == "message":
            print("\n=== Final Answer ===")
            print(response.output_text)


if __name__ == "__main__":
    main()
