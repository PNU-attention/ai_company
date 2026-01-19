"""CLI interface for AI Company."""

import asyncio
import json
from typing import Optional

import click

from src.main import (
    get_pending_interrupts,
    resume_with_response,
    run_company,
    setup_mcp_tools,
)


@click.group()
def cli():
    """AI Company CLI - Run your AI-powered company."""
    pass


@cli.command()
@click.option("--goal", "-g", required=True, help="Company goal/objective")
@click.option("--kpi", "-k", multiple=True, help="KPIs (can specify multiple)")
@click.option("--constraint", "-c", multiple=True, help="Constraints (can specify multiple)")
@click.option("--context", help="Additional context")
@click.option("--budget", "-b", help="Budget constraints")
@click.option("--timeline", "-t", help="Expected timeline")
@click.option("--thread-id", default="default", help="Session thread ID")
def run(
    goal: str,
    kpi: tuple,
    constraint: tuple,
    context: Optional[str],
    budget: Optional[str],
    timeline: Optional[str],
    thread_id: str
):
    """Start the AI Company with a goal."""
    click.echo(f"Starting AI Company with goal: {goal}")
    click.echo("-" * 50)

    result = asyncio.run(run_company(
        goal=goal,
        kpis=list(kpi) if kpi else None,
        constraints=list(constraint) if constraint else None,
        context=context,
        budget=budget,
        timeline=timeline,
        thread_id=thread_id
    ))

    click.echo(f"\nPhase: {result.get('current_phase')}")
    click.echo(f"Projects created: {len(result.get('projects', {}))}")
    click.echo(f"Tasks created: {len(result.get('tasks', {}))}")
    click.echo(f"Agents created: {len(result.get('agents', {}))}")

    # Check for interrupts
    if result.get('pending_interrupts'):
        click.echo("\n" + "=" * 50)
        click.echo("ACTION REQUIRED:")
        for interrupt in result['pending_interrupts']:
            click.echo(f"\nType: {interrupt.get('interrupt_type')}")
            click.echo(f"From: {interrupt.get('from_agent')}")
            click.echo(f"Message: {interrupt.get('message')}")

            if interrupt.get('required_inputs'):
                click.echo("\nRequired Inputs:")
                for inp in interrupt['required_inputs']:
                    click.echo(f"  - {inp.get('key')}: {inp.get('description', inp.get('label'))}")


@cli.command()
@click.option("--thread-id", default="default", help="Session thread ID")
def status(thread_id: str):
    """Check current status and pending interrupts."""
    interrupt = get_pending_interrupts(thread_id)

    if interrupt:
        click.echo("Pending Interrupt:")
        click.echo(f"  Type: {interrupt.get('type')}")
        click.echo(f"  From: {interrupt.get('from_agent')}")
        click.echo(f"  Message: {interrupt.get('message')}")

        if interrupt.get('inputs_needed'):
            click.echo("\n  Required Inputs:")
            for inp in interrupt['inputs_needed']:
                click.echo(f"    - {inp['name']}: {inp.get('description', '')}")

        if interrupt.get('options'):
            click.echo(f"\n  Options: {', '.join(interrupt['options'])}")
    else:
        click.echo("No pending interrupts.")


@cli.command()
@click.option("--interrupt-id", "-i", required=True, help="Interrupt ID to respond to")
@click.option("--approve/--reject", default=None, help="Approve or reject")
@click.option("--input", "-n", multiple=True, help="Input values as key=value")
@click.option("--message", "-m", help="Optional message")
@click.option("--thread-id", default="default", help="Session thread ID")
def respond(
    interrupt_id: str,
    approve: Optional[bool],
    input: tuple,
    message: Optional[str],
    thread_id: str
):
    """Respond to a pending interrupt."""
    # Parse inputs
    inputs = {}
    for inp in input:
        if "=" in inp:
            key, value = inp.split("=", 1)
            inputs[key] = value

    click.echo(f"Responding to interrupt: {interrupt_id}")

    result = asyncio.run(resume_with_response(
        interrupt_id=interrupt_id,
        approved=approve,
        inputs=inputs if inputs else None,
        message=message,
        thread_id=thread_id
    ))

    click.echo(f"\nPhase: {result.get('current_phase')}")
    click.echo(f"Execution continued: {result.get('should_continue', False)}")


@cli.command()
def setup_tools():
    """Setup and connect MCP tools."""
    click.echo("Setting up MCP tools...")

    result = asyncio.run(setup_mcp_tools())

    click.echo(f"\nTotal available tools: {result['total_tools']}")
    click.echo("\nServer Status:")
    for server, status in result['servers'].items():
        if status['connected']:
            click.echo(f"  {server}: Connected ({status['tools']} tools)")
        else:
            error = status.get('error', 'Unknown error')
            click.echo(f"  {server}: Not connected - {error}")


@cli.command()
@click.option("--thread-id", default="default", help="Session thread ID")
@click.option("--format", "-f", type=click.Choice(["json", "summary"]), default="summary")
def export(thread_id: str, format: str):
    """Export current state."""
    from src.graph.company_graph import create_company_graph
    from src.context.checkpointer import create_checkpointer

    checkpointer = create_checkpointer()
    graph = create_company_graph(checkpointer=checkpointer)
    state = graph.get_state(thread_id)

    if not state:
        click.echo("No state found for this thread.")
        return

    if format == "json":
        click.echo(json.dumps(state.model_dump(), indent=2, default=str, ensure_ascii=False))
    else:
        click.echo("=" * 50)
        click.echo("AI Company State Summary")
        click.echo("=" * 50)
        click.echo(f"\nPhase: {state.current_phase}")
        click.echo(f"\nGoal: {state.ceo_request.goal if state.ceo_request else 'N/A'}")

        click.echo(f"\nAgents ({len(state.agents)}):")
        for agent in state.agents.values():
            click.echo(f"  - {agent.role_name} ({agent.status.value})")

        click.echo(f"\nProjects ({len(state.projects)}):")
        for project in state.projects.values():
            click.echo(f"  - {project.name} ({project.status.value})")

        click.echo(f"\nTasks ({len(state.tasks)}):")
        for task in state.tasks.values():
            click.echo(f"  - {task.name} ({task.status.value})")


if __name__ == "__main__":
    cli()
