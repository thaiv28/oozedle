# Deployment

Oozedle is served at **https://oozedle.thaiv.dev** from AWS, through the `thaiv.dev` platform in `~/repos/project-platform-infrastructure` (AWS CDK).

## Infrastructure (owned by project-platform-infrastructure)

- Stack `ThaivOozedleProject` (`us-west-2`, deployed 2026-10-21, infra PR #23): a private, versioned S3 bucket behind CloudFront with origin path `/current`, the shared `*.thaiv.dev` certificate, Route 53 A/AAAA aliases, and `/404.html` for missing paths.
- Deploy access: the shared GitHub OIDC role from `ThaivProjectPlatform` (any `thaiv28/*` repo on `main`), granted this bucket and distribution through the managed policy `thaiv-oozedle-static-deployment`.
- Infrastructure changes go through that repo's **Deploy Oozedle Infrastructure** workflow (`diff`, then `deploy`).
- CloudFront's default root object covers `/` only, so pages are `.html` files (`players.html`, `players/<slug>.html`).

Repository settings (set 2026-10-21):

| Kind | Name | Source |
|---|---|---|
| Variable | `DEPLOYMENT_BUCKET` | `ThaivOozedleProject` output `DeploymentBucket` |
| Variable | `CLOUDFRONT_DISTRIBUTION_ID` | `ThaivOozedleProject` output `CloudFrontDistributionId` |
| Secret | `AWS_ROLE_ARN` | `ThaivProjectPlatform` output `DeploymentRoleArn` |

## Publishing

`.github/workflows/publish.yml` runs on pushes to `main`, pull requests, manual dispatch, and every six hours at minute 17. Its `check` job installs frozen dependencies and runs ruff format/check and pytest. The independent `build` job installs frozen runtime dependencies, restores cached `data/raw` (falling back to `raw-`), syncs workbooks, saves the cache only on `main`, prints the last 25 data-check lines, builds, and uploads the `site` artifact.

`deploy` needs both jobs and runs only on non-PR `main` with bucket and distribution variables set. It downloads the artifact, assumes `AWS_ROLE_ARN` in us-west-2, syncs static assets with immutable one-year caching, syncs other output to `s3://$DEPLOYMENT_BUCKET/current/`, invalidates CloudFront, and checks https://oozedle.thaiv.dev/ up to five times, ten seconds apart. Concurrency is per ref; only PR runs cancel earlier runs. Permissions are contents read, id-token write, actions write.

The scheduled `keepalive` job re-enables this workflow through `gh api` using the workflow token, preventing GitHub's inactivity shutdown after 60 days.

`pages-redirect.yml` is manual-only. It writes canonical/meta-refresh/link redirects for the index, 404 and 2024–2026 pages (years retain `?season=YYYY`), then configures Pages, uploads and deploys the redirect artifact in the `github-pages` environment. Run once after merge, then turn off Pages in repository settings.

## Old site

The site used to be on GitHub Pages at `thaiv28.github.io/oozedle` (former workflow `static.yml`, removed; its daily cron was disabled by GitHub on 2026-04-07 after 60 days without commits). It is being retired behind a redirect to oozedle.thaiv.dev.
