from openai import AsyncOpenAI
import asyncio

client = AsyncOpenAI()

async def run_shield(problem):
    code = problem['filetext']
    prompt = f"read through this codebase and find the security vulnerability. Code:\n\n{code}"
    response = await client.responses.create(
        model="gpt-4.1",
        tools=[{"type": "web_search_preview"}],
        input=prompt,
    )
    model_answer = response.output_text
    correct_answer = problem["readme"]
    return model_answer, correct_answer


def run_shield_batch(problems):
    """
    problems: list of problem objects
    """
    loop = asyncio.get_event_loop()
    tasks = [run_shield(problem) for problem in problems]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    return results


def main():
    # Define a list of problems with vulnerable code and the expected vulnerability descriptions
    problems = [
        {
            "filetext": '''
def insecure_eval(user_input):
    # Unsafe evaluation of user input
    result = eval(user_input)
    return result
''',
            "readme": "The code uses eval on unsanitized user input, allowing arbitrary code execution."
        },
        {
            "filetext": '''
import sqlite3

def get_user_balance(user_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    # SQL query constructed with direct string interpolation
    query = f"SELECT balance FROM accounts WHERE user_id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchone()[0]
''',
            "readme": "The code constructs an SQL query by directly interpolating user_id, leading to SQL injection vulnerability."
        }
    ]

    # Run the batch of problems through the shield
    results = run_shield_batch(problems)

    # Print out the model's findings versus the expected answers
    for idx, (model_answer, correct_answer) in enumerate(results, start=1):
        print(f"Problem {idx}:")
        print("Model's Answer:\n", model_answer)
        print("Expected Answer:\n", correct_answer)
        print("-" * 40)


if __name__ == "__main__":
    main()
