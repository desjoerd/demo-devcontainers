# Onboarding Demo - .NET 10 + Aspire

Welcome to the team! Before picking up your first ticket, follow this guide to
set up your local development environment and verify that the application works.

This is a small distributed application based on Microsoft's
[Aspire starter](https://aspire.dev/get-started/first-app/), generated with
`Aspire.ProjectTemplates` 13.6.5 and targeting **.NET 10** throughout.
It uses randomly generated weather data: no cloud subscription, API key,
database migration, or paid service is required.

## Contents

- [What you will run](#what-you-will-run)
- [1. Install Git](#1-install-git)
- [2. Install the .NET 10 SDK](#2-install-the-net-10-sdk)
- [3. Install and start a container runtime](#3-install-and-start-a-container-runtime)
- [4. Install and configure your editor](#4-install-and-configure-your-editor)
- [5. Install Node.js and npm](#5-install-nodejs-and-npm)
- [6. Install Python](#6-install-python)
- [7. Clone the repository](#7-clone-the-repository)
- [8. Configure local HTTPS](#8-configure-local-https)
- [9. Restore and build](#9-restore-and-build)
- [10. Start the application](#10-start-the-application)
- [11. Verify your environment](#11-verify-your-environment)
- [12. Run the .NET integration test](#12-run-the-net-integration-test)
- [13. Run the Python API check](#13-run-the-python-api-check)
- [14. Run the Playwright browser tests](#14-run-the-playwright-browser-tests)
- [Day-to-day development](#day-to-day-development)
- [Troubleshooting](#troubleshooting)
- [Ready for your first ticket](#ready-for-your-first-ticket)

## What you will run

```text
Browser --> Blazor frontend --> ASP.NET Core API
                                      |
                                      +--> Redis output cache (container)

Aspire AppHost: starts resources, connects services, and provides a dashboard
Playwright (Node.js/npm): verifies the UI in a real Chromium browser
Python: verifies API health and forecast data
```

| Project | Responsibility |
| --- | --- |
| [OnboardingDemo.AppHost](./OnboardingDemo.AppHost) | Orchestration, dependency order, service references, dashboard |
| [OnboardingDemo.Web](./OnboardingDemo.Web) | Blazor frontend with an interactive counter and weather page |
| [OnboardingDemo.ApiService](./OnboardingDemo.ApiService) | `/weatherforecast` API returning five random forecasts |
| [OnboardingDemo.ServiceDefaults](./OnboardingDemo.ServiceDefaults) | Shared health checks, service discovery, HTTP resilience, OpenTelemetry |
| [OnboardingDemo.Tests](./OnboardingDemo.Tests) | Integration test that starts the application, including Redis |
| [tests/browser](./tests/browser) | Playwright browser tests, installed with npm |
| [scripts](./scripts) | Python API validation and its unit tests |

The .NET processes run on your machine; Redis runs in a container. You do not
need to install Redis separately. Aspire supplies the Redis connection string
to the API and the API's address to the frontend.

The API caches `/weatherforecast` responses in Redis for five seconds. Caching
lives on the API endpoint rather than the streaming Blazor page: Blazor's
antiforgery cookies and streaming responses are not suitable for output caching.

### Prerequisite checklist

- Git on your terminal's `PATH`.
- A stable **.NET 10 SDK**, not just the runtime.
- Docker Desktop or Docker Engine, running and accessible to your user.
- Visual Studio Code and its C# tooling.
- Node.js 22 or 24 LTS with npm for the browser test suite.
- Playwright's matching Chromium browser and OS dependencies.
- Python 3.11 or newer for the API validation script.
- A browser with the local ASP.NET Core development certificate trusted.
- Internet access to NuGet and container registries for the first restore/run.
- Available local ports for the dashboard and application endpoints.

The Aspire SDK, dashboard, orchestration tooling, and client libraries are
restored through the project dependencies. **There is no Aspire workload to
install.** The standalone Aspire CLI is optional and is not needed for this guide.
A separate Redis installation and a database server are not required.

## 1. Install Git

Install [Git](https://git-scm.com/downloads) for your operating system.

- **Windows:** install Git for Windows and enable command-line access.
- **macOS:** install Git using the installer or your preferred package manager;
  Apple's command-line developer tools also provide Git.
- **Ubuntu/Debian:** install it with `sudo apt update` followed by
  `sudo apt install git`.

Open a **new terminal** after installation and verify:

```shell
git --version
```

If you intend to push changes, configure your Git author name/email and GitHub
authentication using your team's normal process. Cloning this public repository
does not require authentication.

## 2. Install the .NET 10 SDK

Download the **SDK** from the [.NET 10 download page](https://dotnet.microsoft.com/download/dotnet/10.0).
Choose the installer matching your OS and CPU architecture (Arm64 or x64).

- **Windows:** use the .NET 10 SDK installer, then restart your terminal/editor.
- **macOS:** use the matching Arm64 or x64 SDK installer.
- **Linux:** follow the distribution-specific
  [.NET installation instructions](https://learn.microsoft.com/dotnet/core/install/linux).
  Configure the appropriate package feed if required, then install
  `dotnet-sdk-10.0`. Do not mix package feeds for the same .NET installation.

Check the installed SDKs:

```shell
dotnet --list-sdks
dotnet --list-runtimes
```

You should see a `10.0.xxx` SDK and `Microsoft.NETCore.App` /
`Microsoft.AspNetCore.App` 10.0 runtimes.

The repository's [global.json](./global.json) selects a stable .NET 10 SDK,
starting at 10.0.100 and allowing newer .NET 10 feature bands and patches.
It does **not** roll forward to .NET 11 or use preview SDKs. You may keep other
SDKs installed alongside .NET 10.

## 3. Install and start a container runtime

### Windows

1. Enable hardware virtualization if it is disabled.
2. Follow the [Docker Desktop Windows installation guide](https://docs.docker.com/desktop/setup/install/windows-install/),
   including its WSL 2 requirements. Restart if requested.
3. Start Docker Desktop and select **Linux containers**, not Windows containers.
4. If you develop inside WSL, enable Docker Desktop integration for that
   distribution. Install Git and the .NET SDK inside WSL too, and run all
   repository commands there rather than mixing Windows and Linux tooling.

### macOS

1. Install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)
   for your CPU architecture.
2. Start Docker Desktop and complete its first-run setup.
3. Wait until the container engine is running.

### Linux

1. Install [Docker Engine](https://docs.docker.com/engine/install/) for your
   distribution, or Docker Desktop.
2. Start the daemon according to the installation guide.
3. Configure access for your development user. See Docker's
   [Linux post-installation instructions](https://docs.docker.com/engine/install/linux-postinstall/).
   Membership of the `docker` group grants root-equivalent privileges; use your
   organization's approved setup. Log out and back in after group changes.

### Verify the runtime from the terminal you will use for development

```shell
docker version
docker info
docker run --rm hello-world
```

For Docker, `docker version` should show both Client and Server information.
A working CLI alone is not enough: Aspire must be able to start containers.
The hello-world command also verifies registry access.

This sample uses the `docker.io/library/redis:8.2` image. Aspire pulls and starts
it automatically. The 8.2 tag allows Redis patch updates within that release
line; the first pull can take a while.

**Already using Podman?** Aspire supports it as an alternative. Verify
`podman info` and `podman run --rm docker.io/library/hello-world`, then set
`ASPIRE_CONTAINER_RUNTIME=podman` in the same terminal before running the
application or tests:

```bash
# Bash / Zsh
export ASPIRE_CONTAINER_RUNTIME=podman
```

```powershell
# PowerShell
$env:ASPIRE_CONTAINER_RUNTIME = "podman"
```

On macOS/Windows, your Podman machine must also be running. Do not install a
second engine just for this sample if your existing supported engine works.

## 4. Install and configure your editor

Install [Visual Studio Code](https://code.visualstudio.com/).
Enable its `code` shell command if you want to open the repository from a terminal.
On macOS, use **Shell Command: Install 'code' command in PATH** in the Command Palette.

Install these extensions from the Extensions view:

- **C# Dev Kit** (`ms-dotnettools.csdevkit`), including its C# extension dependency.
  Review its license terms for your organization.
- **Aspire** (`microsoft-aspire.aspire-vscode`) for Aspire editor integration.

The repository includes [extension recommendations](./.vscode/extensions.json),
but VS Code does not install these automatically.

The terminal commands below also work without editor integrations. If you use
another IDE, ensure its installed version supports .NET 10 and Aspire.

## 5. Install Node.js and npm

Install **Node.js 24 LTS** (recommended) or **22 LTS**, including npm, from
[nodejs.org](https://nodejs.org/en/download). The supported major versions are
declared in [package.json](./package.json). Node runs the Playwright test runner,
not the application itself.

- **Windows/macOS:** use the appropriate installer or your approved version manager.
- **Linux:** use the official installation guidance or your team's version
  manager. Distribution repositories may provide an older, unsupported Node.
- **WSL:** install Node inside the same distribution as .NET; do not use a
  Windows Node executable to run Linux browser tests.

Restart your terminal and check:

```shell
node --version
npm --version
```

Installing Node does **not** install Playwright's browser binaries. Those are
downloaded separately after cloning the repository.

## 6. Install Python

Install **Python 3.11 or newer** from [python.org](https://www.python.org/downloads/)
or your approved package manager.

- **Windows:** enable command-line access in the installer and verify
  `py -3 --version`. If `python` opens the Microsoft Store instead, check your
  installation and app execution aliases.
- **macOS:** install a current Python 3; do not depend on Apple's system tooling.
- **Linux:** install your distribution's `python3` package and check its version.
  For Ubuntu/Debian, use `sudo apt install python3`. Older distributions may
  need a newer supported Python installation.

On macOS/Linux, verify:

```shell
python3 --version
```

The API checker uses only the standard library, so no `pip install` or virtual
environment is required. Run it with the interpreter you verified; do not assume
the bare `python` command points to the right version.

## 7. Clone the repository

```shell
git clone https://github.com/desjoerd/demo-devcontainers.git
cd demo-devcontainers
code .
```

Only trust the workspace if you trust its contents. Allow C# Dev Kit to load
[OnboardingDemo.sln](./OnboardingDemo.sln) and complete initialization.

Run all remaining commands from the **repository root**. Check SDK selection
again here, because `global.json` only applies within the repository:

```shell
dotnet --version
dotnet --info
```

The selected SDK must be `10.0.xxx`, even if .NET 11 is also installed.

## 8. Configure local HTTPS

The default launch profile uses HTTPS for the dashboard and application.
Create/trust an ASP.NET Core development certificate:

```shell
dotnet dev-certs https --trust
dotnet dev-certs https --check --trust
```

Accept the OS trust prompt when shown. Restart your browser after changing
certificate trust.

- **Windows/macOS:** the command normally integrates with the OS trust store.
- **Linux:** browser trust stores and required system utilities vary. Follow the
  [.NET Linux certificate guidance](https://learn.microsoft.com/aspnet/core/security/enforcing-ssl#trust-https-certificate-on-linux)
  if the command reports missing dependencies or your browser still rejects
  the certificate. Some browsers require additional configuration.
- **WSL:** a certificate trusted inside Linux is not necessarily trusted by a
  Windows-hosted browser. Follow the
  [WSL HTTPS guidance](https://learn.microsoft.com/aspnet/core/security/enforcing-ssl#trust-https-certificate-from-windows-subsystem-for-linux)
  for that boundary.

Do not commit exported certificates or private keys. Do not disable TLS
validation globally to work around a trust error.

## 9. Restore and build

```shell
dotnet restore OnboardingDemo.sln
dotnet build OnboardingDemo.sln --no-restore
npm ci
npx playwright install chromium
```

`npm ci` installs the exact dependency tree in [package-lock.json](./package-lock.json).
Do not install Playwright globally or regenerate the lockfile during onboarding.
Run the browser install again after a Playwright version update; a system Chrome
installation is not a substitute for its matching Chromium build.

On Linux, Chromium also needs system libraries. If Playwright reports missing
libraries, install the dependencies on a supported distribution:

```shell
npx playwright install-deps chromium
```

This may request elevated privileges and use the OS package manager. In a
restricted environment, ask your administrator to provision those libraries
instead of running npm itself as root. See Playwright's
[system requirements](https://playwright.dev/docs/intro#system-requirements).
Windows/macOS browser prerequisites are handled by the browser installation.

Restore needs access to [NuGet](https://api.nuget.org/v3/index.json),
[npm](https://registry.npmjs.org/), and Playwright's browser download endpoints.
On a corporate network, configure your approved proxy and root certificates
for .NET and your container runtime. They do not necessarily use the same
proxy/trust configuration.

Expected result: all five projects build successfully and target `net10.0`.
Do not start services manually or write local connection strings: the AppHost
wires them together.

## 10. Start the application

Make sure your container engine is still running, then start the **AppHost**:

```shell
dotnet run --project OnboardingDemo.AppHost --launch-profile https
```

Leave that terminal open. On the first run, allow time for Aspire's tooling,
Redis image download, and resource health checks.

The console prints an Aspire dashboard URL with a login token. Open the
**complete URL printed by your process**. The HTTPS dashboard's base address
is `https://localhost:17039`; opening only that address may ask for the token.
Treat the token as a local credential rather than copying it into commits or
shared screenshots.

In the dashboard, wait for these resources to become healthy:

| Resource | What it is |
| --- | --- |
| `cache` | Redis container |
| `apiservice` | Weather API process, waiting for Redis |
| `webfrontend` | Blazor process, waiting for the API |

Open the frontend using its **dashboard endpoint link**. Do not use the
dashboard address as the application URL. Aspire manages endpoint proxying
and Redis's host port; use the displayed endpoints rather than assuming
Redis is on port 6379 on your machine.

### Local HTTP alternative

If HTTPS trust is not yet configured, you can run the local demo with the
included HTTP profile:

```shell
dotnet run --project OnboardingDemo.AppHost --launch-profile http
```

This uses HTTP endpoints for the local dashboard and projects; it does not
disable certificate validation. Open the token-bearing dashboard URL printed
in the terminal. The HTTP dashboard base address is `http://localhost:15283`.
Use this only for local development, not as a deployment configuration.

## 11. Verify your environment

1. Open `webfrontend` from the dashboard. The homepage says **Welcome to the team!**
2. Open **Counter** and increment the counter to verify interactive Blazor.
3. Open **Weather**. You should see a table containing five forecasts.
4. Refresh the weather page within five seconds to see the cached output;
   refresh after that interval to request a new random forecast.
5. Open the API endpoint from the dashboard and append `/weatherforecast`.
   It should return a JSON array with five entries, including `date`,
   `temperatureC`, `temperatureF`, and `summary`.
6. On the API, `/openapi/v1.json` exposes the development OpenAPI document.
   There is no Swagger UI bundled with this sample.
7. Inspect **Console logs**, **Structured logs**, **Traces**, and **Metrics**
   in the dashboard. Visit the weather page again to generate traffic.
   A cache hit avoids generating a new forecast inside the API.
8. Both .NET services expose `/health` and `/alive` in Development.
   The API readiness check includes its Redis connection.

There are no secrets to enter and no seed data to load. All forecasts are
generated in memory, and Redis stores disposable API responses.

## 12. Run the .NET integration test

Stop the interactive AppHost with **Ctrl+C** first, then run:

```shell
dotnet test OnboardingDemo.sln --no-restore
```

The integration test starts its own AppHost, API, frontend, and Redis container.
It checks dependency health, homepage content, the forecast JSON shape/range,
identical API responses within the cache window, the rendered weather table,
and both service health endpoints.
It does not automate browser clicks on the Counter page.

The test needs a working container runtime. Aspire's testing host manages its
own endpoints; the browser trust setup above is for interactive HTTPS use.
The test has a three-minute timeout to allow for resource startup; slow first
image pulls may require pre-pulling:

```shell
docker pull docker.io/library/redis:8.2
```

For Podman, use `podman pull docker.io/library/redis:8.2` and keep
`ASPIRE_CONTAINER_RUNTIME=podman` set in the test terminal.

## 13. Run the Python API check

Start the AppHost with the **HTTP profile** from step 10. Leave it running and
open a second terminal in the repository root.

On macOS/Linux:

```shell
python3 scripts/check_forecast.py --api-url http://localhost:5331
```

On Windows:

```powershell
py -3 scripts/check_forecast.py --api-url http://localhost:5331
```

Use the API endpoint shown in your dashboard if you changed its port. The script
checks API health, five consecutive forecast dates, temperature bounds,
Celsius/Fahrenheit consistency, and non-empty summaries. It prints a clear
result and exits nonzero on connection errors or invalid data.

The default API URL is the HTTP profile's `http://localhost:5331`. For an HTTPS
URL, Python must also trust the development certificate; Python and your
browser may use different trust stores. Do not disable TLS validation.

The validator also has fast unit tests that need no running app or containers:

```shell
python3 -m unittest discover -s scripts -p "test_*.py"
```

On Windows, replace `python3` with `py -3`. These tests cover valid data and
invalid shapes, missing/invalid fields, temperatures, and nonconsecutive dates.

Stop the interactive AppHost before continuing to the browser suite.

## 14. Run the Playwright browser tests

With the container engine running and **no interactive AppHost running**, use:

```shell
npm run test:e2e
```

[playwright.config.js](./playwright.config.js) starts the AppHost using the
local HTTP profile, waits for the frontend readiness endpoint, runs Chromium
tests, and stops its server afterward. You do not need to launch the app
separately. The tests verify homepage content, two interactive counter clicks,
and navigation to a five-row weather table.

The tests deliberately refuse to reuse an already running frontend: this
prevents testing a stale application by accident. Ports 5115, 5331, 15283,
19209, and 20059 must be available. The HTTP profile avoids browser certificate
trust requirements for the automated suite.

On Podman, set `ASPIRE_CONTAINER_RUNTIME=podman` in the npm terminal as well;
Playwright passes that environment to the AppHost.

To watch the browser on a machine with a graphical desktop:

```shell
npm run test:e2e:headed
```

To inspect the HTML report after a run:

```shell
npm run test:e2e:report
```

The report command starts a local viewer; stop it with Ctrl+C when finished.
Failure traces are saved under `test-results/`; the HTML report is in
`playwright-report/`. Both are ignored by Git and can contain page contents,
so review them before sharing.

## Day-to-day development

1. Start your container engine.
2. Pull the latest repository changes.
3. Restore/build if dependencies changed; run `npm ci` after lockfile changes
   and reinstall Playwright Chromium when its version changes.
4. Start the AppHost using the command above.
5. Edit the frontend or API; use your editor's .NET debugging/Hot Reload support,
   or stop and restart the AppHost after changes.
6. Run the Python check against your running app.
7. Stop the app, then run the .NET integration and Playwright tests sequentially
   before sharing your work.

For VS Code debugging, use C# Dev Kit's Solution Explorer to start a new debug
instance of **OnboardingDemo.AppHost**, not only the Web project.

Stop the AppHost with **Ctrl+C**. Aspire stops its child processes and the
Redis container. No persistent Redis volume is configured, so cached API
responses are disposable. Downloaded images remain in your engine's image cache.
Avoid broad Docker cleanup commands on a machine shared with other projects.

## Troubleshooting

| Symptom | Checks / next steps |
| --- | --- |
| `dotnet` or `git` is not recognized | Restart the terminal/editor after installation; check `PATH` and which OS environment the terminal belongs to. |
| A compatible .NET SDK was not found | Run `dotnet --list-sdks`. Install the .NET **10 SDK** for your architecture. A runtime-only install or .NET 11 alone does not satisfy `global.json`. |
| Terminal builds, editor does not | Restart VS Code after installing the SDK; check the SDK detected by C# Dev Kit and whether you opened the correct solution. |
| Cannot connect to the Docker daemon | Start the engine; run `docker info` in the same terminal. Check the active Docker context, WSL integration, and any `DOCKER_HOST` override. |
| Linux socket permission denied | Use your approved Docker user/rootless configuration, then log out/in if groups changed. Do not run the whole editor/AppHost as root as a shortcut. |
| Podman installed but Aspire tries Docker | Set `ASPIRE_CONTAINER_RUNTIME=podman` in the terminal launching the AppHost/tests; verify the Podman machine/engine is running. |
| Image pull fails or times out | Try the explicit Redis pull above. Check registry access, proxy settings, DNS, rate limits, and available disk space. |
| NuGet restore fails | Check access to NuGet, approved feeds, proxy configuration, and corporate CA trust. Use `dotnet nuget list source` to inspect configured feeds. |
| HTTPS or certificate error | Re-run the certificate checks; follow the OS/browser-specific trust steps above. Confirm the browser and .NET processes use the intended trust stores. The local HTTP profile is available while resolving trust. |
| Dashboard asks for a token | Use the complete login URL from your current AppHost's console output. A token from an earlier run may no longer work. |
| Address already in use | Stop your previous AppHost. Inspect the owning process before stopping anything. Dashboard/telemetry ports are in the AppHost launch settings; service ports are in each service's launch settings. |
| Frontend stays waiting | Inspect `cache` and `apiservice` in the dashboard. The API waits for Redis, and the frontend waits for the API to be healthy. |
| Running only a service fails with missing configuration | Run the AppHost. It provides Redis configuration to the API and API service discovery to the frontend. |
| Weather values do not change immediately | API output is cached for five seconds. Wait for cache expiry before refreshing; generated data can occasionally repeat. |
| Traces appear empty | Generate requests, wait briefly for export, and check dashboard filters. Health-check requests are deliberately excluded from traces. |
| Integration test times out | Stop the interactive AppHost, check engine readiness and HTTPS trust, pre-pull Redis, then rerun the test. Inspect the test output for the failing resource. |
| npm reports an unsupported engine | Check `node --version` in this terminal. Use Node 22 or 24, not a stale system Node or an executable from another OS environment. |
| PowerShell blocks `npm.ps1` | Use `npm.cmd` / `npx.cmd` or follow your organization's approved PowerShell policy; do not disable execution policy globally. |
| `npm ci` fails | Check npm registry/proxy access and that the lockfile matches the manifest. Do not use `npm install` to hide a lockfile mismatch during onboarding. |
| Playwright cannot find its browser executable | Run `npx playwright install chromium` using the same OS user and environment as the tests. Browser caches are user-specific. |
| Chromium reports missing shared libraries | Run `npx playwright install-deps chromium` on a supported Linux distribution, or ask your administrator to install the reported libraries. |
| Browser tests report an existing server | Stop your interactive AppHost before `npm run test:e2e`. The suite owns its server lifecycle and refuses to reuse an existing frontend. |
| Python cannot connect | Keep the AppHost running for the Python check and pass the **API** URL, not the dashboard/frontend URL. Use HTTP if Python does not trust the local certificate. |
| `python3` / `py` is not found | Verify Python installation and PATH in the current terminal. On Windows use `py -3`; on macOS/Linux use `python3`. |

For a reproducible support report, include your OS, selected SDK version,
container engine/version, failing command, and relevant error output. Redact
tokens, credentials, and private configuration before sharing logs.

## Ready for your first ticket

- [ ] Git and the .NET 10 SDK work in the development terminal.
- [ ] The container engine can run containers as your development user.
- [ ] VS Code loads the solution and C# tooling.
- [ ] Node/npm work, `npm ci` succeeds, and Playwright Chromium is installed.
- [ ] Python 3.11+ works in the development terminal.
- [ ] Local HTTPS is trusted by .NET and your browser.
- [ ] Restore and build succeed.
- [ ] All three Aspire resources become healthy.
- [ ] Counter and Weather work in the frontend.
- [ ] The integration test passes.
- [ ] Python validator unit tests and the live API check pass.
- [ ] The Playwright browser tests pass.

Once every item is checked, your local development environment is ready.
