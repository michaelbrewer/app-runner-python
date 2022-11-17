# Python App Runner Example

Simple example using CDK to bootstrap a new AppRunner project using the Python managed runtime.

## Infra deployment

```bash
cd infra
make dev
# Your forked repo
export GITHUB_URL="https://github.com/michaelbrewer/app-runner-python"
# Your Github connection arn in App Runner
export GITHUB_ARN="arn:aws:apprunner:<REGION>:<ACCOUNT_ID>:connection/personal/<UUID>"
cdk deploy
```
