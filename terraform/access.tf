variable "users" { type = "map", default = { } }

# Repository access controls
data "aws_iam_policy_document" "repo-policy-doc" {
  count = "${length(keys(var.users))}"

  statement {
    sid = "RepoList"
    effect = "Allow"
    actions = [
      "codecommit:GetRepository",
      "codecommit:BatchGetRepositories",
      "codecommit:ListRepositories"
    ]
    resources = [ "*" ]
  }

  statement {
    sid = "RepoRead"
    effect = "Allow"
    actions = [
      "codecommit:Get*",
      "codecommit:GitPull",
      "codecommit:List*"
    ]
    resources = ["${formatlist("arn:aws:codecommit:%s:%s:%s", var.aws_region, data.aws_caller_identity.current.account_id, split(",", replace(element(var.users[element(keys(var.users), count.index)],0), " ", "") ))}"]
  }

  statement {
    sid = "RepoWrite"
    effect = "Allow"
    actions = [
      "codecommit:CreateBranch",
      "codecommit:DeleteBranch",
      "codecommit:Get*",
      "codecommit:GitPull",
      "codecommit:GitPush",
      "codecommit:List*",
      "codecommit:UpdateDefaultBranch"
    ]
    resources = ["${formatlist("arn:aws:codecommit:%s:%s:%s", var.aws_region, data.aws_caller_identity.current.account_id, split(",", replace(element(var.users[element(keys(var.users), count.index)],1), " ", "") ))}"]
  }

  statement {
    sid = "ECRRead"
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetRepositoryPolicy",
      "ecr:DescribeRepositories",
      "ecr:ListImages",
      "ecr:BatchGetImage"
    ]
    resources = [ "*" ]
  }
}

resource "aws_iam_policy" "repo-policy" {
  count = "${length(keys(var.users))}"
  name  = "repo-policy-${uuid()}"
  path  = "/"
  policy = "${element(data.aws_iam_policy_document.repo-policy-doc.*.json, count.index)}"

  lifecycle {
    ignore_changes = ["name"]
  }
}

resource "aws_iam_user_policy_attachment" "rp-policy-attachment" {
  count   = "${length(keys(var.users))}"
  user    = "${element(keys(var.users), count.index)}"
  policy_arn = "${element(aws_iam_policy.repo-policy.*.arn, count.index)}"
}

data "aws_iam_policy_document" "console-policy-doc" {
  count = "${length(keys(var.users))}"

  statement {
    sid = "ConsoleRead"
    effect = "Allow"
    actions = [
      "codecommit:Get*",
      "codecommit:GitPull",
      "codecommit:List*"      
    ]
    resources = ["${formatlist("arn:aws:codecommit:%s:%s:%s", var.aws_region, data.aws_caller_identity.current.account_id, concat(split(",", replace(element(var.users[element(keys(var.users), count.index)],0), " ", "")), split(",", replace(element(var.users[element(keys(var.users), count.index)],1), " ", ""))))}"]
  }

  statement {
    sid = "ConsoleWrite"
    effect = "Allow"
    actions = [
      "codecommit:GetRepository",
      "codecommit:BatchGetRepositories",
      "codecommit:ListRepositories"
    ]
    resources = [ "*" ]
  }
}

resource "aws_iam_policy" "console-policy" {
  count = "${length(keys(var.users))}"
  name  = "console-policy-${uuid()}"
  path  = "/"
  policy = "${element(data.aws_iam_policy_document.console-policy-doc.*.json, count.index)}"

  lifecycle {
    ignore_changes = ["name"]
  }
}

resource "aws_iam_role_policy_attachment" "cl-policy-attachment" {
  count   = "${length(keys(var.users))}"
  role       = "${data.terraform_remote_state.foundry.role_prefix}${element(keys(var.users), count.index)}${data.terraform_remote_state.foundry.role_suffix}"
  policy_arn = "${element(aws_iam_policy.console-policy.*.arn, count.index)}"
}
