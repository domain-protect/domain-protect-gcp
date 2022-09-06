locals {
  env = lower(terraform.workspace)

  secrets = zipmap(var.slack_channels, var.slack_webhook_urls)
}