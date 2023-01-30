output "Domain_Protect_permissions" {
  value = "Use GCP IAM console to grant org level permissions to service account ${module.iam.service_account_email} see https://github.com/domain-protect/domain-protect-gcp#manually-apply-audit-permissions-at-org-level"
}

output "Pub_Sub_permissions" {
  value = "Use GCP IAM console to grant project level permission to Google managed service account service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com see https://github.com/domain-protect/domain-protect-gcp#ensure-correct-Pub/Sub-project-level-permissions"
}
