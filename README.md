# domain-protect-gcp
* Scans Google Cloud DNS across a GCP Organization for domain records vulnerable to takeover
* Amazon Route53 vulnerable domains can be detected by [Domain Protect](https://github.com/ovotech/domain-protect)

### deploy to security audit project and scan your entire GCP Organization

![Alt text](images/gcp-architecture.png?raw=true "Domain Protect GCP architecture")

### receive alerts by Slack or email

<kbd>
  <img src="images/slack-gcp.png" width="500">
</kbd>

### deploy in your GCP Organization using GitHub Actions

<kbd>
  <img src="images/deploy-pipeline.png" width="500">
</kbd>

### or manually scan from your laptop

![Alt text](manual-scans/images/gcp-cname.png?raw=true "Detect vulnerable ElasticBeanstalk CNAMEs")

## subdomain detection functionality
Scans Google Cloud DNS for:
* Subdomain NS delegations vulnerable to takeover
* CNAME records for missing Google Cloud Storage buckets
* A records for Google Cloud Load Balancer with missing storage bucket backend  
* Vulnerable CNAME records for Azure resources
* Vulnerable CNAME records for AWS resources  
* CNAME for Amazon CloudFront distributions with missing S3 origin
* CNAME for Amazon S3 website

## options
1. scheduled Google Cloud Functions with Slack alerts, across a GCP Organization, deployed using Terraform
2. [manual scans](manual-scans/README.md) run from your laptop or Cloud Shell

## notifications
* Slack channel notification per vulnerability type, listing account names and vulnerable domains

## requirements
* Storage bucket for Terraform state file
* Terraform 1.0.x
* Service Usage API enabled on Google Cloud project

## deployment permissions
The Terraform service account requires the following roles at the Project level:
```
App Engine Creator
Cloud Functions Developer
Cloud Scheduler Admin
Create Service Accounts
Project IAM Admin
Pub/Sub Admin
Service Account Admin
Service Account User
Service Usage Admin
Storage Admin
```

## usage
* replace the Terraform state Google Cloud Storage bucket fields in the command below as appropriate
* for local testing, duplicate terraform.tfvars.example, rename without the .example suffix
* enter details appropriate to your organization and save
* alternatively enter Terraform variables within your CI/CD pipeline
* check whether App Engine has been created in the infrastructure project
* add Terraform variables ```create_app_engine``` and ```app_service_region``` if different from default

```
terraform init -backend-config=bucket=TERRAFORM_STATE_BUCKET -backend-config=prefix="terraform/state/domain-protect-gcp"
terraform workspace new dev
terraform plan
terraform apply
```

## manually apply audit permissions at org level
* At the organisation level, IAM, apply the following permissions to the domain-protect service account:
```
DNS Reader (roles/dns.reader)
Folder Viewer (roles/resourcemanager.folderViewer)
Organization Viewer (roles/resourcemanager.organizationViewer) 
```
* This step is performed manually to avoid giving org wide IAM permisssions to the Terraform service account

## adding notifications to extra Slack channels
* add an extra channel to your slack_channels variable list
* add an extra webhook URL or repeat the same webhook URL to your slack_webhook_urls variable list
* apply Terraform

## ci/cd
* infrastructure deployed using GitHub Actions
* use separate deployment repository [domain-protect-gcp-deploy](https://github.com/domain-protect/domain-protect-gcp-deploy)
* use OpenID Connect, service account keys not required
* configuration details provided at [domain-protect-gcp-deploy](https://github.com/domain-protect/domain-protect-gcp-deploy)

| GITHUB ACTIONS SECRETS             | EXAMPLE                                                                         |
|--------------------------------|------------------------------------------------------------------------------------------------|
| GCP_WORKLOAD_IDENTITY_PROVIDER | projects/123456789/locations/global/workloadIdentityPools/github-actions/providers/domain-protect-gcp-github |
| GCP_SERVICE_ACCOUNT            | my-service-account@my-project.iam.gserviceaccount.com                                          |
| TERRAFORM_STATE_BUCKET         | tfstate48903                                                                                   |
| TERRAFORM_STATE_PREFIX         | terraform/state/domain-protect-gcp                                                                             |                                                               |                                  |
| SLACK_CHANNELS                 | ["security-alerts"]                                                                            |
| SLACK_CHANNELS_DEV             | ["security-alerts-dev"]                                                                        |
| SLACK_WEBHOOK_URLS             | ["https://hooks.slack.com/services/XXX/XXX/XXX"]                                               |
| TF_VAR_project                 | mygcpprojectid                                                                                 |


## local development

* Python and Terraform local tests:
```
black --check --line-length 120 .
prospector --max-line-length 120 --profile tests/prospector/profile.yaml
bandit --ini .config/sast_python_bandit_cli.yml manual-scans terraform-modules
terraform fmt -check -recursive
checkov --config-file .config/sast_terraform_checkov_cli.yml --directory
```

## limitations
* this tool cannot guarantee 100% protection against subdomain takeover
* it only scans Google Cloud DNS, and only checks a limited number of takeover types
* for detection of Amazon Route53 vulnerable domains use [Domain Protect](https://github.com/ovotech/domain-protect)