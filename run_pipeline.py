#!/usr/bin/env python3
# run_pipeline.py

from run_agent import run_shield_batch
from batch_judge import judge_batch

def main():
    # same problem definitions as in run_agent.py
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

    # 1) run the “shield” agent on each problem
    agent_results = run_shield_batch(problems)
    # agent_results is a list of (model_answer, correct_answer)

    # 2) judge each model_answer against its correct_answer
    scores = judge_batch(agent_results)
    # scores is a list of floats in [0.0, 10.0]

    # 3) print a combined report
    for idx, ((model_answer, correct_answer), score) in enumerate(zip(agent_results, scores), start=1):
        print(f"Problem {idx}:")
        print("Model's Answer:")
        print(model_answer.strip(), "\n")
        print("Expected Answer:")
        print(correct_answer, "\n")
        print(f"Score: {score:.1f}/10")
        print("-" * 40)

if __name__ == "__main__":
    main()
