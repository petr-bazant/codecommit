//----------------------------------------------------------------------------
// Git repository hosted in AWS
//----------------------------------------------------------------------------
module "codecommit-repo" {
  source = "./modules/codecommit_repo"
  repo-name = "codecommit"
}
output "codecommit-repo-ssh-url" {
  value = "${module.codecommit-repo.repo-ssh-url}"
}
