//----------------------------------------------------------------------------
// Job definitions for Toxic CI tool
//----------------------------------------------------------------------------
module "toxicjob-repo" {
  source = "./modules/codecommit_repo"
  repo-name = "toxicjob"
}
output "toxicjob-repo-ssh-url" {
  value = "${module.toxicjob-repo.repo-ssh-url}"
}
