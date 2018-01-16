variable "realm"                { }
variable "aws_region"           { }
variable "foundry_state_bucket" { }
variable "foundry_state_key"    { }

provider "aws" {
  region = "${var.aws_region}"
}

data "aws_caller_identity" "current" {}

data "terraform_remote_state" "foundry" {
  backend = "s3"
  config {
    bucket = "${var.foundry_state_bucket}"
    key    = "${var.foundry_state_key}"
    region = "${var.aws_region}"
  }
}

resource "aws_route53_record" "codecommit" {
  zone_id   = "${data.terraform_remote_state.foundry.public_zone_id}"
  name      = "git"
  type      = "CNAME"
  ttl       = "300"
  records   = ["git-codecommit.us-east-1.amazonaws.com"]
}
