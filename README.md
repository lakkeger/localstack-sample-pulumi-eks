# Pulumi EKS Fargate on Localstack

Small sample code to run a Localstack provisioned "EKS Fargate" cluster (k3d)

## Requirements
- Pulumi
- Localstack Pro

## Instructions

### To create from scratch
0. (Optional) Set Pulumi for local backend
```
export PULUMI_BACKEND_URL=file://`pwd`
export PULUMI_CONFIG_PASSPHRASE=lsdevtest
```
1. Create project dir
```
mkdir test-eks
```
2. Init project
```
pulumi init aws-python -y -s dev -C test-eks
```
3. Pin pulumi version
```
cat <<EOF > test-eks/requirements.txt
pulumi>=3.0.0,<4.0.0
pulumi-aws==6.0.4 #Must be pinned due to pulumi-eks hardcoded dependency
pulumi-eks
pulumi-kubernetes
EOF
```
4. Add pulumi code to `__main__.py`
5. Run `pulumilocal preview -C test-eks -s test` and interrupt it (^C) after it starts to hang
6. Clean up unnecessary endpoints from `Pulumi.test.yaml`
7. We are now set to run the code ✅

### To spin it up
0. (optional) Set AWS variables if there is no default profile configured
```
export AWS_SECRET_ACCESS_KEY=test
export AWS_ACCESS_KEY_ID=test
export AWS_ENDPOINT_URL=http://localhost.localstack.cloud:4566
```
1. Run Localstack
```
localstack start -d
``` 
2. Run pulumi
```
pulumi up -y -C test-eks -s test
```
3. Visit `http://localhost:8081`
4. Profit 💵

### To clean up
Simply run:  
```pulumi destroy -y -C test-eks -s test```

## Notes

- Env variables `AWS_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` are necessary before running the code as kubernetes deployment not inheriting AWS creds
- AWS version pinned to 6.0.4 due to hard coded dependency in pulumi-eks so pulumilocal could generate the right endpoints first (then we removed the ones we didn't need)
- Run with `pulumi` and not `pulumilocal` due to performance degradation in this version of AWS package with increasing number of custom endpoints (adding all 2xx endpoints with `pulumilocal` would make this sample run 20-30 mins)
- if configuring the endpoints manually and not using pulumilocal the version pin is not necessary
- for `NodePort` services one must expose the server port manually with:
```
k3d cluster edit <CLUSTER_NAME> --port-add <HOST_PORT>:<NODE_PORT>@server:0
```
- `LoadBalancer` type services currently are not supported
