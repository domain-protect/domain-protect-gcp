variable "project" {
  description = "GCP project for domain protect infrastructure - define in tfvars file or CI/CD environment variables"
  default     = ""
}

variable "name" {
  description = "application name, forms first part of resource names"
  default     = "domain-protect"
}

variable "region" {
  description = "GCP region to deploy infrastructure"
  default     = "europe-west1"
}

variable "app_service_region" {
  description = "GCP region which App Service is deployed to, this is a Project wide setting"
  default     = "europe-west1"
}

variable "create_app_engine" {
  description = "Create App Engine if not already set up on the Project"
  default     = false
}

variable "zone" {
  description = "GCP availability zone"
  default     = "europe-west1-c"
}

variable "functions" {
  description = "list of names of Functions files in the function/code folder"
  default     = ["cname", "ns", "cname_storage", "a_storage"]
  type        = list(any)
}

variable "slack_channels" {
  description = "List of Slack Channels - enter in tfvars file or CI/CD environment variables"
  default     = []
  type        = list(any)
}

variable "slack_channels_dev" {
  description = "List of Slack Channels to use for testing purposes with dev environment - enter in tfvars file or CI/CD environment variables"
  default     = []
  type        = list(any)
}

variable "slack_webhook_urls" {
  description = "List of Slack webhook URLs, in the same order as the slack_channels list - enter in tfvars file or CI/CD environment variables"
  default     = []
  type        = list(any)
}

variable "slack_emoji" {
  description = "Slack emoji"
  default     = ":warning:"
}

variable "slack_username" {
  description = "Slack username appearing in the from field in the Slack message"
  default     = "Domain Protect"
}

variable "time_zone" {
  description = "Time zone used by Cloud Scheduler"
  default     = "Europe/London"
}

variable "ingress_settings" {
  description = "Controls what traffic can reach the function"
  default     = "ALLOW_INTERNAL_ONLY"
}

variable "schedule" {
  description = "Schedule for triggering functions in CRON syntax"
  default     = "0 9 * * *" #fire at 9 a.m. every day
}

variable "available_memory" {
  description = "Available memory for function"
  default     = 1024
}

variable "runtime" {
  description = "Lambda language runtime"
  default     = "python38"
}

variable "timeout" {
  description = "Function timeout in seconds"
  default     = 540
}