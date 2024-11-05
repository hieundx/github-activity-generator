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

class Args:
    """
    Interface for command-line arguments.
    """
    no_weekends: bool
    max_commits: int
    frequency: int
    repository: str
    user_name: str
    user_email: str
    day_start: datetime
    day_end: datetime
    
    def __init__(self, no_weekends: bool, max_commits: int, frequency: int, repository: str,
                 user_name: str, user_email: str, day_start: datetime, day_end: datetime):
        self.no_weekends = no_weekends
        self.max_commits = max_commits
        self.frequency = frequency
        self.repository = repository
        self.user_name = user_name
        self.user_email = user_email
        self.day_start = day_start
        self.day_end = day_end

    @classmethod
    def from_argparse(cls, args: argparse.Namespace) -> 'Args':
        """
        Create Args instance from argparse.Namespace.
        """
        return cls(
            no_weekends=args.no_weekends,
            max_commits=args.max_commits,
            frequency=args.frequency,
            repository=args.repository,
            user_name=args.user_name,
            user_email=args.user_email,
            day_start=datetime.strptime(args.day_start, '%Y-%m-%d'),
            day_end=datetime.strptime(args.day_end, '%Y-%m-%d') if args.day_end != 'now' else datetime.now()
        )

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

def parse_arguments(argsval: List[str]) -> Args:
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
    parser.add_argument('-ds', '--day_start', type=str,
                        help="Start date to add commits")
    parser.add_argument('-de', '--day_end', type=str, default='now',
                        help="End date to add commits")
    return Args.from_argparse(parser.parse_args(argsval))

def validate_args(args: Args) -> None:
    """
    Validate command-line arguments.
    """
    if not args.repository:
        print('Repository name is required', file=sys.stderr)
        sys.exit(1)
    else:
        try:
            subprocess.check_output(['gh', 'repo', 'view', args.repository])
        except subprocess.CalledProcessError:
            print(f"Repository {args.repository} does not exist", file=sys.stderr)
            sys.exit(1)
    
    if args.day_end < args.day_start:
        print('Start date cannot be after end date', file=sys.stderr)
        sys.exit(1)
    
    if args.day_start > datetime.now():
        print('Start date cannot be in the future', file=sys.stderr)
        sys.exit(1)
            
def create_repository(args: Args) -> str:
    """
    Create and initialize a new Git repository.
    """
    curr_date = datetime.now()
    if args.repository:
        directory = args.repository
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

def configure_git(args: Args) -> None:
    """
    Configure Git user name and email if provided.
    """
    if args.user_name:
        run(['git', 'config', 'user.name', args.user_name])
    if args.user_email:
        run(['git', 'config', 'user.email', args.user_email])

def generate_commits(args: Args) -> None:
    """
    Generate commits based on the specified parameters.
    """
    start_date = args.day_start
    end_date = args.day_end
    
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
    
    try:
        subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        print("Remote origin does not exist, adding...")
        directory_url = json.loads(subprocess.check_output(['gh', 'repo', 'view', '--json', 'url', args.repository]).decode('utf-8').strip())
        run(['git', 'remote', 'add', 'origin', directory_url['url']])
        
    run(['git', 'branch', '-M', MAIN_BRANCH])
    run(['git', 'push', '-u', 'origin', MAIN_BRANCH])

if __name__ == "__main__":
    main()