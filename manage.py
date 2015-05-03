#!/usr/bin/env python
import os
import sys
import dotenv

try:
    dotenv.read_dotenv()
except:
    pass

if __name__ == "__main__":
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'DEVELOPMENT').title()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard_gobernacion.settings")
    os.environ.setdefault('DJANGO_CONFIGURATION', ENVIRONMENT)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
