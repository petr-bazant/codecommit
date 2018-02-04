//----------------------------------------------------------------------------
// Shipyard deployment tool
//----------------------------------------------------------------------------
module "shipyard-repo" {
  source = "./modules/codecommit_repo"
  repo-name = "shipyard"
}
output "shipyard-repo-ssh-url" {
  value = "${module.shipyard-repo.repo-ssh-url}"
}
