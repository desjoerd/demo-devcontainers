# Onboarding Demo - .NET 10 + Aspire

A Blazor frontend, weather API, and Redis cache, based on the
[Aspire starter](https://aspire.dev/get-started/first-app/).

## 1. Install the tools

| Tool | Purpose |
| --- | --- |
| [Git 2.36+](https://git-scm.com/downloads) | Clone the repo and use the stacked PR extension |
| [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0) | Build and run the application |
| [Docker Desktop or Docker Engine](https://docs.docker.com/get-docker/) | Run Redis; start the engine with Linux containers |
| [Visual Studio Code](https://code.visualstudio.com/) | Editor; install **C# Dev Kit** and **Aspire** extensions |
| [GitHub CLI 2.0+](https://cli.github.com/manual/installation) | GitHub authentication and stacked pull requests |
| [Node.js 22 or 24 and npm](https://nodejs.org/en/download) | Playwright browser tests |
| [Python 3.11+](https://www.python.org/downloads/) | API checker |

Node, Python, and GitHub CLI are not required to run the application itself.
They are needed for browser tests, the API checker, and the stacked PR CLI
workflow respectively.
The Aspire workload, standalone Aspire CLI, and a separate Redis installation
are not required.

Using Podman instead of Docker? Start Podman and set
`ASPIRE_CONTAINER_RUNTIME=podman` in your development terminal: use
`export ASPIRE_CONTAINER_RUNTIME=podman` in Bash/Zsh or
`$env:ASPIRE_CONTAINER_RUNTIME = "podman"` in PowerShell.
For WSL, install the tools in the same distribution as the repository and
enable your container engine's WSL integration.

## 2. Configure your environment

Clone the repository and open its root in VS Code. For stacked pull requests,
authenticate GitHub CLI and install its extension:

```shell
gh auth login
gh extension install github/gh-stack
gh stack --help
```

The extension uses `gh stack submit` to create or update stacked PRs.

Check that the tools you installed are available. From the repository root,
`dotnet --version` must select a **10.0.x** SDK:

```shell
git --version
dotnet --version
docker info
gh --version
node --version
npm --version
python3 --version
```

Use `podman info` instead of `docker info` if using Podman. On Windows, use
`py -3 --version` instead of `python3 --version`.

Trust the local HTTPS certificate, then restore and build:

```shell
dotnet dev-certs https --trust
dotnet restore OnboardingDemo.sln
dotnet build OnboardingDemo.sln --no-restore
```

For browser tests, also install the npm packages and Playwright's Chromium:

```shell
npm ci
npx playwright install chromium
```

On Linux, if Chromium reports missing system libraries, run
`npx playwright install-deps chromium` or ask your administrator to install them.
First-time restore and image/browser downloads require internet access.

## 3. Run the application

Make sure your container engine is running:

```shell
dotnet run --project OnboardingDemo.AppHost --launch-profile https
```

Open the complete dashboard URL printed in the terminal; it contains a login
token, so don't share it. Wait for `cache`, `apiservice`, and `webfrontend` to
become healthy, then open the frontend from the dashboard and visit **Counter**
and **Weather**.

If HTTPS trust is not configured, use `--launch-profile http` for local
development instead. Stop the AppHost with **Ctrl+C**.

## 4. Run the checks

To check the API with Python, start the AppHost using the **HTTP profile** and
leave it running. In another terminal:

```shell
python3 scripts/check_forecast.py --api-url http://localhost:5331
python3 -m unittest discover -s scripts -p "test_*.py"
```

On Windows, replace `python3` with `py -3`.

Stop the AppHost before running the integration and browser tests:

```shell
dotnet test OnboardingDemo.sln --no-restore
npm run test:e2e
```

Both tests start their own application resources and require a working container
engine. Playwright also starts and stops its own AppHost.
