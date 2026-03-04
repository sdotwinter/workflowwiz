#!/usr/bin/env python3
"""
WorkflowWiz - No-code Visual Workflow Automation for DevOps
A CLI tool to create, visualize, and run automated workflows.
"""

import click
import json
import yaml
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# ANSI colors for visual output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    id: str
    name: str
    command: str
    enabled: bool = True
    status: StepStatus = StepStatus.PENDING
    output: str = ""
    duration: float = 0

@dataclass
class Workflow:
    name: str
    description: str
    version: str = "1.0.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Workflow':
        steps = [
            WorkflowStep(
                id=step.get('id', f'step_{i}'),
                name=step.get('name', f'Step {i+1}'),
                command=step.get('command', ''),
                enabled=step.get('enabled', True)
            )
            for i, step in enumerate(data.get('steps', []))
        ]
        return cls(
            name=data.get('name', 'Untitled'),
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            steps=steps,
            variables=data.get('variables', {})
        )

def load_workflow(path: str) -> Workflow:
    """Load workflow from YAML or JSON file."""
    path_obj = Path(path)
    with open(path_obj) as f:
        if path_obj.suffix in ['.yaml', '.yml']:
            data = yaml.safe_load(f)
        else:
            data = json.load(f)
    return Workflow.from_dict(data)

def render_step(step: WorkflowStep, max_width: int = 60) -> None:
    """Render a single workflow step with visual feedback."""
    status_symbols = {
        StepStatus.PENDING: f"{Colors.YELLOW}○{Colors.ENDC}",
        StepStatus.RUNNING: f"{Colors.CYAN}◐{Colors.ENDC}",
        StepStatus.SUCCESS: f"{Colors.GREEN}●{Colors.ENDC}",
        StepStatus.FAILED: f"{Colors.RED}✖{Colors.ENDC}",
        StepStatus.SKIPPED: f"{Colors.YELLOW}⊘{Colors.ENDC}",
    }
    
    status_colors = {
        StepStatus.PENDING: Colors.YELLOW,
        StepStatus.RUNNING: Colors.CYAN,
        StepStatus.SUCCESS: Colors.GREEN,
        StepStatus.FAILED: Colors.RED,
        StepStatus.SKIPPED: Colors.YELLOW,
    }
    
    symbol = status_symbols[step.status]
    color = status_colors[step.status]
    
    # Truncate long names
    name = step.name[:max_width - 10] + "..." if len(step.name) > max_width - 10 else step.name
    
    if step.status == StepStatus.RUNNING:
        click.echo(f"  {symbol} {color}{name}{Colors.ENDC} ", nl=False)
        click.echo(f"{Colors.CYAN}⟳{Colors.ENDC}")
    elif step.status == StepStatus.SUCCESS:
        duration_str = f"{step.duration:.2f}s"
        click.echo(f"  {symbol} {color}{name}{Colors.ENDC} {Colors.BLUE}done ({duration_str}){Colors.ENDC}")
    elif step.status == StepStatus.FAILED:
        click.echo(f"  {symbol} {color}{name}{Colors.ENDC} {Colors.RED}FAILED{Colors.ENDC}")
    elif step.status == StepStatus.SKIPPED:
        click.echo(f"  {symbol} {color}{name}{Colors.ENDC} {Colors.YELLOW}skipped{Colors.ENDC}")
    else:
        click.echo(f"  {symbol} {name}")

def render_workflow(workflow: Workflow, current_step: Optional[str] = None) -> None:
    """Render the entire workflow with all steps."""
    click.echo(f"\n{Colors.HEADER}{Colors.BOLD}▶ {workflow.name}{Colors.ENDC}")
    click.echo(f"{Colors.BLUE}{workflow.description}{Colors.ENDC}")
    click.echo(f"{Colors.BLUE}Version: {workflow.version}{Colors.ENDC}")
    
    if workflow.variables:
        click.echo(f"{Colors.CYAN}Variables:{Colors.ENDC}")
        for key, value in workflow.variables.items():
            click.echo(f"  • {key} = {value}")
    
    click.echo(f"\n{Colors.BOLD}Steps:{Colors.ENDC}")
    for step in workflow.steps:
        render_step(step)
    click.echo()

def execute_step(step: WorkflowStep) -> bool:
    """Execute a single workflow step."""
    import subprocess
    
    step.status = StepStatus.RUNNING
    start_time = time.time()
    
    try:
        # Replace variables in command (simple substitution)
        # In real usage, this would handle variable substitution
        result = subprocess.run(
            step.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        step.output = result.stdout if result.returncode == 0 else result.stderr
        step.duration = time.time() - start_time
        step.status = StepStatus.SUCCESS if result.returncode == 0 else StepStatus.FAILED
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        step.output = "Command timed out after 300 seconds"
        step.duration = time.time() - start_time
        step.status = StepStatus.FAILED
        return False
    except Exception as e:
        step.output = str(e)
        step.duration = time.time() - start_time
        step.status = StepStatus.FAILED
        return False

def render_progress_bar(current: int, total: int, width: int = 30) -> None:
    """Render a simple progress bar."""
    percent = current / total
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    click.echo(f"\r{Colors.GREEN}[{bar}]{Colors.ENDC} {int(percent * 100)}%", nl=False)

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """WorkflowWiz - No-code Visual Workflow Automation for DevOps
    
    Create, visualize, and run automated workflows with a simple YAML/JSON config.
    """
    pass

@cli.command()
@click.argument('workflow_file')
@click.option('--dry-run', is_flag=True, help='Preview workflow without executing')
def run(workflow_file: str, dry_run: bool):
    """Run a workflow from a YAML or JSON file."""
    try:
        workflow = load_workflow(workflow_file)
    except FileNotFoundError:
        click.echo(f"{Colors.RED}Error: Workflow file not found: {workflow_file}{Colors.ENDC}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Colors.RED}Error loading workflow: {e}{Colors.ENDC}", err=True)
        sys.exit(1)
    
    # Show workflow
    render_workflow(workflow)
    
    if dry_run:
        click.echo(f"{Colors.YELLOW}Dry run mode - no steps will be executed{Colors.ENDC}")
        return
    
    # Count enabled steps
    enabled_steps = [s for s in workflow.steps if s.enabled]
    total_steps = len(enabled_steps)
    current_step = 0
    failed = False
    
    click.echo(f"{Colors.BOLD}Executing workflow...{Colors.ENDC}\n")
    
    for step in workflow.steps:
        if not step.enabled:
            step.status = StepStatus.SKIPPED
            render_step(step)
            continue
        
        # Re-render workflow to show current state
        render_workflow(workflow, step.id)
        
        # Execute step
        success = execute_step(step)
        
        # Re-render to show result
        click.clear()
        render_workflow(workflow)
        
        if not success:
            failed = True
            click.echo(f"\n{Colors.RED}{Colors.BOLD}Workflow FAILED at step: {step.name}{Colors.ENDC}")
            click.echo(f"{Colors.RED}Output: {step.output[:200]}{Colors.ENDC}")
            break
        
        current_step += 1
        render_progress_bar(current_step, total_steps)
    
    click.echo()  # New line after progress
    
    if failed:
        click.echo(f"\n{Colors.RED}{Colors.BOLD}✖ Workflow FAILED{Colors.ENDC}", err=True)
        sys.exit(1)
    else:
        click.echo(f"\n{Colors.GREEN}{Colors.BOLD}✔ Workflow COMPLETED successfully{Colors.ENDC}")

@cli.command()
@click.argument('name')
@click.option('--description', default='A new workflow', help='Workflow description')
@click.option('--output', '-o', default='workflow.yaml', help='Output file')
def init(name: str, description: str, output: str):
    """Initialize a new workflow from template."""
    template = {
        'name': name,
        'description': description,
        'version': '1.0.0',
        'variables': {
            'ENV': 'production',
            'REGION': 'us-west-2'
        },
        'steps': [
            {
                'id': 'step_1',
                'name': 'Check prerequisites',
                'command': 'echo "Checking prerequisites..."',
                'enabled': True
            },
            {
                'id': 'step_2',
                'name': 'Deploy application',
                'command': 'echo "Deploying application..."',
                'enabled': True
            },
            {
                'id': 'step_3',
                'name': 'Run health check',
                'command': 'echo "Running health check..."',
                'enabled': True
            }
        ]
    }
    
    path = Path(output)
    with open(path, 'w') as f:
        if path.suffix in ['.yaml', '.yml']:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)
        else:
            json.dump(template, f, indent=2)
    
    click.echo(f"{Colors.GREEN}Created workflow: {output}{Colors.ENDC}")
    click.echo(f"Edit this file to customize your workflow.")

@cli.command()
@click.argument('workflow_file')
def visualize(workflow_file: str):
    """Visualize a workflow without executing."""
    try:
        workflow = load_workflow(workflow_file)
    except FileNotFoundError:
        click.echo(f"{Colors.RED}Error: Workflow file not found: {workflow_file}{Colors.ENDC}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Colors.RED}Error loading workflow: {e}{Colors.ENDC}", err=True)
        sys.exit(1)
    
    render_workflow(workflow)

@cli.command()
def templates():
    """List available workflow templates."""
    click.echo(f"{Colors.HEADER}{Colors.BOLD}WorkflowWiz Templates{Colors.ENDC}\n")
    
    templates_list = [
        {
            'name': 'Docker Deploy',
            'description': 'Build and deploy Docker container',
            'steps': 4
        },
        {
            'name': 'Kubernetes Rollout',
            'description': 'Deploy to Kubernetes with rollback',
            'steps': 5
        },
        {
            'name': 'CI/CD Pipeline',
            'description': 'Full CI/CD pipeline',
            'steps': 6
        },
        {
            'name': 'Database Migration',
            'description': 'Run database migrations safely',
            'steps': 3
        },
        {
            'name': 'Server Health Check',
            'description': 'Comprehensive server health check',
            'steps': 5
        }
    ]
    
    for i, t in enumerate(templates_list, 1):
        click.echo(f"{Colors.CYAN}{i}. {t['name']}{Colors.ENDC}")
        click.echo(f"   {t['description']}")
        click.echo(f"   {Colors.BLUE}Steps: {t['steps']}{Colors.ENDC}\n")

if __name__ == '__main__':
    cli()
