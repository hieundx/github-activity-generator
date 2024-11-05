#!/usr/bin/env python
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from random import randint
from subprocess import Popen
from typing import List, Optional

# Constants
MAX_COMMITS_PER_DAY = 20
MIN_COMMITS_PER_DAY = 1
DEFAULT_MAX_COMMITS = 10
DEFAULT_FREQUENCY = 80
DEFAULT_DAYS_BEFORE = 365
DEFAULT_DAYS_AFTER = 0
REPOSITORY_PREFIX = 'repository-'
README_FILENAME = 'README.md'
MAIN_BRANCH = 'main'

def main(def_args: List[str] = sys.argv[1:]) -> None:
    """
    Main function to generate a Git repository with fake contributions.
    """
    args = parse_arguments(def_args)
    validate_args(args)
    directory_exists = create_repository(args)
    if not directory_exists:
        configure_git(args)
    generate_commits(args)
    push_to_remote(args)
    print('\nRepository generation ' +
          '\x1b[6;30;42mcompleted successfully\x1b[0m!')

def parse_arguments(argsval: List[str]) -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Generate a Git repository with fake contributions.")
    parser.add_argument('-nw', '--no_weekends', action='store_true', default=False,
                        help="Do not commit on weekends")
    parser.add_argument('-mc', '--max_commits', type=int, default=DEFAULT_MAX_COMMITS,
                        help=f"Maximum number of commits per day (1-{MAX_COMMITS_PER_DAY})")
    parser.add_argument('-fr', '--frequency', type=int, default=DEFAULT_FREQUENCY,
                        help="Percentage of days to commit (0-100)")
    parser.add_argument('-r', '--repository', type=str,
                        help="Remote git repository URL (SSH or HTTPS)")
    parser.add_argument('-un', '--user_name', type=str,
                        help="Git user.name config override")
    parser.add_argument('-ue', '--user_email', type=str,
                        help="Git user.email config override")
    parser.add_argument('-db', '--days_before', type=int, default=DEFAULT_DAYS_BEFORE,
                        help="Number of days before current date to start commits")
    parser.add_argument('-da', '--days_after', type=int, default=DEFAULT_DAYS_AFTER,
                        help="Number of days after current date to end commits")
    return parser.parse_args(argsval)

def validate_args(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments.
    """
    if args.days_before < 0:
        sys.exit('days_before must not be negative')
    if args.days_after < 0:
        sys.exit('days_after must not be negative')

def create_repository(args: argparse.Namespace) -> str:
    """
    Create and initialize a new Git repository.
    """
    curr_date = datetime.now()
    if args.repository:
        directory = extract_repo_name(args.repository)
    else:
        directory = f"{REPOSITORY_PREFIX}{curr_date.strftime('%Y-%m-%d-%H-%M-%S')}"
    if os.path.exists(directory):
        os.chdir(directory)
        return True
    os.mkdir(directory)
    os.chdir(directory)
    run(['git', 'init', '-b', MAIN_BRANCH])
    return False

def extract_repo_name(repository: str) -> str:
    """
    Extract repository name from the given URL.
    """
    pattern = r'git@github\.com:.+/(.+)(?:\.git)?$'
    match = re.search(pattern, repository)
    return match.group(1) if match else ''

def configure_git(args: argparse.Namespace) -> None:
    """
    Configure Git user name and email if provided.
    """
    if args.user_name:
        run(['git', 'config', 'user.name', args.user_name])
    if args.user_email:
        run(['git', 'config', 'user.email', args.user_email])

def generate_commits(args: argparse.Namespace) -> None:
    """
    Generate commits based on the specified parameters.
    """
    curr_date = datetime.now()
    start_date = curr_date.replace(hour=14, minute=0) - timedelta(days=args.days_before)
    end_date = start_date + timedelta(days=args.days_after)
    
    print('start date: ' + start_date.strftime('%Y-%m-%d %H:%M'))
    print('end date: ' + end_date.strftime('%Y-%m-%d %H:%M'))

    for day in date_range(start_date, end_date):
        if should_commit(day, args.no_weekends, args.frequency):
            for commit_time in commit_times_for_day(day, args):
                create_commit(commit_time)

def date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    Generate a list of dates between start_date and end_date.
    """
    return [start_date + timedelta(n) for n in range((end_date - start_date).days + 1)]

def should_commit(day: datetime, no_weekends: bool, frequency: int) -> bool:
    """
    Determine if a commit should be made on the given day.
    """
    return (not no_weekends or day.weekday() < 5) and randint(0, 100) < frequency

def commit_times_for_day(day: datetime, args: argparse.Namespace) -> List[datetime]:
    """
    Generate commit times for a given day.
    """
    num_commits = contributions_per_day(args)
    return [day + timedelta(minutes=m) for m in range(num_commits)]

def create_commit(date: datetime) -> None:
    """
    Create a single commit with the given date.
    """
    with open(README_FILENAME, 'a') as file:
        file.write(f"{message(date)}\n\n")
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', f'"{message(date)}"',
         '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])

def run(commands: List[str]) -> None:
    """
    Run a shell command and wait for it to complete.
    """
    Popen(commands).wait()

def message(date: datetime) -> str:
    """
    Generate a commit message for the given date.
    """
    return date.strftime('Contribution: %Y-%m-%d %H:%M')

def contributions_per_day(args: argparse.Namespace) -> int:
    """
    Determine the number of contributions for a day.
    """
    max_commits = min(max(args.max_commits, MIN_COMMITS_PER_DAY), MAX_COMMITS_PER_DAY)
    return randint(MIN_COMMITS_PER_DAY, max_commits)

def push_to_remote(args) -> None:
    """
    Push the generated commits to the remote repository if specified.
    """
    # try:
    #     subprocess.check_output(['gh', 'repo', 'view', directory])
    # except subprocess.CalledProcessError:
    #     print(f"Repository {directory} does not exist, creating...")
    #     run(['gh', 'repo', 'create', '--private', directory])
    
    # directory_url = json.loads(subprocess.check_output(['gh', 'repo', 'view', '--json', 'url', directory]).decode('utf-8').strip())
    
    try:
        subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        print("Remote origin does not exist, adding...")
        run(['git', 'remote', 'add', 'origin', args.repository])
        
    run(['git', 'branch', '-M', MAIN_BRANCH])
    run(['git', 'push', '-u', 'origin', MAIN_BRANCH])

if __name__ == "__main__":
    main()