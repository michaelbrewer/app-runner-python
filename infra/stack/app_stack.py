import os
from constructs import Construct
from aws_cdk import Stack
import aws_cdk.aws_apprunner_alpha as apprunner
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy
from aws_cdk.aws_apprunner import CfnObservabilityConfiguration, CfnService
from aws_cdk import aws_dynamodb


class AppRunnerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        table = aws_dynamodb.Table(
            self,
            "AppRunnerTable",
            table_name="app-runner-python-table",
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=aws_dynamodb.Attribute(name="pk", type=aws_dynamodb.AttributeType.STRING),
        )

        # apprunner.Service(
        #     self,
        #     "AppRunnerPythonDemo",
        #     source=apprunner.Source.from_git_hub(
        #         repository_url="https://github.com/michaelbrewer/app-runner-python",
        #         branch="main",
        #         configuration_source=apprunner.ConfigurationSourceType.REPOSITORY,
        #         connection=apprunner.GitHubConnection.from_connection_arn(os.environ["GITHUB_ARN"]),
        #     ),
        # )

        instance_role = Role(
            self,
            "AppRunnerKotlinRole",
            assumed_by=ServicePrincipal("tasks.apprunner.amazonaws.com"),
            managed_policies=[ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")],
        )
        table.grant_read_data(instance_role)
        observability_configuration = CfnObservabilityConfiguration(
            self,
            "AppRunnerObservability",
            observability_configuration_name="AppRunnerObservability",
            trace_configuration=CfnObservabilityConfiguration.TraceConfigurationProperty(vendor="AWSXRAY"),
        )
        CfnService(
            self,
            "AppRunnerPythonDemo",
            source_configuration=CfnService.SourceConfigurationProperty(
                authentication_configuration=CfnService.AuthenticationConfigurationProperty(
                    connection_arn=os.environ["GITHUB_ARN"]
                ),
                code_repository=CfnService.CodeRepositoryProperty(
                    code_configuration=CfnService.CodeConfigurationProperty(
                        configuration_source="API",
                        code_configuration_values=CfnService.CodeConfigurationValuesProperty(
                            runtime="PYTHON_3",
                            build_command="pip install -r requirements.txt && opentelemetry-bootstrap --action=install",
                            start_command="opentelemetry-instrument python app.py",
                            port="8080",
                            runtime_environment_variables=[
                                CfnService.KeyValuePairProperty(name="OTEL_PROPAGATORS", value="xray"),
                                CfnService.KeyValuePairProperty(name="OTEL_PYTHON_ID_GENERATOR", value="xray"),
                                CfnService.KeyValuePairProperty(name="OTEL_PYTHON_DISABLED_INSTRUMENTATIONS", value="urllib3"),
                                CfnService.KeyValuePairProperty(name="OTEL_RESOURCE_ATTRIBUTES", value="'service.name=app_runner_python'"),
                                CfnService.KeyValuePairProperty(name="TABLE_NAME", value=table.table_name),
                            ],
                        ),
                    ),
                    repository_url="https://github.com/michaelbrewer/app-runner-python",
                    source_code_version=CfnService.SourceCodeVersionProperty(type="BRANCH", value="main"),
                ),
                auto_deployments_enabled=True,
            ),
            instance_configuration=CfnService.InstanceConfigurationProperty(instance_role_arn=instance_role.role_arn),
            network_configuration=CfnService.NetworkConfigurationProperty(
                egress_configuration=CfnService.EgressConfigurationProperty(egress_type="DEFAULT")
            ),
            service_name="PythonService",
            observability_configuration=CfnService.ServiceObservabilityConfigurationProperty(
                observability_configuration_arn=observability_configuration.attr_observability_configuration_arn,
                observability_enabled=True,
            ),
        )
