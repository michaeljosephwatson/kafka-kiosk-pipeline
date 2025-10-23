variable "aws_access_key_id" {
  type = string
}
variable "aws_secret_access_key" {
  type = string
}

provider "aws" {
  region = "eu-west-2"
  access_key = var.aws_access_key_id
  secret_key = var.aws_secret_access_key
}

data "aws_vpc" "c20" {
  filter {
    name = "tag:Name"
    values = ["c20-VPC"]
  }
}

data "aws_subnets" "c20" {
  filter {
    name = "tag:Name"
    values = ["c20-public-subnet-2", "c20-public-subnet-1"]
  }
}

resource "aws_security_group" "ec2_sg" {
  name = "c20-mikey-kafka-sg"
  description = "For the running of the kafka pipeline on a ec2 instance"
  vpc_id = data.aws_vpc.c20.id

  ingress {
    description      = "SSH"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
    
}

resource "aws_instance" "kafka_pipeline" {
  ami                    = "ami-0f7b02bb6a0e14062"
  instance_type          = "t2.nano"
  subnet_id              = data.aws_subnets.c20.ids[0]
  key_name = "c20-mikey-kafka-pipeline-w10"
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  associate_public_ip_address = true

  tags = {
    Name = "c20-mikey-kafka-pipeline-ec2"
  }
}