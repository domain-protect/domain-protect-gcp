module "services" {
  source = "./terraform-modules/services"
}

module "iam" {
  source     = "./terraform-modules/iam"
  name       = var.name
  depends_on = [module.services.iam_service_id]
}

module "pubsub-results" {
  source  = "./terraform-modules/pubsub-results"
  name    = var.name
  project = var.project
}

module "pubsub-scheduler" {
  source             = "./terraform-modules/pubsub-scheduler"
  name               = var.name
  app_service_region = var.app_service_region
  create_app_engine  = var.create_app_engine
  project            = var.project
  time_zone          = var.time_zone
  schedule           = var.schedule
  schedule_dev       = var.schedule_dev
  depends_on         = [module.services.cloud_scheduler_service_id]
}

module "storage" {
  source = "./terraform-modules/storage"
  name   = var.name
  region = var.region
}

module "function" {
  source                = "./terraform-modules/function"
  functions             = var.functions
  name                  = var.name
  project               = var.project
  region                = var.region
  bucket_name           = module.storage.bucket_name
  available_memory      = var.available_memory
  timeout               = var.timeout
  ingress_settings      = var.ingress_settings
  runtime               = var.runtime
  pubsub_topic          = module.pubsub-scheduler.pubsub_topic_name
  service_account_email = module.iam.service_account_email
  depends_on            = [module.services.cloud_functions_service_id, module.services.cloud_build_service_id]
}

module "function-slack" {
  source                = "./terraform-modules/function-slack"
  functions             = var.functions
  name                  = var.name
  project               = var.project
  region                = var.region
  bucket_name           = module.storage.bucket_name
  timeout               = var.timeout
  ingress_settings      = var.ingress_settings
  runtime               = var.runtime
  pubsub_topic          = module.pubsub-results.pubsub_topic_name
  service_account_email = module.iam.service_account_email
  slack_channels        = local.env == "dev" ? var.slack_channels_dev : var.slack_channels
  slack_webhook_urls    = var.slack_webhook_urls
  slack_emoji           = var.slack_emoji
  slack_username        = var.slack_username
  depends_on            = [module.services.cloud_functions_service_id, module.services.cloud_build_service_id]
}