import os
from constructs import Construct
from aws_cdk import Stack
import aws_cdk.aws_apprunner_alpha as apprunner
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy
from aws_cdk.aws_apprunner import CfnObservabilityConfiguration, CfnService


class AppRunnerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
                        configuration_source="REPOSITORY",
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
