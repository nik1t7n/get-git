import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from github import GitHubAssistant


async def main():
    console = Console()
    console.print("[bold blue]Welcome to the GitHub Assistant[/bold blue]")
    username = Prompt.ask("Enter your GitHub username")
    token = Prompt.ask("Enter your GitHub token", password=True)

    assistant = GitHubAssistant(username=username, token=token)

    while True:
        console.print("\n[bold]Menu:[/bold]")
        console.print("1. View repositories")
        console.print("2. Delete repository / Leave repository")
        console.print("3. Transfer repository")
        console.print("4. Delete duplicate repositories (compare with another account)")
        console.print("5. Account statistics")
        console.print("6. Exit")
        choice = Prompt.ask("Choose an action", choices=["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            # Select filter for viewing repositories
            console.print("\n[bold]Repository viewing options:[/bold]")
            console.print("1. All repositories (owned and collaborated)")
            console.print("2. Only owned repositories")
            console.print("3. Only collaborated repositories")
            filter_choice = Prompt.ask("Choose an option", choices=["1", "2", "3"])
            if filter_choice == "1":
                repo_filter = "all"
            elif filter_choice == "2":
                repo_filter = "owner"
            elif filter_choice == "3":
                repo_filter = "collaborator"
            repos = await assistant.get_repositories(repo_filter)
            if not repos:
                console.print("[yellow]No repositories found.[/yellow]")
            else:
                table = Table(title="Your Repositories", show_lines=True)
                table.add_column("Index", style="cyan", justify="right")
                table.add_column("Name", style="green")
                table.add_column("Visibility", style="magenta")
                table.add_column("Type", style="yellow")
                table.add_column("URL", style="blue", overflow="fold")
                for idx, repo in enumerate(repos, start=1):
                    table.add_row(
                        str(idx),
                        repo["name"],
                        repo["visibility"],
                        repo["repo_type"],
                        repo["html_url"],
                    )
                console.print(table)

        elif choice == "2":
            # Delete (if owner) or leave (if collaborator)
            repos = await assistant.get_repositories("all")
            if not repos:
                console.print("[yellow]No repositories found.[/yellow]")
                continue
            table = Table(title="Select a repository to delete/leave", show_lines=True)
            table.add_column("Index", style="cyan", justify="right")
            table.add_column("Name", style="green")
            table.add_column("Visibility", style="magenta")
            table.add_column("Type", style="yellow")
            table.add_column("URL", style="blue", overflow="fold")
            for idx, repo in enumerate(repos, start=1):
                table.add_row(
                    str(idx),
                    repo["name"],
                    repo["visibility"],
                    repo["repo_type"],
                    repo["html_url"],
                )
            console.print(table)
            repo_index = Prompt.ask("Enter the index of the repository to delete/leave")
            try:
                repo_index_int = int(repo_index) - 1
                selected_repo = repos[repo_index_int]
            except (IndexError, ValueError):
                console.print("[red]Invalid index selected.[/red]")
                continue
            if selected_repo["repo_type"] == "owner":
                # If you are the owner – delete the repository
                await assistant.delete_repository(selected_repo["name"])
            else:
                # If you are a collaborator – offer to leave the repository
                await assistant.leave_repository(selected_repo)

        elif choice == "3":
            # Transfer repository – list only owned repositories
            repos = await assistant.get_repositories("owner")
            if not repos:
                console.print("[yellow]No owned repositories found.[/yellow]")
                continue
            table = Table(title="Select a repository to transfer", show_lines=True)
            table.add_column("Index", style="cyan", justify="right")
            table.add_column("Name", style="green")
            table.add_column("Visibility", style="magenta")
            table.add_column("URL", style="blue", overflow="fold")
            for idx, repo in enumerate(repos, start=1):
                table.add_row(
                    str(idx), repo["name"], repo["visibility"], repo["html_url"]
                )
            console.print(table)
            repo_index = Prompt.ask("Enter the index of the repository to transfer")
            try:
                repo_index_int = int(repo_index) - 1
                selected_repo = repos[repo_index_int]
            except (IndexError, ValueError):
                console.print("[red]Invalid index selected.[/red]")
                continue
            new_owner = Prompt.ask("Enter the new account's username")
            new_token = Prompt.ask("Enter the new account's token", password=True)
            delete_old_str = Prompt.ask(
                "Delete repository from the old account after transfer? (yes/no)",
                choices=["yes", "no"],
                default="no",
            )
            delete_old = delete_old_str.lower() == "yes"
            await assistant.transfer_repository(
                selected_repo["name"], new_owner, new_token, delete_old
            )

        elif choice == "4":
            # Delete duplicate repositories (compare with another account)
            other_username = Prompt.ask("Enter the other account's username")
            other_token = Prompt.ask("Enter the other account's token", password=True)
            exclude_input = Prompt.ask(
                "Enter repository names to exclude (separated by spaces)", default=""
            )
            exclude_list = exclude_input.split() if exclude_input.strip() else []
            await assistant.delete_duplicate_repos(
                other_username, other_token, exclude_list
            )

        elif choice == "5":
            # Account statistics
            stats = await assistant.get_account_statistics()
            if stats:
                stats_table = Table(title="Account Statistics", show_lines=True)
                stats_table.add_column("Statistic", style="cyan", justify="right")
                stats_table.add_column("Value", style="green")
                for key, value in stats.items():
                    stats_table.add_row(str(key), str(value))
                # Wrap the table in a panel for enhanced visuals
                panel = Panel(
                    stats_table,
                    title="GitHub Account Stats",
                    border_style="bright_blue",
                )
                console.print(panel)

        elif choice == "6":
            console.print("[bold green]Exiting GitHub Assistant. Goodbye![/bold green]")
            break

    await assistant.close()


if __name__ == "__main__":
    asyncio.run(main())
