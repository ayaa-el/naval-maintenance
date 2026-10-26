"""
Lanceur de l'application desktop.
Ouvre le serveur Django en arrière-plan, puis affiche l'interface
dans une fenêtre native (sans barre de navigateur), via pywebview.

Pour lancer l'application :
    python desktop_app.py
"""
import os
import threading
import webbrowser
import django
import webview

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.management import call_command


def demarrer_serveur_django():
    call_command("runserver", "127.0.0.1:8000", use_reloader=False)


class API:
    """Fonctions accessibles depuis le JavaScript de la page (window.pywebview.api)."""

    def ouvrir_dans_navigateur(self, url):
        webbrowser.open(url)


if __name__ == "__main__":
    thread_serveur = threading.Thread(target=demarrer_serveur_django, daemon=True)
    thread_serveur.start()

    webview.create_window(
        "Gestion de la Maintenance Navale - ANP",
        "http://127.0.0.1:8000",
        width=1280,
        height=800,
        min_size=(1000, 700),
        js_api=API(),
    )
    webview.start()