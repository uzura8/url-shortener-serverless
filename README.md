# Url-Shortener-Serverless

Constructed by

* Serverside: Flask + Lambda + APIGateway (deploy by serverside framework)

## Instration

#### Preparation

You need below

* nodeJS >= v14.15.X
* aws-cli >= 1.18.X
* Terraform >= 0.14.5

#### Install tools

Install serverless, python venv and terraform on mac

```bash
# At project root dir
npm install -g serverless
python3 -m venv .venv

brew install tfenv
tfenv install 0.14.5
tfenv use 0.14.5
```

### Install Packages

Install npm packages

```bash
# At project root dir
npm install
```

Install python packages

```bash
. .venv/bin/activate
pip install -r requirements.txt
```

## Deploy AWS Resources by Terraform

#### Create AWS S3 Bucket for terraform state and frontend config

Create S3 Buckets like below in ap-northeast-1 region

* __your-serverless-deployment__
    + Store deployment state files by terraformand and serverless framework
    + Create directory "terraform/your-project-name"

#### 1. Edit Terraform config file

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform
cp terraform.tfvars.sample terraform.tfvars
vi terraform.tfvars
```

```terraform
prj_prefix = "your-porject-name"
 ...
route53_zone_id = "Set your route53 zone id"
domain_api_prd  = "your-domain.example.com"
domain_api_dev  = "your-domain-dev.example.com"
```

#### 2. Set AWS profile name to environment variable

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=your-aws-profile-name
export AWS_REGION="ap-northeast-1"
```

#### 3. Execute terraform init

Command Example to init

```bash
terraform init -backend-config="bucket=your-serverless-deployment" -backend-config="key=terraform/your-project/terraform.tfstate" -backend-config="region=ap-northeast-1" -backend-config="profile=your-aws-profile-name"
```

#### 4. Execute terraform apply

```bash
terraform apply -auto-approve -var-file=./terraform.tfvars
```

## Deploy Server Side Resources

### Setup configs

Setup config files per stage

```bash
cp -r config/stages-sample config/stages
vi config/stages/*
```

```bash
# config/stages/common.yml

service: 'your-project-name'
awsAccountId: 'your-aws-acconnt-id'
defaultRegion: 'ap-northeast-1'
deploymentBucketName: 'your-serverless-deployment'
cmsService: 'your-cms-project'
```

```bash
# config/stages/prd.yml
# config/stages/dev.yml

domainName: your-domain.example.com
notificationEmail: admin@example.com
 ...
```


### Create Domains for API

Execute below command

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE="your-profile-name"
export AWS_REGION="ap-northeast-1"

sls create_domain # Deploy for dev
```

If deploy for prod

```bash
sls create_domain --stage prd # Deploy for prod
```

### Deploy to Lambda

Execute below command

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE="your-profile-name"
export AWS_REGION="ap-northeast-1"

sls deploy # Deploy for dev
```

If deploy for prod

```bash
sls deploy --stage prd # Deploy for prod
```

## Development
### Local Development

Install packages for development

```bash
. .venv/bin/activate
pip install pylint
```

### Work on local

Set venv

```bash
. .venv/bin/activate
```

Start dynamodb local

```bash
sls dynamodb install
sls dynamodb start
```

Execute below command

```bash
sls wsgi serve
```

Request [http://127.0.0.1:5000](http://127.0.0.1:5000/hoge)


## Destroy Resources

Destroy for serverless resources

```bash
sls remove --stage Target-stage
sls delete_domain --stage Target-stage
```

Removed files in S3 Buckets named "your-domain.example.com-cloudfront-logs" and "your-domain.example.com" 

Destroy for static server resources by Terraform

```bash
terraform destroy -auto-approve -var-file=./terraform.tfvars
```

