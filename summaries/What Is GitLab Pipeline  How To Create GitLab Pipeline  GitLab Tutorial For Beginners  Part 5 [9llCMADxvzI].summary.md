# Summary: What Is a GitLab Pipeline? (GitLab Tutorial Part 5)

- **Source video**: What Is GitLab Pipeline? | How To Create GitLab Pipeline | GitLab Tutorial For Beginners | Part 5 (`9llCMADxvzI`)
- **Approx. length**: ~37:00
- **Topic**: Building a GitLab CI/CD pipeline for a Maven project with `.gitlab-ci.yml`
- **Audience / level**: Beginners to CI/CD who already know basic GitLab

## One-line takeaway
A practical build-it-live walkthrough of a GitLab CI/CD pipeline, covering stages, jobs, runners, caching, artifacts, and deployment for a sample Maven app.

## Table of contents
| Time | Section |
|------|---------|
| 00:00 | Intro and learning objectives |
| 01:12 | CI/CD terminology: pipeline, jobs, stages, runners |
| 02:11 | The sample Maven code base |
| 04:17 | Creating `.gitlab-ci.yml` via the pipeline editor |
| 05:57 | The default template: stages, jobs, validation |
| 08:48 | Editor benefits: validate, visualize, lint, merged YAML |
| 10:21 | `only`/`except` and `when` keywords |
| 12:54 | Editing the template for Maven |
| 13:45 | Specifying a Docker `image` |
| 15:08 | Defining pipeline `variables` |
| 17:24 | `cache` for Maven dependencies |
| 18:18 | Build, unit test, and JUnit `artifacts` |
| 21:20 | Deploy job and `environment` |
| 23:16 | Committing and running the pipeline |
| 24:41 | Inspecting job console output |
| 30:46 | Test reports, artifacts, deployments |
| 32:49 | CI/CD settings: runners, masked variables, triggers, schedules |

## Sections
### Concepts and setup (00:00–04:17)
- Defines pipeline (top-level CI/CD process), jobs (steps), stages (order), and runners (agents that execute jobs; shared runners are GitLab-hosted).
- Introduces a minimal Maven project (a `hello world` app plus one JUnit test).

### Writing the pipeline (04:17–23:16)
- Uses the pipeline editor (live validation, visualize/lint/merged-YAML tabs).
- Adds a Maven Docker `image`, `variables` (`MAVEN_CLI_OPTS`, `MAVEN_OPTS` using the predefined `CI_PROJECT_DIR`), and a `cache` on `.m2/repository`.
- Build/unit-test/lint/deploy jobs across build → test → deploy stages; unit test emits JUnit `artifacts`; deploy sets a `staging` environment.

### Running and configuring (23:16–end)
- Commits trigger the run; walks the console output showing image pull, cache miss on first run, dependency downloads, test results, and artifact upload.
- Shows JUnit test rendering, artifact download, the deployment entry, and settings for custom config path, timeouts, Auto DevOps, self-hosted runners, protected/masked variables, pipeline triggers, and schedules.

## Key takeaways
- A pipeline is defined in `.gitlab-ci.yml`; jobs in the same stage run in parallel.
- Caching dependencies (`.m2/repository`) speeds up later runs.
- Artifacts persist outputs (e.g. JUnit reports) beyond the job for download and UI rendering.
- Masked/protected variables keep secrets like passwords out of logs.

## Strengths
- Built from scratch step by step, so you see cause and effect for each keyword.
- Explains not just *how* but *why* (caching, artifacts, `when: on_success` defaults).
- Good tour of the surrounding UI: editor validation, job logs, environments, settings.

## Weaknesses
- Maven/Java specific; other stacks are only mentioned via templates.
- "Deploy" only runs the app locally, not a real remote deployment.
- Assumes Part 1–4 knowledge of GitLab; no recap of the GitLab flow.
- Ends with a product/blog promo rather than next steps.

## Who should watch
Developers who know Git/GitLab basics and want a concrete first CI/CD pipeline. Some familiarity with YAML and a build tool (Maven here) helps.
