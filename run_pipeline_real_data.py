#!/usr/bin/env python3
# run_pipeline_real_data.py

import json
import os
import datetime
from run_agent import run_shield_batch
from batch_judge import judge_batch

def process_batch(batch, batch_num, log_file):
    print(f"Processing batch {batch_num} with {len(batch)} problems...")
    
    # 1) run the "shield" agent on the batch of problems
    agent_results = run_shield_batch(batch)
    # agent_results is a list of (model_answer, correct_answer)

    # 2) judge each model_answer against its correct_answer
    scores = judge_batch(agent_results)
    # scores is a list of floats in [0.0, 10.0]

    # 3) write results to log file
    with open(log_file, 'a') as f:
        f.write(f"\n\n{'='*50}\n")
        f.write(f"BATCH {batch_num} RESULTS\n")
        f.write(f"{'='*50}\n\n")
        
        for idx, ((model_answer, correct_answer), score) in enumerate(zip(agent_results, scores), start=1):
            problem_idx = (batch_num - 1) * 10 + idx
            f.write(f"Problem {problem_idx}:\n")
            f.write("Model's Answer:\n")
            f.write(f"{model_answer.strip()}\n\n")
            f.write("Expected Answer:\n")
            f.write(f"{correct_answer}\n\n")
            f.write(f"Score: {score:.1f}/10\n")
            f.write(f"{'-'*40}\n\n")
    
    # 4) print a summary for this batch
    avg_score = sum(scores) / len(scores) if scores else 0
    print(f"Batch {batch_num} complete. Average score: {avg_score:.2f}/10")
    print(f"Results written to {log_file}")
    
    return scores

def main():
    # Load real problem data from problems_filtered.json
    with open('problems_filtered.json', 'r') as f:
        all_problems = json.load(f)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/pipeline_results_{timestamp}.log"
    
    # Initialize the log file with header
    with open(log_file, 'w') as f:
        f.write(f"PIPELINE RESULTS - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total problems: {len(all_problems)}\n")
    
    # Process problems in batches of 10
    batch_size = 10
    all_scores = []
    
    for i in range(0, len(all_problems), batch_size):
        batch_num = (i // batch_size) + 1
        batch = all_problems[i:i+batch_size]
        batch_scores = process_batch(batch, batch_num, log_file)
        all_scores.extend(batch_scores)
    
    # Write summary to log file
    with open(log_file, 'a') as f:
        f.write("\n\n" + "="*50 + "\n")
        f.write("FINAL SUMMARY\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total problems processed: {len(all_scores)}\n")
        f.write(f"Average score: {sum(all_scores) / len(all_scores):.2f}/10\n")
        
        # Score distribution
        score_ranges = {
            "0-2": 0,
            "2-4": 0,
            "4-6": 0,
            "6-8": 0,
            "8-10": 0
        }
        
        for score in all_scores:
            if 0 <= score < 2:
                score_ranges["0-2"] += 1
            elif 2 <= score < 4:
                score_ranges["2-4"] += 1
            elif 4 <= score < 6:
                score_ranges["4-6"] += 1
            elif 6 <= score < 8:
                score_ranges["6-8"] += 1
            else:
                score_ranges["8-10"] += 1
        
        f.write("\nScore distribution:\n")
        for range_name, count in score_ranges.items():
            percentage = (count / len(all_scores)) * 100
            f.write(f"{range_name}: {count} problems ({percentage:.1f}%)\n")
    
    print(f"\nAll batches processed. Full results available in {log_file}")
    print(f"Average score across all problems: {sum(all_scores) / len(all_scores):.2f}/10")

if __name__ == "__main__":
    main()