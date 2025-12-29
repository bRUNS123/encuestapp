# Credentials & Management Tools

## Default Admin Credentials
When running `python manage.py ensure_admin`, the following superuser is created if it doesn't exist:

- **Email:** `admin@example.com`
- **Password:** `admin123`

## Management Commands

### Create Admin User
To ensure the default admin user exists:
```sh
python manage.py ensure_admin
```

### Clean Test User
To delete a specific user (useful for resetting test scenarios):
```sh
python manage.py clean_test_user --email=test@example.com
```
Replace `test@example.com` with the actual email you want to delete.
