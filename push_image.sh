aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 950328280813.dkr.ecr.us-east-1.amazonaws.com
docker build -t chainbreaker_server .
docker tag chainbreaker_server:latest 950328280813.dkr.ecr.us-east-1.amazonaws.com/chainbreaker_server:latest
docker push 950328280813.dkr.ecr.us-east-1.amazonaws.com/chainbreaker_server:latest