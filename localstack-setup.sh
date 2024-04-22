#!/bin/sh

echo "install dependecies on localstack container..."
apt-get install -y jq

echo "initializing localstack s3"

## setup s3 buckets
awslocal s3 mb s3://file-archive

## upload python container files to s3 bucket
# awslocal s3 cp /var/lib/localstack/lib/hello_heart/python s3://python-files --recursive
# awslocal s3 cp /var/lib/localstack/lib/hello_heart/data s3://data --recursive
# awslocal s3 cp /var/lib/localstack/lib/hello_heart/utils s3://utils --recursive

### create RDS database to store 
awslocal rds create-db-cluster \
    --db-cluster-identifier hh-cluster \
    --engine aurora-postgresql \
    --database-name hhdb \
    --master-username user \
    --master-user-password password

awslocal rds create-db-instance \
    --db-instance-identifier hh-instance \
    --db-cluster-identifier hh-cluster \
    --engine aurora-postgresql \
    --db-instance-class db.t2.micro

cat << 'EOF' > mycreds.json
{
    "engine": "aurora-postgresql", 
    "username": "user",
    "password": "password",
    "host": "localhost",
    "dbname": "hhdb",
    "port": "4510"
}
EOF

awslocal secretsmanager create-secret \
    --name dbpass \
    --secret-string /var/lib/localstack/cache/mycreds.json
