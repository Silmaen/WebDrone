# WebDrone

ServerWeb for drone management — Django, French UI. Production host : `drone.argawaen.net`.

## Déploiement

```bash
cp .env.sample .env    # puis éditer : au minimum SECRET_KEY et ALLOWED_HOSTS
./deploy.sh            # pull + build + up + attente des healthchecks
```

`deploy.sh` est le point d'entrée unique — il vérifie l'outillage et le `.env`, crée les
répertoires montés avant que Docker ne le fasse en root, met à jour le dépôt, rafraîchit
les images, construit, démarre, et attend que `web` puis `nginx` se déclarent sains.
Migrations et `collectstatic` sont lancés par `entrypoint.sh` au démarrage du conteneur.

```bash
./deploy.sh check           # y a-t-il une mise à jour en attente ? (0 / 10 / 1)
./deploy.sh --no-pull       # ne rien récupérer, déployer ce qui est sur le disque
./deploy.sh --tests         # lancer les tests avant de démarrer
./deploy.sh --dry-run       # afficher le plan sans rien exécuter
./deploy.sh status | logs [service] | stop | restart
./deploy.sh tests [app] | superuser | shell
./deploy.sh help
```

Le même fichier est ce qu'actionne le bouton « Mettre à jour » de la console de la flotte,
qui le lance sans argument et sans terminal : voir `CLAUDE.md` pour les contraintes que
cela impose.

## Services

| Service | Image | Publié |
|---|---|---|
| `web` | construite ici (`python:3.13-slim`), gunicorn sur `:8000` | non, réseau compose uniquement |
| `nginx` | `nginx:1.30.4-alpine`, sert `/static/` et `/media/`, proxy pour le reste | `${PORT:-8180}:80` |

Les versions d'images sont épinglées et suivies par `wud` via les labels
`wud.*` du `docker-compose.yml` ; la logique de chaque label est documentée dans
`CLAUDE.md`.

## Développement local

```bash
python manage.py runserver
python manage.py test
```
