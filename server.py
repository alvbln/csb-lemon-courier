#!/usr/bin/env python3
"""Run the Django dev server on a fixed port 8000 for screenshots."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csbproj.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
