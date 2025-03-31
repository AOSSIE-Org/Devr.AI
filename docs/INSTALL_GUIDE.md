# Devr.AI Installation Guide

Follow this guide to set up Devr.AI's development environment on your local machine.

## Prerequisites

-   [Python](https://www.python.org/) 3.9+ (version 3.10 is recommended)
-   [Node.js](https://nodejs.org/en) (latest LTS version)
-   [Git](https://git-scm.com/) (any recent version)

## Setup Guide

1. Clone the repository. (If you are using a fork of the repository, replace the GitHub repo url with your own)

```sh
git clone https://github.com/AOSSIE-Org/Devr.AI.git
cd Devr.AI
```

2. This project uses [poetry](https://python-poetry.org/) for package management. Install poetry with the following steps: (Skip this step if you have poetry installed)

    - On Linux / MacOS / WSL

    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

    - On Windows (powershell)

    ```powershell
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
    ```

    - Verify the installation with the command: (should say v2.0.0 or above)

    ```sh
    poetry --version
    ```

3. Install Project Dependencies. Inside the project directory (at root level), run the following commands:

```sh
poetry env use python3.10
poetry install --with dev
```

This should install all the necessary dependencies for the project.

4. To activate the virtual environment created by poetry, run the following commands:

    - On Linux / Mac / WSL

    ```sh
    eval $(poetry env activate)
    ```

    - On Windows (powershell)

    ```powershell
    Invoke-Expression (poetry env activate)
    ```

    - Verify the installation with the command: (should say v2.0.0 or above)

    ```sh
    poetry --version
    ```

    > **Note:** If the `poetry` command is not recognized, ensure that the poetry executable is added to your system's PATH environment variable.

To run this project:

```sh
cd frontend
npm install
npm start
```

> [!NOTE]
> For further information about poetry and managing environments refer to the [poetry docs](https://python-poetry.org/docs/managing-environments/).
