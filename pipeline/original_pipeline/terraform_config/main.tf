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

variable "db_username" {
  type = string
  default = "mikey"
}
variable "db_password" {
  type = string
  default = "password"
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

resource "aws_db_subnet_group" "rds_subnets" {
  name = "c20-mikey-museum-db-subnets"
  subnet_ids = data.aws_subnets.c20.ids
}

resource "aws_security_group" "rds_sg" {
  name = "museum-rds-sg"
  description = "For Museum Postgres Access"
  vpc_id = data.aws_vpc.c20.id

  ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "museum" {
  identifier = "c20-mikey-museum-rds"
  engine = "postgres"
  engine_version = "17.4"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  username = var.db_username
  password = var.db_password
  db_subnet_group_name = aws_db_subnet_group.rds_subnets.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  apply_immediately = true
  db_name = "museum"
  publicly_accessible = true
  skip_final_snapshot = true
}


resource "null_resource" "apply_schema" {
  depends_on = [aws_db_instance.museum]

  triggers = {
    schema_checksum = filesha256("../schema.sql")
  }

  provisioner "local-exec" {
    command = <<EOT
PGPASSWORD='${var.db_password}' psql \
  -h ${aws_db_instance.museum.address} \
  -U ${var.db_username} \
  -d museum \
  -p 5432 \
  -f ../schema.sql
EOT
  }
}

output "rds_endpoint" {
  value = aws_db_instance.museum.address
}
output "rds_port" {
  value = aws_db_instance.museum.port
}


