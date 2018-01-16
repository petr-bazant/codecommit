variable "name"         { }

resource "aws_iam_user" "user" {
  name = "${var.name}"
}

resource "aws_iam_user_ssh_key" "ssh-key" {
  username   = "${aws_iam_user.user.name}"
  encoding   = "SSH"
  public_key = "${tls_private_key.rsa-key.public_key_pem}"
}

resource "tls_private_key" "rsa-key" {
  algorithm = "RSA"
  rsa_bits = 4096
}

data "aws_iam_policy_document" "policy-doc" {
  statement {
    sid = "1"
    effect = "Allow"
    actions = [
      "codecommit:Get*",
      "codecommit:GitPull",
      "codecommit:List*"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "policy" {
  path  = "/"
  policy = "${data.aws_iam_policy_document.policy-doc.json}"
}

resource "aws_iam_user_policy_attachment" "policy-attachment" {
  user       = "${aws_iam_user.user.name}"
  policy_arn = "${aws_iam_policy.policy.arn}"
}

output "name" {
  value = "${aws_iam_user.user.name}"
}

output "ssh-key-id" {
  value = "${aws_iam_user_ssh_key.ssh-key.ssh_public_key_id}"
}

output "private-key" {
  value = "${tls_private_key.rsa-key.private_key_pem}"
  sensitive = true
}

output "public-key" {
  value = "${tls_private_key.rsa-key.public_key_pem}"
  sensitive = true
}
