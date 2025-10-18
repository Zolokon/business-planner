# Terraform Configuration Specification - Business Planner

> **Infrastructure as Code for Digital Ocean**  
> **Created**: 2025-10-17  
> **Tool**: Terraform  
> **Target**: Digital Ocean Droplet ($6/month)

---

## 🎯 Purpose

Define entire infrastructure in code:
- **Reproducible** - Can recreate from scratch
- **Version controlled** - Changes tracked in Git
- **Documented** - Infrastructure is self-documenting
- **Automated** - One command to deploy

---

## 📁 Terraform Structure

```
infrastructure/terraform/
├── main.tf           # Main configuration
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── droplet.tf        # Droplet resource
├── networking.tf     # Firewall, domains
├── monitoring.tf     # Alerts (optional)
├── terraform.tfvars.example  # Example values
└── README.md         # How to use
```

---

## 📝 Main Configuration (main.tf)

```hcl
terraform {
  required_version = ">= 1.6.0"
  
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.34"
    }
  }
  
  # Remote state (optional, for team)
  # backend "s3" {
  #   bucket = "planner-terraform-state"
  #   key    = "production/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "digitalocean" {
  token = var.do_token
}
```

---

## 📝 Variables (variables.tf)

```hcl
# Digital Ocean API token
variable "do_token" {
  description = "Digital Ocean API token"
  type        = string
  sensitive   = true
}

# SSH Key
variable "ssh_key_name" {
  description = "Name of SSH key in DO"
  type        = string
  default     = "planner-key"
}

# Droplet Configuration
variable "droplet_name" {
  description = "Name of the Droplet"
  type        = string
  default     = "business-planner"
}

variable "droplet_region" {
  description = "Digital Ocean region"
  type        = string
  default     = "fra1"  # Frankfurt (closest to Kazakhstan)
}

variable "droplet_size" {
  description = "Droplet size"
  type        = string
  default     = "s-1vcpu-1gb"  # $6/month
}

variable "droplet_image" {
  description = "Droplet image"
  type        = string
  default     = "docker-20-04"  # Ubuntu 20.04 with Docker pre-installed
}

# Backups
variable "enable_backups" {
  description = "Enable automated backups (+$1.20/month)"
  type        = bool
  default     = true
}

# Monitoring
variable "enable_monitoring" {
  description = "Enable DO monitoring (free)"
  type        = bool
  default     = true
}

# Tags
variable "tags" {
  description = "Tags for resources"
  type        = list(string)
  default     = ["production", "planner", "telegram-bot"]
}

# Domain (optional)
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}
```

---

## 📝 Droplet Resource (droplet.tf)

```hcl
# SSH Key resource
resource "digitalocean_ssh_key" "planner" {
  name       = var.ssh_key_name
  public_key = file("~/.ssh/id_rsa.pub")
}

# Droplet resource
resource "digitalocean_droplet" "planner" {
  name   = var.droplet_name
  region = var.droplet_region
  size   = var.droplet_size
  image  = var.droplet_image
  
  ssh_keys = [digitalocean_ssh_key.planner.id]
  
  # Enable features
  backups    = var.enable_backups
  monitoring = var.enable_monitoring
  ipv6       = true
  
  tags = var.tags
  
  # User data (cloud-init)
  user_data = templatefile("${path.module}/cloud-init.yaml", {
    hostname = var.droplet_name
  })
  
  # Lifecycle
  lifecycle {
    prevent_destroy = true  # Safety: don't accidentally destroy
  }
}
```

---

## 📝 Networking (networking.tf)

```hcl
# Firewall
resource "digitalocean_firewall" "planner" {
  name = "${var.droplet_name}-firewall"
  
  droplet_ids = [digitalocean_droplet.planner.id]
  
  # SSH (restricted to your IP - change this!)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["YOUR_IP_HERE/32"]  # Replace!
  }
  
  # HTTP (will redirect to HTTPS)
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  # HTTPS
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  # Allow all outbound
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# Domain (optional)
resource "digitalocean_domain" "planner" {
  count = var.domain_name != "" ? 1 : 0
  
  name = var.domain_name
}

# DNS A Record
resource "digitalocean_record" "planner_a" {
  count = var.domain_name != "" ? 1 : 0
  
  domain = digitalocean_domain.planner[0].name
  type   = "A"
  name   = "@"
  value  = digitalocean_droplet.planner.ipv4_address
  ttl    = 3600
}

# DNS AAAA Record (IPv6)
resource "digitalocean_record" "planner_aaaa" {
  count = var.domain_name != "" ? 1 : 0
  
  domain = digitalocean_domain.planner[0].name
  type   = "AAAA"
  name   = "@"
  value  = digitalocean_droplet.planner.ipv6_address
  ttl    = 3600
}
```

---

## 📝 Outputs (outputs.tf)

```hcl
output "droplet_id" {
  description = "ID of the Droplet"
  value       = digitalocean_droplet.planner.id
}

output "droplet_ip" {
  description = "IPv4 address of the Droplet"
  value       = digitalocean_droplet.planner.ipv4_address
}

output "droplet_ipv6" {
  description = "IPv6 address of the Droplet"
  value       = digitalocean_droplet.planner.ipv6_address
}

output "droplet_urn" {
  description = "URN of the Droplet"
  value       = digitalocean_droplet.planner.urn
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh root@${digitalocean_droplet.planner.ipv4_address}"
}

output "webhook_url" {
  description = "Telegram webhook URL"
  value       = var.domain_name != "" ? "https://${var.domain_name}/webhook/telegram" : "https://${digitalocean_droplet.planner.ipv4_address}/webhook/telegram"
}

output "monthly_cost" {
  description = "Estimated monthly cost"
  value       = "$${var.enable_backups ? "7.20" : "6.00"}/month"
}
```

---

## 📝 Cloud-Init (cloud-init.yaml)

```yaml
#cloud-config

# Set hostname
hostname: ${hostname}
fqdn: ${hostname}.local

# Update packages
package_update: true
package_upgrade: true

# Install packages
packages:
  - docker-compose
  - certbot
  - python3-certbot-nginx
  - fail2ban
  - ufw

# Create planner user
users:
  - name: planner
    groups: docker
    shell: /bin/bash
    sudo: ['ALL=(ALL) NOPASSWD:ALL']

# Setup directories
runcmd:
  - mkdir -p /opt/business-planner
  - mkdir -p /backups
  - chown -R planner:planner /opt/business-planner
  
  # Configure fail2ban
  - systemctl enable fail2ban
  - systemctl start fail2ban
  
  # Setup firewall (in addition to DO firewall)
  - ufw allow 22/tcp
  - ufw allow 80/tcp
  - ufw allow 443/tcp
  - ufw --force enable
  
  # Docker cleanup cron
  - echo "0 3 * * * docker system prune -af --volumes --filter 'until=720h'" | crontab -
```

---

## 🚀 Usage Commands

### Initialize

```bash
# Navigate to terraform directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan (preview changes)
terraform plan

# Apply (create infrastructure)
terraform apply

# Outputs
terraform output
```

### Update Infrastructure

```bash
# Make changes to .tf files

# Preview changes
terraform plan

# Apply changes
terraform apply

# Destroy (careful!)
terraform destroy
```

---

## 📊 Cost Estimation

```bash
# Preview costs (built-in)
terraform plan

# Expected output:
# digitalocean_droplet.planner: $6.00/month
# backups: $1.20/month (if enabled)
# Total: $7.20/month
```

---

## 🔒 Secrets Management

### terraform.tfvars (NOT in Git!)

```hcl
# Create this file locally
# Add to .gitignore

do_token = "dop_v1_xxxxxxxxxxxxxxxxxxxxx"
ssh_key_name = "planner-production"
domain_name = "planner.yourdomain.com"
```

### Environment Variables

```bash
# Alternative: Use env vars
export TF_VAR_do_token="dop_v1_xxxx"
export TF_VAR_domain_name="planner.yourdomain.com"

terraform apply
```

---

## ✅ Terraform Checklist

Before `terraform apply`:

- [ ] DO API token configured
- [ ] SSH key exists (~/.ssh/id_rsa.pub)
- [ ] terraform.tfvars created (not in Git!)
- [ ] Reviewed plan output
- [ ] Confirmed costs
- [ ] Ready to create real infrastructure

---

**Status**: ✅ Terraform Specification Complete  
**Resources**: Droplet, Firewall, Domain (optional)  
**Cost**: $6-7/month  
**Next**: Docker Configuration

