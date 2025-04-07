import os
import subprocess
import sys

def run_migrations():
    """Run database migrations"""
    print("Running migrations...")
    subprocess.run([sys.executable, "manage.py", "makemigrations"])
    subprocess.run([sys.executable, "manage.py", "migrate"])

def create_superuser():
    """Create a superuser if it doesn't exist"""
    from django.contrib.auth.models import User
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "admin")
        print("Created superuser: admin/admin")

def main():
    """Main function to run the server"""
    # Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    import django
    django.setup()

    # Run migrations
    run_migrations()

    # Create superuser
    create_superuser()

    # Start server
    print("Starting server...")
    subprocess.run([sys.executable, "manage.py", "runserver", "0.0.0.0:8000"])

if __name__ == "__main__":
    main() 