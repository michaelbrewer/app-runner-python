import aws_cdk as cdk

from stack.app_stack import AppRunnerStack


app = cdk.App()
stack = AppRunnerStack(app, "app-runner-python")
cdk.Tags.of(stack).add("project", "app-runner-python-demo")
app.synth()
