"""
Module: Team Management Implementation

This module provides functions for managing a team in a quantitative finance portfolio.

Requirements:
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: r, Databricks
- Demonstrate quant skills related to: presales, team management, consulting
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

from typing import List, Dict

def assign_tasks(team: List[str], tasks: List[str]) -> Dict[str, str]:
    """
    Assign tasks to team members.

    Args:
    team (List[str]): List of team members
    tasks (List[str]): List of tasks to be assigned

    Returns:
    Dict[str, str]: A dictionary mapping team members to tasks assigned
    """
    if len(team) == 0:
        raise ValueError("Team cannot be empty")
    
    if len(tasks) == 0:
        raise ValueError("Tasks cannot be empty")
    
    assigned_tasks = {}
    for i in range(len(tasks)):
        assigned_tasks[team[i % len(team)]] = tasks[i]
    
    return assigned_tasks

if __name__ == "__main__":
    team = ["Alice", "Bob", "Charlie"]
    tasks = ["Task 1", "Task 2", "Task 3", "Task 4"]
    
    assigned_tasks = assign_tasks(team, tasks)
    for member, task in assigned_tasks.items():
        print(f"{member} has been assigned: {task}")