//----------------------------------------------------------------------------
// Toxic CI tool
//----------------------------------------------------------------------------
module "toxic-repo" {
  source = "./modules/codecommit_repo"
  repo-name = "toxic"
}
output "toxic-repo-ssh-url" {
  value = "${module.toxic-repo.repo-ssh-url}"
}
