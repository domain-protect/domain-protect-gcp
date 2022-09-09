locals {
  env = lower(terraform.workspace)

  slack_channels = local.env == "dev" ? var.slack_channels_dev : var.slack_channels
  secrets        = zipmap(local.slack_channels, var.slack_webhook_urls)
}