# code-commit

This repository contains Terraform configurations for managing AWS CodeCommit infrastructure.

## Deploying with Terraform

The most direct way to deploy the resources is to run Terraform directly. To do so, `terraform` must be executed from the directory containing the Terraform configuration files, `terraform/`.

```bash
$ cd terraform
```

For environments where AWS credential files are available or wherever it is preferred to not use environment variables or AWS access keys, configure the following, where `PROFILE` refers to a profile in `~/.aws/credentials` with permissions to manage the resources:
```bash
export AWS_PROFILE=PROFILE
```

(Optional) Create a backend configuration file (`remote-state-backend.tf`) if you would like to store terraform state remotely:
```json
{
  "terraform": {
    "backend": {
      "s3":{
        "region":"us-east-1",
        "bucket":"some-bucket",
        "key":"terraform-states/codecommit/terraform.tfstate",
      }
    }
  }
}
```

Create a `codecommit.tfvars` file containing required configuration values:
```json
{
  "realm": "test",
  "aws_region": "us-east-1",
  "foundry_state_bucket": "foundry-lab",
  "foundry_state_key": "terraform-states/site-foundry/terraform.tfstate",
  "users": {
    "firstname.lastname@home.com": [
      "readRepo1,readRepo2",
      "writeRepo1,writeRepo2,..."
    ], ...
  }
}    
```

Then, initialize Terraform:
```bash
$ terraform init
```
There will now be a `.terraform` directory with the configured values.

Now, run `terraform apply`, supplying the configuration values file:

```bash
$ terraform apply -var-file codecommit.tfvars
```
