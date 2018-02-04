//----------------------------------------------------------------------------
// Toxic service user, for accessing CodeCommit/Git to run CI jobs
//----------------------------------------------------------------------------
module "toxic-user" {
  source = "./modules/service_user"
  name = "svc-toxic-${var.realm}"
}
output "toxic-ssh-key-id" {
  value = "${module.toxic-user.ssh-key-id}"
  sensitive = true
}
output "toxic-private-key" {
  value = "${module.toxic-user.private-key}"
  sensitive = true
}
output "toxic-public-key" {
  value = "${module.toxic-user.public-key}"
  sensitive = true
}

//-----------------------------------------------------------
// Auxilliary functions related to this svc user for
// toxic. This block is not required for basic service
// user accounts.
//-----------------------------------------------------------

data "aws_iam_policy_document" "toxic-ecr-policy-doc" {
  statement {
    sid = "ECRWrite"
    effect = "Allow"
    actions = [
      "ecr:*"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "toxic-ecr-policy" {
  path = "/"
  policy = "${data.aws_iam_policy_document.toxic-ecr-policy-doc.json}"
}

resource "aws_iam_user_policy_attachment" "toxic-ecr-policy-attachment" {
  user = "${module.toxic-user.name}"
  policy_arn = "${aws_iam_policy.toxic-ecr-policy.arn}"
}
