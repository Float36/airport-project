#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from concurrent.futures.process import EXTRA_QUEUED_CALLS

from pyngrok import ngrok, conf
import atexit


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airport_config.settings')

    # if 'runserver' in sys.argv:
    #     try:
    #         # getting a port
    #         port_index = sys.argv.index('runserver') + 1
    #
    #         port = int(sys.argv[port_index]) if len(sys.argv) > port_index and sys.argv[port_index].isdigit() else 8000
    #     except ValueError:
    #         port = 8000
    #
    #     try:
    #         # Open HTTP tunnel to port
    #         public_url = ngrok.connect(port)
    #         public_url_str = public_url.public_url
    #
    #         print("=" * 50)
    #         print(f"!!! NGROK TUNNEL IS RUNNING AT: {public_url_str} !!!")
    #         print("=" * 50)
    #
    #         # Close tunnel when server is closed
    #         atexit.register(ngrok.disconnect, public_url)
    #
    #         # Add ngrok to ALLOWED_HOSTS
    #         from django.conf import settings
    #
    #         # Got a host
    #         ngrok_host = public_url_str.split("//")[1]
    #         settings.ALLOWED_HOSTS.append(ngrok_host)
    #     except Exception as e:
    #         print(f"!!! NGROK FAILED TO START: {e} !!!")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
