locals {
  env = lower(terraform.workspace)

  secret_version_list = split("/", var.secret_version_name)
  secret_version      = element(local.secret_version_list, length(local.secret_version_list) - 1)

  secret_resource_id_list = split("/", var.secret_resource_id)
  secret_id               = element(local.secret_resource_id_list, length(local.secret_resource_id_list) - 1)

  slack_channel_sanitised = replace(var.slack_channel, "_", "-") # satisfy Cloud Run naming requirements
}