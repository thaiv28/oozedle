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

`.github/workflows/publish.yml` (to be added with the site): check (ruff, pytest), sync and build, then on `main` deploy to `s3://$DEPLOYMENT_BUCKET/current/`, invalidate CloudFront and health-check.

## Old site

The site used to be on GitHub Pages at `thaiv28.github.io/oozedle` (workflow `static.yml`, daily cron, disabled by GitHub on 2026-04-07 after 60 days without commits). It is being retired behind a redirect to oozedle.thaiv.dev.
