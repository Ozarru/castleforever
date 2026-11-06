#!/usr/bin/env python
"""Standalone helper to populate the CastleForever catalog database."""
import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.management import call_command

if __name__ == "__main__":
    call_command("seed_catalog")
    print("Database populated.")
