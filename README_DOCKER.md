# Odoo 19 Docker Setup

This setup allows you to run Odoo 19 in Docker for testing the custom modules.

## Prerequisites

- Docker installed
- Docker Compose installed

## Quick Start

1. **Build and start the containers:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f odoo
   ```

3. **Access Odoo:**
   - Open your browser and go to: `http://localhost:10019`
   - The first time you access, you'll see the Odoo database creation wizard

4. **Stop the containers:**
   ```bash
   docker-compose down
   ```

5. **Stop and remove volumes (clean start):**
   ```bash
   docker-compose down -v
   ```

## Database Configuration

When creating a new database in Odoo:
- **Database Name**: Choose any name (e.g., `kafaat_test`)
- **Email**: Your admin email
- **Password**: Your admin password
- **Language**: Select your preferred language
- **Country**: Select your country
- **Demo Data**: Uncheck if you don't want demo data

## Module Installation

After creating the database:

1. Go to **Apps** menu
2. Click **Update Apps List**
3. Remove the **Apps** filter to see all modules
4. Search for your custom modules:
   - `grants_training_suite_v19`
   - `hr_employee_enhance`
   - `hr_reward_warning`
   - etc.
5. Click **Install** on the modules you want to test

## Port Configuration

- **Odoo**: Port `10019` (mapped to container port 8069)
- **PostgreSQL**: Port `5432` (for direct database access if needed)

## Volumes

The following volumes are created:
- `odoo-db-data`: PostgreSQL database data
- `odoo-web-data`: Odoo filestore and sessions
- `odoo-config`: Odoo configuration files

## Custom Addons Path

Your custom addons are mounted from:
```
./custom_addons -> /mnt/extra-addons
```

All modules in the `custom_addons` folder are automatically available.

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs odoo

# Restart containers
docker-compose restart
```

### Database connection issues
```bash
# Check if database container is healthy
docker-compose ps

# Restart database
docker-compose restart db
```

### Module not showing
1. Make sure the module is in `custom_addons` folder
2. Check that `__manifest__.py` exists and is valid
3. Update Apps List in Odoo
4. Check Odoo logs for errors:
   ```bash
   docker-compose logs odoo | grep -i error
   ```

### Reset everything
```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove images (optional)
docker rmi kafaat-main_odoo

# Start fresh
docker-compose up -d
```

## Development Tips

### View Odoo logs in real-time
```bash
docker-compose logs -f odoo
```

### Access Odoo shell
```bash
docker-compose exec odoo odoo shell -d your_database_name
```

### Access PostgreSQL
```bash
docker-compose exec db psql -U odoo -d postgres
```

### Restart Odoo only
```bash
docker-compose restart odoo
```

## Environment Variables

You can customize the setup by creating a `.env` file:

```env
POSTGRES_DB=postgres
POSTGRES_USER=odoo
POSTGRES_PASSWORD=odoo
ODOO_PORT=10019
```

## Notes

- The setup uses Odoo 19 official image
- PostgreSQL 15 is used as the database
- All custom addons are automatically available
- Data persists in Docker volumes

