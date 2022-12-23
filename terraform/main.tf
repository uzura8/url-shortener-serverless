variable "prj_prefix" {}
variable "region_api" {}
variable "region_acm" {}
variable "route53_zone_id" {}
variable "domain_api_dev" {}
variable "domain_api_prd" {}

provider "aws" {
  region = var.region_api
  alias  = "api"
}

provider "aws" {
  region = var.region_acm
  alias  = "acm"
}

terraform {
  backend "s3" {
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.74.2"
    }
  }
}

locals {
  fqdn = {
    api_dev = var.domain_api_dev
    api_prd = var.domain_api_prd
  }
}


resource "aws_acm_certificate" "api_dev" {
  provider          = aws.acm
  domain_name       = local.fqdn.api_dev
  validation_method = "DNS"

  tags = {
    Name      = join("-", [var.prj_prefix, "acm"])
    ManagedBy = "terraform"
  }
}
resource "aws_acm_certificate" "api_prd" {
  provider          = aws.acm
  domain_name       = local.fqdn.api_prd
  validation_method = "DNS"

  tags = {
    Name      = join("-", [var.prj_prefix, "acm"])
    ManagedBy = "terraform"
  }
}

# CNAME Record
resource "aws_route53_record" "api_dev_acm_c" {
  for_each = {
    for d in aws_acm_certificate.api_dev.domain_validation_options : d.domain_name => {
      name   = d.resource_record_name
      record = d.resource_record_value
      type   = d.resource_record_type
    }
  }
  zone_id         = var.route53_zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 172800
  records         = [each.value.record]
  allow_overwrite = true
}

resource "aws_route53_record" "api_prd_acm_c" {
  for_each = {
    for d in aws_acm_certificate.api_prd.domain_validation_options : d.domain_name => {
      name   = d.resource_record_name
      record = d.resource_record_value
      type   = d.resource_record_type
    }
  }
  zone_id         = var.route53_zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 172800
  records         = [each.value.record]
  allow_overwrite = true
}

## Related ACM Certification and CNAME record
resource "aws_acm_certificate_validation" "api_dev" {
  provider                = aws.acm
  certificate_arn         = aws_acm_certificate.api_dev.arn
  validation_record_fqdns = [for record in aws_route53_record.api_dev_acm_c : record.fqdn]
}
resource "aws_acm_certificate_validation" "api_prd" {
  provider                = aws.acm
  certificate_arn         = aws_acm_certificate.api_prd.arn
  validation_record_fqdns = [for record in aws_route53_record.api_prd_acm_c : record.fqdn]
}
