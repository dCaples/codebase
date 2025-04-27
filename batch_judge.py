from openai import AsyncOpenAI
client = AsyncOpenAI()



import re

async def judge(model_answer, correct_answer):
    prompt = (
        "we are testing a security dev by getting them to find a vulnerability in a "
        f"codebase. They say the code is vulnerable to {model_answer}. The correct answer is:\n\n"
        f"{correct_answer}\n\n"
        "Does the dev's response align with the true answer? answer with an integer "
        "from 0 to 10, where 0 is not correct at all and 10 is completely correct. Only respond with score: <your score>"
    )
    response = await client.responses.create(
        model="gpt-4.1",
        input=prompt,
    )
    text = response.output_text
    # try to grab the first number
    m = re.search(r'(-?\d+(?:\.\d+)?)', text)
    if m:
        try:
            num =  float(m.group(1))
            if num < 0 or num > 10:
                return 0.0
            return num
            
        except ValueError:
            return 0.0

    # fallback if nothing parsed
    return 0.0

def judge_batch(answer_problem_pairs):
    """
    answer_problem_pairs: list of tuples (answer, problem_object)
    """
    import asyncio
    loop = asyncio.get_event_loop()
    tasks = [judge(answer, problem_object) for answer, problem_object in answer_problem_pairs]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    return results

if __name__ == "__main__":
    answer_problem_pairs = [
        ("SQL injection", "The code is vulnerable to SQL injection because it does not use parameterized queries."),
        ("XSS from not sanitizing user input", "The code is vulnerable to XSS because it does not sanitize user input."),
        ("Html injection something?", "The code is vulnerable to CSRF because it does not use anti-CSRF tokens."),
    ]
    results = judge_batch(answer_problem_pairs)
    print(results)