#!/usr/bin/env python3
# repo_scanner.py

import os
import subprocess
import shutil
import json
from run_agent import run_shield_batch

def scan_github_repo(github_url):
    """
    Given a GitHub URL:
    1. Clones the repo to ./repo
    2. Runs code2prompt to generate code.md
    3. Runs the shield function to find vulnerabilities
    4. Returns the vulnerabilities as a string
    
    Args:
        github_url (str): URL of the GitHub repository to scan
        
    Returns:
        str: Identified vulnerabilities
    """
    # Step 1: Clone the repository
    print(f"Cloning repository from {github_url}...")
    repo_dir = "./repo"
    
    # Remove repo directory if it already exists
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    
    try:
        subprocess.run(["git", "clone", github_url, repo_dir], 
                      check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return f"Error cloning repository: {e.stderr}"
    
    # Step 2: Run code2prompt
    print("Generating code summary...")
    try:
        code_md_path = "code.md"
        subprocess.run(["code2prompt", "--path", repo_dir, "--output", code_md_path],
                      check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return f"Error running code2prompt: {e.stderr}"
    
    # Step 3: Read the generated code.md file
    try:
        with open(code_md_path, 'r') as f:
            code_content = f.read()
    except Exception as e:
        return f"Error reading code.md: {str(e)}"
    
    # Step 4: Prepare problem for the shield function
    problem = {
        "filetext": code_content,
        "readme": "Security scan for GitHub repository"
    }
    
    # Step 5: Run the shield function to find vulnerabilities
    print("Analyzing for security vulnerabilities...")
    results = run_shield_batch([problem])
    model_answer, _ = results[0]
    
    # Step 6: Format and return the results
    repo_name = github_url.split('/')[-1].replace('.git', '')
    
    vulnerability_report = f"""
==============================================
SECURITY VULNERABILITY REPORT FOR {repo_name}
==============================================

GitHub Repository: {github_url}
Scan Date: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}

IDENTIFIED VULNERABILITIES:
---------------------------
{model_answer}
"""
    
    # Clean up - remove the repo directory and code.md
    print("Cleaning up temporary files...")
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    if os.path.exists(code_md_path):
        os.remove(code_md_path)
    
    return vulnerability_report

def save_report(report, output_file=None):
    """
    Save the vulnerability report to a file
    
    Args:
        report (str): The vulnerability report
        output_file (str, optional): Output file path. If None, a default path is used.
    
    Returns:
        str: Path to the saved report file
    """
    if output_file is None:
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        # Generate a timestamp-based filename
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"reports/vulnerability_report_{timestamp}.txt"
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    return output_file

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan a GitHub repository for security vulnerabilities')
    parser.add_argument('url', help='GitHub repository URL')
    parser.add_argument('--output', '-o', help='Output file for the vulnerability report')
    
    args = parser.parse_args()
    
    # Run the scan
    report = scan_github_repo(args.url)
    
    # Save the report
    output_path = save_report(report, args.output)
    
    print(f"\nVulnerability scan completed!")
    print(f"Report saved to: {output_path}")
    print("\nSummary of findings:")
    
    # Print a brief summary (first few lines) of the report
    summary_lines = [line for line in report.split('\n') if line.strip()][:10]
    print('\n'.join(summary_lines))
    print("...")

if __name__ == "__main__":
    main()