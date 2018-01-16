variable "repo-name" {}

resource "aws_codecommit_repository" "repo" {
  repository_name = "${var.repo-name}"
}

output "repo-ssh-url" {
  value = "${aws_codecommit_repository.repo.clone_url_ssh}"
}
