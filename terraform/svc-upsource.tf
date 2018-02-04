//----------------------------------------------------------------------------
// Upsource service user, for accessing CodeCommit/Git to expose in Upsource
//----------------------------------------------------------------------------
module "upsource-user" {
  source = "./modules/service_user"
  name = "svc-upsource-${var.realm}"
}
output "upsource-ssh-key-id" {
  value = "${module.upsource-user.ssh-key-id}"
  sensitive = true
}
output "upsource-private-key" {
  value = "${module.upsource-user.private-key}"
  sensitive = true
}
output "upsource-public-key" {
  value = "${module.upsource-user.public-key}"
  sensitive = true
}

//-----------------------------------------------------------
// Auxilliary functions related to this svc user for
// Upsource. This block is not required for basic service
// user accounts.
//-----------------------------------------------------------
variable "upsource_project_map"     { type = "map", default = { } }
variable "upsource_admin_user"      { }
variable "upsource_admin_password"  { }
variable "upsource_url"             { }

resource "local_file" "upsource_users_json" {
  content = "${jsonencode(var.users)}"
  filename = "/tmp/upsourceUsers.json"
}

resource "local_file" "upsource_projects_json" {
  content = "${jsonencode(var.upsource_project_map)}"
  filename = "/tmp/upsourceProjects.json"
}

resource "local_file" "upsource_admin_password_txt" {
  content = "${var.upsource_admin_password}"
  filename = "/tmp/upsourceAdminPassword.txt"
}

resource "local_file" "upsource_private_key_file" {
  content = "${module.upsource-user.private-key}"
  filename = "/tmp/upsourcePrivateKey"
}

resource "null_resource" "provision_upsource" {
  triggers {
    users = "${jsonencode(var.users)}"
  }
  provisioner "local-exec" {
    command = "python ${path.module}/provisionUpsource.py -- ${var.upsource_url} ${var.upsource_admin_user} ${local_file.upsource_admin_password_txt.filename} ${local_file.upsource_users_json.filename} ${local_file.upsource_projects_json.filename} ssh://${module.upsource-user.ssh-key-id}@${aws_route53_record.codecommit.fqdn}/v1/repos/ ${local_file.upsource_private_key_file.filename}"
  }
}
