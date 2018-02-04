//----------------------------------------------------------------------------
// Git repository hosted in AWS
//----------------------------------------------------------------------------
module "engci-repo" {
  source = "./modules/codecommit_repo"
  repo-name = "engci"
}
output "engci-repo-ssh-url" {
  value = "${module.engci-repo.repo-ssh-url}"
}
