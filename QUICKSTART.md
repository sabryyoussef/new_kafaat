# Quick Start Guide - Odoo 19 Docker

## 🚀 Quick Start

### Option 1: Using the Start Script (Recommended)
```bash
cd /home/sabry3/Downloads/kafaat-main
./start-docker.sh
```

### Option 2: Manual Start
```bash
cd /home/sabry3/Downloads/kafaat-main
docker-compose up -d
```

## 📍 Access Odoo

Once containers are running:
- **URL**: http://localhost:10019
- **Port**: 10019 (mapped from container port 8069)

## 🗄️ First Time Setup

1. **Create Database**:
   - Open http://localhost:10019
   - Fill in the database creation form:
     - Database Name: `kafaat_test` (or any name)
     - Email: Your email
     - Password: Your admin password
     - Language: Select your language
     - Country: Select your country
     - **Uncheck "Load demonstration data"** (unless you want demo data)

2. **Install Custom Modules**:
   - Go to **Apps** menu
   - Click **Update Apps List**
   - Remove the **Apps** filter
   - Search for your modules:
     - `grants_training_suite_v19`
     - `hr_employee_enhance`
     - `hr_reward_warning`
     - etc.
   - Click **Install**

## 🛠️ Useful Commands

### View Logs
```bash
docker-compose logs -f odoo
```

### Stop Containers
```bash
docker-compose down
```

### Stop and Remove All Data (Fresh Start)
```bash
docker-compose down -v
```

### Restart Odoo
```bash
docker-compose restart odoo
```

### Check Container Status
```bash
docker-compose ps
```

### Access Odoo Shell
```bash
docker-compose exec odoo odoo shell -d your_database_name
```

### Access PostgreSQL
```bash
docker-compose exec db psql -U odoo -d postgres
```

## 📁 Project Structure

```
kafaat-main/
├── custom_addons/          # All your Odoo modules
│   ├── grants_training_suite_v19/
│   ├── hr_employee_enhance/
│   └── ...
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Odoo 19 image
├── start-docker.sh       # Quick start script
└── README_DOCKER.md      # Detailed documentation
```

## ⚙️ Configuration

- **Odoo Port**: 10019
- **PostgreSQL Port**: 5432
- **Database**: postgres
- **User**: odoo
- **Password**: odoo

## 🔧 Troubleshooting

### Port Already in Use
If port 10019 is already in use, edit `docker-compose.yml` and change:
```yaml
ports:
  - "10019:8069"  # Change 10019 to another port
```

### Module Not Showing
1. Check module is in `custom_addons` folder
2. Verify `__manifest__.py` exists
3. Update Apps List in Odoo
4. Check logs: `docker-compose logs odoo | grep -i error`

### Database Connection Issues
```bash
# Check database health
docker-compose ps db

# Restart database
docker-compose restart db
```

## 📝 Notes

- Data persists in Docker volumes
- Custom addons are mounted from `./custom_addons`
- All modules in `custom_addons` are automatically available
- First startup may take a few minutes to download images

