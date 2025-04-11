# Quick Start
## Step 1
git clone https://github.com/quanquan1996/aws-s3tables-duckdb-lambda.git    
cd aws-s3tables-duckdb-lambda   
aws ecr get-login-password --region {yourRegion} | docker login --username AWS --password-stdin {yourAccountID}.dkr.ecr.{yourRegion}.amazonaws.com  
sudo docker buildx build --platform linux/amd64 --provenance=false -t docker-image:{yourImageName} .    
sudo docker tag docker-image:{yourImageName} {yourAccountID}.dkr.ecr.{yourRegion}.amazonaws.com/{yourEcrRepoName}:latest    
sudo docker push {yourAccountID}.dkr.ecr.{yourRegion}.amazonaws.com/{yourEcrRepoName}:latest    
## Step 2
use your ECR repo name in the lambda function, and you are ready to go  