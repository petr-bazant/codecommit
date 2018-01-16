{
 "Version": "2012-10-17",
 "Statement": [
  {
   "Effect": "Allow",
   "Action": [
    "codecommit:BatchGetRepositories",
    "codecommit:Get*",
    "codecommit:List*",
    "codecommit:CreateRepository",
    "codecommit:CreateBranch",
    "codecommit:DeleteBranch",
    "codecommit:Put*",
    "codecommit:Test*",
    "codecommit:Update*",
    "codecommit:GitPull",
    "codecommit:GitPush"
   ],
    "Resource": [
        "arn:aws:codecommit:us-east-1:${accountId}:*"
    ]
  }
 ]
}