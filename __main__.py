import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as kubernetes

# Create an EKS cluster with the default configuration.
cluster = eks.Cluster("cluster", fargate=True)
eks_provider = kubernetes.Provider("eks-provider", kubeconfig=cluster.kubeconfig_json)
# Deploy a small canary service (NGINX), to test that the cluster is working.
my_deployment = kubernetes.apps.v1.Deployment("my-deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels={
            "appClass": "my-deployment",
        },
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        replicas=2,
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels={
                "appClass": "my-deployment",
            },
        ),
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels={
                    "appClass": "my-deployment",
                },
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[kubernetes.core.v1.ContainerArgs(
                    name="my-deployment",
                    image="nginx",
                    ports=[kubernetes.core.v1.ContainerPortArgs(
                        name="http",
                        container_port=80,
                    )],
                )],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=eks_provider))

my_service = kubernetes.core.v1.Service("my-service2",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        labels={
            "appClass": "my-deployment",
        },
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        type="ClusterIP",
        ports=[kubernetes.core.v1.ServicePortArgs(
            port=80,
            target_port="http",
        )],
        selector={
            "appClass": "my-deployment",
        },
    ),
    opts=pulumi.ResourceOptions(provider=eks_provider))

ingress = kubernetes.networking.v1.Ingress("ingress",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        annotations={
            "nginx.ingress.kubernetes.io/rewrite-target": "/",
        },
    ),
    spec=kubernetes.networking.v1.IngressSpecArgs(
        rules=[kubernetes.networking.v1.IngressRuleArgs(
            http=kubernetes.networking.v1.HTTPIngressRuleValueArgs(
                paths=[kubernetes.networking.v1.HTTPIngressPathArgs(
                    backend=kubernetes.networking.v1.IngressBackendArgs(
                        service=kubernetes.networking.v1.IngressServiceBackendArgs(
                            name=my_service.id.apply(lambda id: id.split("/")[1]),
                            port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                number=80,
                            ),
                        ),
                    ),
                    path="/",
                    path_type="Prefix",
                )],
            ),
        )],
    ))

cluster_info = aws.eks.get_cluster(name=cluster.eks_cluster.name)

# Export the cluster's kubeconfig.
pulumi.export("update-cmd",
              cluster.eks_cluster.name.apply(lambda cluster_name: f"awslocal eks update-kubeconfig --name {cluster_name} && kubectl config use-context {cluster_info.arn}")
)
# # Export the URL for the load balanced service.
pulumi.export("url", "http://localhost:8081/")
