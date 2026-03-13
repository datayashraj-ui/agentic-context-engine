# Oracle Cloud Free Tier Setup

## Create Free Account

1. Go to cloud.oracle.com
2. Click "Start for free"
3. Enter email → verify
4. Choose region: **Choose a region close to your customers** (e.g., ap-mumbai-1 for India)
5. Complete identity verification (credit card required but not charged)

## Create ARM Instance (Always Free)

1. Compute → Instances → Create Instance
2. Name: `nexus-server`
3. Placement: availability domain AD-1 (or whichever has ARM quota)
4. Image: **Ubuntu 24.04** (Canonical Ubuntu)
5. Shape: Click "Change Shape"
   - Shape series: **Ampere** (ARM)
   - Shape: **VM.Standard.A1.Flex**
   - OCPUs: **4** (max free)
   - Memory: **24 GB** (max free)
6. Networking:
   - Create new VCN or use existing
   - Subnet: public subnet
   - Assign public IP: **Yes**
7. Add SSH key:
   - Paste your public key from `~/.ssh/id_ed25519.pub`
   - Or generate new key pair and download
8. Boot volume:
   - Size: **200 GB** (max free)
   - Performance: Balanced
9. Click **Create**

## Configure Security Rules (Open Required Ports)

1. Networking → Virtual Cloud Networks → your VCN
2. Security Lists → Default Security List → Add Ingress Rules

| Source CIDR | Protocol | Port | Description |
|-------------|----------|------|-------------|
| 0.0.0.0/0 | TCP | 22 | SSH |
| 0.0.0.0/0 | TCP | 80 | HTTP (Coolify reverse proxy) |
| 0.0.0.0/0 | TCP | 443 | HTTPS (SSL) |
| 0.0.0.0/0 | TCP | 8000 | Coolify admin (remove after setup) |

**Note:** All other services (3000-8765) stay internal-only.

## Instance firewall (iptables)

Oracle Ubuntu instances have a local firewall too:

```bash
# Open required ports in iptables
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 22 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT

# Save rules
sudo netfilter-persistent save
```

## DNS Configuration

Point your domain to the Oracle Cloud public IP:

```
# In your DNS provider (Cloudflare, Namecheap, etc.)
Type  Name     Value
A     @        YOUR_ORACLE_IP
A     *        YOUR_ORACLE_IP   # Wildcard for subdomains
```

**Cloudflare recommended:** Enable proxying (orange cloud) for DDoS protection.

## Storage Layout

```
/home/nexus/          # Application files
  ├── nexus/          # This repo
  ├── logs/           # All application logs
  └── backups/        # Automated backups

/var/lib/docker/      # Docker volumes (200GB disk)
```

## Free Tier Limits (Always Free)

| Resource | Limit |
|---------|-------|
| OCPUs | 4 (Ampere ARM) |
| RAM | 24 GB |
| Disk | 200 GB |
| Outbound data | 10 TB/month |
| Public IP | 2 |
| Cost | $0 forever |

## Backups

Oracle Cloud free tier doesn't include automatic backups.
Set up manual backups:

```bash
# Weekly backup of Docker volumes to object storage
# (Object Storage: 20 GB always free)
# Add to crontab: 0 2 * * 0 /home/nexus/nexus/scripts/backup.sh
```
