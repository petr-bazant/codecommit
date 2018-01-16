{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1505654428000",
            "Effect": "Allow",
            "Action": [
                "codecommit:GitPull"
            ],
            "Resource": [
                "arn:aws:codecommit:us-east-1:${accountId}:*"
            ]
        }
    ]
}