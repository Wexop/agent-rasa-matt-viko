# Rendu RASA Matthieu HEURTIN et Victor TERRIEN

étapes pour démarrer le bot :

- Créer un venv (python3 -m venv ./venv)
- Aller dans le venv (source ./venv/bin/activate)
- Installer les dépendences `pip3 install rasa datetime rasa_sdk `
- Démarrer le serveur `rasa run actions`
- Entraîner le bot `rasa train`
- Démarrer la conversation `rasa shell`