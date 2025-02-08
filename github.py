import asyncio
import os
import shutil

import httpx
from rich.console import Console
from rich.prompt import Confirm


class GitHubAssistant:
    """
    An asynchronous GitHub assistant for managing repositories.

    Features:
      - Fetch repository list with filtering options:
          • All repositories (owned and collaborated)
          • Only owned repositories
          • Only collaborated repositories (where you are not the owner)
      - Delete repository (if you are the owner)
      - Leave repository (if you are a collaborator)
      - Transfer repository to another account (with optional deletion from the old account)
      - Delete duplicate repositories (with exclusion support)
      - Fetch account statistics (basic user info and repository summary)
    """

    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token
        self.base_url = "https://api.github.com"
        self.console = Console()
        # Create a shared asynchronous HTTP client with authorization headers
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_repositories(self, repo_filter: str = "owner") -> list:
        """
        Fetch a list of repositories for the current account with optional filtering.

        Parameter repo_filter:
          - "all"         — all repositories (owned and collaborated)
          - "owner"       — only repositories where you are the owner
          - "collaborator"— only repositories where you are a collaborator (not owner)

        Returns a list of dictionaries with keys:
            name, html_url, visibility, repo_type, owner, stargazers_count, forks_count.
        """
        url = f"{self.base_url}/user/repos?per_page=100"
        response = await self.client.get(url)
        if response.status_code != 200:
            self.console.print(
                f"[red]Error fetching repositories: {response.text}[/red]"
            )
            return []
        repos = response.json()
        result = []
        for repo in repos:
            # Determine repository type: "owner" if your login matches the repository owner,
            # otherwise consider it as "collaborator"
            repo_type = (
                "owner"
                if repo["owner"]["login"].lower() == self.username.lower()
                else "collaborator"
            )
            visibility = "Private" if repo["private"] else "Public"
            repo_info = {
                "name": repo["name"],
                "html_url": repo.get("html_url", ""),
                "visibility": visibility,
                "repo_type": repo_type,
                "owner": repo["owner"]["login"],
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
            }
            # Apply filtering based on the repo_filter parameter
            if repo_filter == "owner" and repo_type != "owner":
                continue
            elif repo_filter == "collaborator" and repo_type != "collaborator":
                continue
            result.append(repo_info)
        return result

    async def delete_repository(self, repo_name: str) -> bool:
        """
        Delete a repository where you are the owner.
        Asks for confirmation and returns True upon successful deletion.
        """
        if not Confirm.ask(
            f"Are you sure you want to delete the repository '{repo_name}'? This action is irreversible."
        ):
            self.console.print("[yellow]Deletion cancelled.[/yellow]")
            return False
        url = f"{self.base_url}/repos/{self.username}/{repo_name}"
        response = await self.client.delete(url)
        if response.status_code == 204:
            self.console.print(
                f"[green]Repository '{repo_name}' successfully deleted.[/green]"
            )
            return True
        else:
            self.console.print(
                f"[red]Error deleting repository '{repo_name}': {response.text}[/red]"
            )
            return False

    async def leave_repository(self, repo: dict) -> bool:
        """
        Leave a repository (if you are a collaborator).
        Sends a DELETE request to remove yourself from the list of collaborators.
        """
        if not Confirm.ask(
            f"Do you really want to leave the repository '{repo['name']}' (Owner: {repo['owner']})?"
        ):
            self.console.print("[yellow]Operation cancelled.[/yellow]")
            return False
        url = f"{self.base_url}/repos/{repo['owner']}/{repo['name']}/collaborators/{self.username}"
        response = await self.client.delete(url)
        if response.status_code == 204:
            self.console.print(
                f"[green]You have successfully left the repository '{repo['name']}'.[/green]"
            )
            return True
        else:
            self.console.print(
                f"[red]Error leaving repository '{repo['name']}': {response.text}[/red]"
            )
            return False

    async def transfer_repository(
        self, repo_name: str, new_owner: str, new_token: str, delete_old: bool = False
    ) -> bool:
        """
        Transfer a repository from the current account to another.

        Steps:
          1. Confirm transfer.
          2. Create repository on the new account.
          3. Clone the repository locally in mirror mode.
          4. Change the remote URL and push mirror to the new repository.
          5. Delete the local copy.
          6. Optionally delete the repository from the old account.
        """
        if not Confirm.ask(
            f"Are you sure you want to transfer the repository '{repo_name}' to account '{new_owner}'?"
        ):
            self.console.print("[yellow]Transfer cancelled.[/yellow]")
            return False

        # Create repository on the new account
        create_url = "https://api.github.com/user/repos"
        headers_new = {
            "Authorization": f"token {new_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        create_data = {"name": repo_name, "private": True}
        async with httpx.AsyncClient(headers=headers_new, timeout=30.0) as new_client:
            create_response = await new_client.post(create_url, json=create_data)
            if create_response.status_code == 201:
                self.console.print(
                    f"[green]Repository '{repo_name}' created on account '{new_owner}'.[/green]"
                )
            else:
                self.console.print(
                    f"[red]Error creating repository on the new account: {create_response.text}[/red]"
                )
                return False

        # Clone the repository using mirror clone
        self.console.print(f"[blue]Cloning repository '{repo_name}'...[/blue]")
        clone_url = f"https://{self.token}@github.com/{self.username}/{repo_name}.git"
        clone_cmd = ["git", "clone", "--mirror", clone_url]
        clone_process = await asyncio.create_subprocess_exec(
            *clone_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await clone_process.communicate()
        if clone_process.returncode != 0:
            self.console.print(
                f"[red]Error cloning repository '{repo_name}': {stderr.decode().strip()}[/red]"
            )
            return False

        repo_dir = f"{repo_name}.git"
        if not os.path.exists(repo_dir):
            self.console.print(f"[red]Local directory '{repo_dir}' not found.[/red]")
            return False

        # Push mirror to the new repository
        self.console.print(
            f"[blue]Pushing repository '{repo_name}' to the new account...[/blue]"
        )
        old_cwd = os.getcwd()
        os.chdir(repo_dir)
        new_remote_url = f"https://{new_token}@github.com/{new_owner}/{repo_name}.git"
        set_remote_cmd = ["git", "remote", "set-url", "origin", new_remote_url]
        set_remote_process = await asyncio.create_subprocess_exec(
            *set_remote_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await set_remote_process.communicate()
        if set_remote_process.returncode != 0:
            self.console.print(
                f"[red]Error setting new remote for '{repo_name}': {stderr.decode().strip()}[/red]"
            )
            os.chdir(old_cwd)
            return False

        push_cmd = ["git", "push", "--mirror", "origin"]
        push_process = await asyncio.create_subprocess_exec(
            *push_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await push_process.communicate()
        os.chdir(old_cwd)
        if push_process.returncode != 0:
            self.console.print(
                f"[red]Error pushing repository '{repo_name}' to the new account: {stderr.decode().strip()}[/red]"
            )
            return False

        # Remove the local mirror copy
        self.console.print(f"[blue]Removing local directory '{repo_dir}'...[/blue]")
        shutil.rmtree(repo_dir, ignore_errors=True)

        # Optionally delete the repository from the old account
        if delete_old:
            if Confirm.ask(f"Delete repository '{repo_name}' from the old account?"):
                deletion_result = await self.delete_repository(repo_name)
                if not deletion_result:
                    self.console.print(
                        f"[red]Failed to delete repository '{repo_name}' from the old account.[/red]"
                    )
        self.console.print(
            f"[green]Repository '{repo_name}' transferred successfully.[/green]"
        )
        return True

    async def list_duplicate_repos(self, other_username: str, other_token: str) -> dict:
        """
        Compare the current account's (owned only) repositories with another account's repositories.
        Returns a dictionary of duplicates, where the key is the repository name and the value is its visibility.
        """
        my_repos = await self.get_repositories("owner")
        headers_other = {
            "Authorization": f"token {other_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = "https://api.github.com/user/repos?per_page=100"
        async with httpx.AsyncClient(
            headers=headers_other, timeout=30.0
        ) as other_client:
            response = await other_client.get(url)
            if response.status_code != 200:
                self.console.print(
                    f"[red]Error fetching repositories for {other_username}: {response.text}[/red]"
                )
                return {}
            other_repos_data = response.json()
            other_repos = {
                repo["name"]: ("Private" if repo["private"] else "Public")
                for repo in other_repos_data
                if repo["owner"]["login"].lower() == other_username.lower()
            }
        duplicates = {
            repo["name"]: repo["visibility"]
            for repo in my_repos
            if repo["name"] in other_repos
        }
        return duplicates

    async def delete_duplicate_repos(
        self, other_username: str, other_token: str, exclude: list
    ):
        """
        Delete from your account (owned repositories only) those repositories
        that are also present in another account.
        You can provide a list of repository names to exclude.
        """
        duplicates = await self.list_duplicate_repos(other_username, other_token)
        if not duplicates:
            self.console.print("[green]No duplicate repositories found.[/green]")
            return
        repos_to_delete = {
            name: vis for name, vis in duplicates.items() if name not in exclude
        }
        if not repos_to_delete:
            self.console.print(
                "[yellow]All duplicates were excluded from deletion.[/yellow]"
            )
            return

        self.console.print(
            "[blue]The following duplicate repositories will be deleted:[/blue]"
        )
        for name, visibility in repos_to_delete.items():
            self.console.print(f" - {name} ({visibility})")
        if not Confirm.ask("Delete these repositories from your account?"):
            self.console.print("[yellow]Deletion cancelled.[/yellow]")
            return
        for repo in repos_to_delete:
            await self.delete_repository(repo)
        self.console.print("[green]Duplicate repositories deletion completed.[/green]")

    async def get_account_statistics(self) -> dict:
        """
        Fetch account statistics:
          - Basic information (login, name, public repository count, followers, following, creation date)
          - Total number of repositories (owned and collaborated)
          - Total stars and forks across all repositories
        """
        stats = {}
        # Fetch user information
        user_url = f"{self.base_url}/user"
        response = await self.client.get(user_url)
        if response.status_code == 200:
            user_info = response.json()
            stats["Login"] = user_info.get("login")
            stats["Name"] = user_info.get("name")
            stats["Public Repos"] = user_info.get("public_repos", 0)
            stats["Followers"] = user_info.get("followers", 0)
            stats["Following"] = user_info.get("following", 0)
            stats["Created At"] = user_info.get("created_at")
        else:
            self.console.print(
                f"[red]Error fetching user information: {response.text}[/red]"
            )

        # Fetch repository details
        repos_all = await self.get_repositories("all")
        stats["Total Repos"] = len(repos_all)
        stats["Owned Repos"] = len([r for r in repos_all if r["repo_type"] == "owner"])
        stats["Collaborator Repos"] = len(
            [r for r in repos_all if r["repo_type"] == "collaborator"]
        )
        total_stars = sum(r.get("stargazers_count", 0) for r in repos_all)
        total_forks = sum(r.get("forks_count", 0) for r in repos_all)
        stats["Total Stars"] = total_stars
        stats["Total Forks"] = total_forks
        return stats
