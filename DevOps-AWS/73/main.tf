resource "aws_vpc" "tf-vpc-20250510" {
  cidr_block       = "${var.vpc_cidr_block}"
  instance_tenancy = "default"

  tags = {
    Name = "tf-vpc-20250510"
    Env  = "prod"
  }
}

terraform {
  backend "s3" {
    bucket = "tf-s3-20250510"
    key    = "terraform-my-backup.tfstate"
    region = "eu-north-1"
    dynamodb_table = "tf-ddb-20250510"
  }
}

output "aws_vpc_output" {
  value = "${aws_vpc.tf-vpc-20250510.id}"
}