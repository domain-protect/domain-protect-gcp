locals {
  env = lower(terraform.workspace)

  slack_channels     = local.env == "dev" ? var.slack_channels_dev : var.slack_channels
  slack_webhook_urls = local.env == "dev" && var.slack_webhook_type == "app" && length(var.slack_webhook_urls_dev) > 0 ? var.slack_webhook_urls_dev : var.slack_webhook_urls
  secrets            = zipmap(local.slack_channels, local.slack_webhook_urls)
}