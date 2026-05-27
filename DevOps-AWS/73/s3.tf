resource "aws_s3_bucket" "tf-s3-20250510" {
  bucket = "tf-s3-20250510"

  tags = {
    Name        = "tf-s3-20250510"
    Environment = "dev"
  }
}