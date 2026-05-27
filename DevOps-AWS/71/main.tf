provider "aws" {
  region = "eu-north-1"
}

resource "aws_s3_bucket" "b" {
  bucket = "my-tf-bucket-03042025"

  tags = {
    Name        = "my-bucket"
    Environment = "dev"
  }
}