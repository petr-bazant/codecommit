//----------------------------------------------------------------------------
// General build tool
//----------------------------------------------------------------------------
module "build-repo" {
  source = "./modules/codecommit_repo"
  repo-name = "build"
}
output "build-repo-ssh-url" {
  value = "${module.build-repo.repo-ssh-url}"
}
