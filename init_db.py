"""
Kohisar Model School & College (KMS)
Automated Database Initialization Script
"""
import sys
import os

def check_and_create_db():
    print("[*] Checking PostgreSQL server connection...")
    try:
        import psycopg
    except ImportError:
        print("[!] psycopg is not installed yet.")
        sys.exit(1)

    db_name = os.environ.get('KMS_DB_NAME', 'kms_db')
    db_user = os.environ.get('KMS_DB_USER', 'postgres')
    db_pass = os.environ.get('KMS_DB_PASSWORD', 'postgres')
    db_host = os.environ.get('KMS_DB_HOST', '127.0.0.1')
    db_port = os.environ.get('KMS_DB_PORT', '5432')

    try:
        conn = psycopg.connect(
            dbname="postgres",
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
            autocommit=True
        )
    except Exception as e:
        print(f"\n[ERROR] Could not connect to PostgreSQL server at {db_host}:{db_port}.")
        print(f"Details: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL service is running.")
        print(f"2. User '{db_user}' exists with password '{db_pass}'.")
        print("   If you used a different password during PostgreSQL installation,")
        print("   please update DATABASES['default']['PASSWORD'] in school_app/settings.py.")
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db_name,))
            exists = cur.fetchone()
            if not exists:
                print(f"[*] Database '{db_name}' does not exist. Creating database...")
                cur.execute(f'CREATE DATABASE "{db_name}" ENCODING "UTF8";')
                print(f"[OK] Database '{db_name}' created successfully.")
            else:
                print(f"[OK] Database '{db_name}' already exists.")
    finally:
        conn.close()

def ensure_superuser():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_app.settings")
    import django
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        print("[*] Creating default admin superuser (admin / admin123)...")
        User.objects.create_superuser('admin', 'admin@kohisar.edu.pk', 'admin123')
        print("[OK] Superuser 'admin' created.")
    else:
        print("[OK] Superuser account already exists.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--create-superuser':
        ensure_superuser()
    else:
        check_and_create_db()
