"""Management command to import data from the MySQL source database into SQLite."""
import os
import tempfile

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Importe les données depuis la base MySQL source vers la base SQLite locale."

    def handle(self, *args, **options):
        mysql_host = os.environ.get("MYSQL_HOST", "")
        mysql_port = os.environ.get("MYSQL_PORT", "3306")
        mysql_name = os.environ.get("MYSQL_NAME", "")
        mysql_user = os.environ.get("MYSQL_USER", "")
        mysql_password = os.environ.get("MYSQL_PASSWORD", "")

        if not all([mysql_host, mysql_name, mysql_user, mysql_password]):
            self.stderr.write(self.style.ERROR(
                "Les variables MYSQL_HOST, MYSQL_NAME, MYSQL_USER et MYSQL_PASSWORD "
                "doivent être définies dans le fichier .env."
            ))
            return

        settings.DATABASES["mysql_source"] = {
            "ENGINE": "django.db.backends.mysql",
            "NAME": mysql_name,
            "USER": mysql_user,
            "PASSWORD": mysql_password,
            "HOST": mysql_host,
            "PORT": mysql_port,
            "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
        }

        self.stdout.write(f"Connexion à MySQL {mysql_host}:{mysql_port}/{mysql_name}...")

        dump_file = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                dump_file = f.name

            self.stdout.write("Export des données depuis MySQL...")
            call_command(
                "dumpdata",
                "--database=mysql_source",
                "--natural-foreign",
                "--natural-primary",
                "--output", dump_file,
                verbosity=options["verbosity"],
            )

            self.stdout.write("Import des données dans SQLite...")
            call_command(
                "loaddata",
                dump_file,
                verbosity=options["verbosity"],
            )

            self.stdout.write(self.style.SUCCESS("Import terminé avec succès."))
        finally:
            if dump_file and os.path.exists(dump_file):
                os.unlink(dump_file)
            settings.DATABASES.pop("mysql_source", None)
