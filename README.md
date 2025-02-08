# Get Git 🚀

> *"Managing GitHub repositories used to be as tedious as untangling a box of old Christmas lights. We were done with the endless manual clicks and misadventures on GitHub's clunky web interface. So, we built this tool to transform chaos into code-driven clarity!"*

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Contributing](#contributing)

---

## Introduction

Once upon a time in the wild world of GitHub, developers were plagued by the monotonous task of managing repositories manually. Deleting an old repo, transferring one to a new account, or even checking for duplicates was a journey fraught with frustration and errors. 😩

In a quest to reclaim lost time and sanity, the **Get Git** was born. This command-line wizard automates the mundane and brings a touch of magic to repository management. With asynchronous powers, interactive prompts, and colorful console outputs courtesy of the `rich` library, say goodbye to manual drudgery and hello to a streamlined workflow! 🎉

---

## Features

The Get Git is packed with superpowers to handle your repository woes:

- **View Repositories**  
  Quickly fetch and filter your repositories (all, owned, or collaborated) and display them in vibrant tables. 🌈

- **Delete or Leave Repositories**  
  As the repository owner, you can delete with a single confirmation. As a collaborator, you can gracefully leave a repository. 🚪

- **Transfer Repositories**  
  Seamlessly transfer a repository to another account. Clone, push, and optionally clean up the old repository—all automated! 🔄

- **Detect & Delete Duplicate Repositories**  
  Compare your repositories with those in another account and remove duplicates (with exclusions if needed). ✂️

- **Account Statistics**  
  Get an at-a-glance view of your GitHub stats: total repositories, stars, forks, and more, presented in a beautifully styled panel. 📊

---

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management. Follow these steps to set up your GitHub Assistant:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/nik1t7n/get-git.git
   cd get-git
   ```

2. **Install Poetry (if you haven't already):**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install the Project Dependencies:**
   ```bash
   poetry install
   ```

4. **Activate the Virtual Environment:**
   ```bash
   poetry shell
   ```

---

## Usage

Getting started is a breeze! Simply run the assistant with:

```bash
poetry run python main.py
```

You will be greeted with a colorful, interactive menu that guides you through the following options:

1. **View Repositories**  
   Filter by all, owned, or collaborated repositories and inspect them in a neat table.

2. **Delete/Leave a Repository**  
   Choose a repository to either delete (if you're the owner) or leave (if you're a collaborator).

3. **Transfer a Repository**  
   Migrate your repository to a new account with a few confirmations—Git magic included!

4. **Delete Duplicate Repositories**  
   Compare with another account and remove duplicate repositories, excluding those you wish to keep.

5. **Account Statistics**  
   Get a summary of your GitHub stats wrapped in an attractive panel.

6. **Exit**  
   Leave the assistant with a smile.

*Example session:*

```plaintext
[bold blue]Welcome to the GitHub Assistant[/bold blue]
Enter your GitHub username: johndoe
Enter your GitHub token: *************

Menu:
1. View repositories
2. Delete repository / Leave repository
3. Transfer repository
4. Delete duplicate repositories (compare with another account)
5. Account statistics
6. Exit
Choose an action: 1
```

---

## How It Works

Under the hood, the Get Git employs a combination of modern Python technologies:

- **Asynchronous Magic:**  
  Using `asyncio` and `httpx`, all network operations are performed asynchronously to keep the tool lightning-fast and responsive. ⚡

- **Interactive CLI with Rich:**  
  The `rich` library turns ordinary terminal output into a work of art with tables, panels, and colorful prompts.

- **GitHub API Integration:**  
  The assistant communicates directly with GitHub’s API to fetch repositories, manage collaborations, and handle transfers securely.

- **Repository Transfer Process:**  
  It automates a multi-step process: cloning the repo in mirror mode, updating remotes, pushing to a new account, and cleaning up locally—making migrations almost magical!

- **Safety First:**  
  Every destructive action (like deletion) is gated behind a confirmation prompt, so you never accidentally lose your precious code. 🛡️

---

## Configuration

To make full use of the GitHub Assistant, you’ll need:

- **A GitHub Username:**  
  Your unique GitHub identity.

- **A GitHub Personal Access Token:**  
  This token must have the necessary permissions (such as `repo`, `delete_repo`, etc.). Learn how to generate one in the [GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

Make sure you keep your token secure—this tool prompts you for it at runtime so it never needs to be stored in plain text!

---

## Troubleshooting & FAQ

**Q: I receive an error when fetching repositories. What now?**  
**A:** Double-check that your personal access token has the correct permissions and that your internet connection is stable. Also, verify GitHub's API status if issues persist.

**Q: The transfer process fails during cloning or pushing.**  
**A:** Ensure Git is installed and available on your system's PATH. Also, confirm that your credentials for both accounts are correct.

**Q: I accidentally started an action. Can I cancel?**  
**A:** Yes! Every critical action requires a confirmation prompt, so you can safely cancel by responding "no" when asked.

For any other issues, please open an issue on the GitHub repository. We love bug reports almost as much as we love new features! 🐞

---

## Contributing

We welcome contributions to make the Get Git even more awesome! To contribute:

1. **Fork the Repository**
2. **Create a New Branch:**  
   ```bash
   git checkout -b feature/your-amazing-feature
   ```
3. **Commit Your Changes:**  
   ```bash
   git commit -m "Add an amazing new feature"
   ```
4. **Push to Your Branch:**  
   ```bash
   git push origin feature/your-amazing-feature
   ```
5. **Open a Pull Request**

Please ensure your contributions adhere to the project’s style and include tests where applicable.
