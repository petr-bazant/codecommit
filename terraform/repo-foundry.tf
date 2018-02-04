//----------------------------------------------------------------------------
// Foundry private cloud infrastructure
//----------------------------------------------------------------------------
module "foundry-repo" {
  source = "./modules/codecommit_repo"
  repo-name = "foundry"
}
output "foundry-repo-ssh-url" {
  value = "${module.foundry-repo.repo-ssh-url}"
}
