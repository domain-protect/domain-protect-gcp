module "services" {
  source = "./terraform-modules/services"
}

module "iam" {
  source     = "./terraform-modules/iam"
  name       = var.name
  project    = var.project
  depends_on = [module.services.iam_service_id]
}

module "pubsub-projects" {
  source  = "./terraform-modules/pubsub-projects"
  name    = var.name
  project = var.project
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

module "function-projects" {
  source                = "./terraform-modules/function-projects"
  name                  = var.name
  project               = var.project
  region                = var.region
  bucket_name           = module.storage.bucket_name
  timeout               = var.timeout
  ingress_settings      = var.ingress_settings
  runtime               = var.runtime
  pubsub_topic          = module.pubsub-scheduler.pubsub_topic_name
  service_account_email = module.iam.service_account_email
  depends_on            = [module.services.cloud_functions_service_id, module.services.cloud_build_service_id]
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
  pubsub_topic          = module.pubsub-projects.pubsub_topic_name
  service_account_email = module.iam.service_account_email
  depends_on            = [module.services.cloud_functions_service_id, module.services.cloud_build_service_id]
}

module "function-slack" {
  for_each = toset(local.slack_channels)

  source                = "./terraform-modules/function-slack"
  name                  = var.name
  project               = var.project
  region                = var.region
  bucket_name           = module.storage.bucket_name
  timeout               = var.timeout
  ingress_settings      = var.ingress_settings
  runtime               = var.runtime
  pubsub_topic          = module.pubsub-results.pubsub_topic_name
  secret_resource_id    = module.secret-manager[each.key].secret_resource_id
  secret_version_name   = module.secret-manager[each.key].secret_version_name
  service_account_email = module.iam.service_account_email
  slack_channel         = each.key
  slack_emoji           = var.slack_emoji
  slack_username        = var.slack_username
  depends_on            = [module.services.cloud_functions_service_id, module.services.cloud_build_service_id]
}

module "secret-manager" {
  for_each = local.secrets

  source       = "./terraform-modules/secret-manager"
  app_name     = var.name
  secret_name  = each.key
  secret_value = each.value
  depends_on   = [module.services.secret_manager_service_id]
}