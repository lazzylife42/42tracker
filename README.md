# 42tracker

[![wakatime](https://wakatime.com/badge/user/4e37586b-a92c-445c-9c61-d6eecf04f9b7/project/bb1eac4f-1807-470d-ac96-d37dcaf13fe6.svg)](https://wakatime.com/badge/user/4e37586b-a92c-445c-9c61-d6eecf04f9b7/project/bb1eac4f-1807-470d-ac96-d37dcaf13fe6)

---

## TLDR

App de tracking personnel pour monitorer ma progression vers un stage tech tier-1. Backend FastAPI + PostgreSQL selfhosté sur homelab, avec sync automatique depuis l'API 42 et LeetCode.

---

## But

Objectif principal : décrocher un stage chez Google, Spotify, Revolut ou équivalent d'ici décembre 2026.

4 domaines trackés :
- **RNCP 7 AI + Databases** — progression XP par bloc, projets validés
- **LeetCode** — patterns résolus (objectif 135 Medium/Hard)
- **Skills gap** — checklist système design, ML theory, MLOps
- **Outreach pipeline** — contacts LinkedIn, statuts, referrals

Projet vitrine fullstack : FastAPI + React + SwiftUI (app iOS = projet 42 Swifty-Companion adapté).

Selfhosté sous `tracker.sabinomonte.ch` via Cloudflare Tunnel sur NUC homelab.

---

## Setup

```bash
cp .env.example .env  # remplir les variables
docker compose up --build -d
```

- `http://localhost:9080` — API FastAPI + docs Swagger
- `http://localhost:9081` — pgAdmin

---

## Endpoints

| Méthode | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Vérifie que la DB est up |
| GET | `/api/projects/` | Liste tous les projets 42 |
| GET | `/api/42/sync` | Sync les projets depuis l'API 42 |

---

## Stack

```
Backend   		: Python 3.11 · FastAPI · SQLAlchemy 2.0 · PostgreSQL 16
Infra     		: Docker Compose · pgAdmin · Cloudflare Tunnel
Intégrations		: API 42 Intranet (OAuth2) · LeetCode GraphQL (à venir)
Frontend  		: React + Tailwind (à venir)
iOS       		: SwiftUI (à venir)
```

---

## Structure

```
app/
  main.py       # FastAPI, routes, lifespan
  models.py     # Tables SQLAlchemy (définition DB)
  schemas.py    # Schémas Pydantic (validation API)
  database.py   # Engine, SessionLocal
  api.py        # Clients API 42 + LeetCode
  sync.py       # Logique de sync/upsert
```

---

---

# Détails techniques

> Mémo des concepts appris pendant le développement.

---

## `database.py`

L'**engine** est la connexion à la base de données. Il lit les variables d'environnement pour construire l'URL de connexion `postgresql://user:password@host:5432/db`.

La **SessionLocal** est une factory qui crée des sessions individuelles — une session par requête HTTP, une transaction isolée.

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# autocommit=False → les transactions sont explicites
# on commit() manuellement quand tout est ok
# si erreur → rollback() automatique, DB intacte
```

`DeclarativeBase` est la classe mère de tous les models. Elle maintient un registre interne (`metadata`) que `create_all` utilise pour générer les tables.

---

## `models.py`

Les models SQLAlchemy définissent la structure des tables SQL. C'est l'équivalent d'un `CREATE TABLE`.

```python
class Projects_42(BASE):
    __tablename__ = "projects_42"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # NOT NULL explicite
    slug = Column(String)                  # nullable implicite (défaut)
```

**Règle** : `nullable=True` est le défaut dans SQLAlchemy. On écrit `nullable=False` seulement quand la colonne est vraiment requise métier.

Les **Enums Python** contraignent les valeurs possibles d'une colonne. SQLAlchemy stocke le **nom** de l'enum en DB, pas la valeur :
```python
class BlocEnum(PyEnum):
    ai = "AI"   # stocké en DB : "ai", affiché : "AI"
    db = "DB"

# INSERT correct :
INSERT INTO projects_42 (bloc) VALUES ('ai')  -- pas 'AI'
```

`create_all` crée les tables si elles n'existent pas (`CREATE TABLE IF NOT EXISTS`). Il ne modifie pas les tables existantes — pour les migrations destructives (ALTER, DROP), il faudra Alembic.

---

## `schemas.py`

Les schemas Pydantic définissent ce que l'API reçoit et retourne en JSON. Distinct des models SQLAlchemy — deux couches séparées.

```
HTTP JSON  →  Pydantic (validation entrée)  →  SQLAlchemy (écriture DB)
DB object  →  Pydantic (sérialisation)      →  HTTP JSON (réponse)
```

**`from_attributes = True`** dans `model_config` permet à Pydantic de lire les attributs d'un objet SQLAlchemy. Sans ça, Pydantic attend un dict et plante sur un objet ORM.

Pattern recommandé avec plusieurs classes selon l'usage :
```python
class ProjectBase(BaseModel):      	# champs communs
class ProjectResponse(ProjectBase): 	# GET — ajoute id + from_attributes
class ProjectUpdate(BaseModel):     	# PATCH — tous les champs optionnels
```

`ProjectUpdate` n'hérite pas de `ProjectBase` — dans un PATCH on veut pouvoir envoyer un seul champ sans que les autres soient requis.

---

## `main.py`

**`lifespan`** contrôle le cycle de vie de l'app. Code avant `yield` = startup, après `yield` = shutdown.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    models.BASE.metadata.create_all(bind=engine)  # startup
    yield
    engine.dispose()                              # shutdown — ferme le pool
```

Sans `lifespan`, `create_all` tournait au niveau module — avant qu'uvicorn soit prêt et avant que la DB soit up. Résultat : crash au démarrage si postgres n'était pas encore prêt.

**`get_db()`** avec `yield` est le pattern FastAPI pour injecter une session DB dans les routes :

```python
def get_db():
    db = SessionLocal()
    try:
        yield db      # injecté dans la route via Depends()
    finally:
        db.close()    # toujours exécuté, même si erreur
```

**`Depends()`** et `Annotated` = injection de dépendances. FastAPI appelle `get_db()` automatiquement pour chaque route qui déclare `db: db_dependency`.

---

## `api.py`

L'API 42 utilise **OAuth2**. Pour un sync automatique sans interaction browser, on utilise le flow **`client_credentials`** — token d'application, pas d'utilisateur.

Différence entre les deux flows :
- `authorization_code` : nécessite un browser + consentement utilisateur → donne accès à `/v2/me`
- `client_credentials` : POST direct avec `client_id` + `client_secret` → donne accès aux endpoints publics comme `/v2/users/{login}`

Le token expire après 7200 secondes. On stocke le timestamp d'expiration et on renouvelle automatiquement :

```python
now = datetime.now().timestamp()
if not self.token or now >= self.token_expires_at:
    # fetch nouveau token
    self.token_expires_at = now + expires_in
```

`r.raise_for_status()` lève une exception si l'API retourne 4xx/5xx — pas de fallback silencieux, conformément aux conventions du projet.

---

## `sync.py`

**Upsert** = UPDATE si la row existe déjà + INSERT sinon. Pattern standard pour les syncs :

```python
existing = db.query(Model).filter_by(slug=slug).first()
if existing:
    for key, value in mapped.items():
        setattr(existing, key, value)  # update dynamique sans lister les colonnes
else:
    db.add(Model(**mapped))
db.commit()
```

`setattr(obj, key, value)` permet de mettre à jour les attributs d'un objet SQLAlchemy dynamiquement depuis un dict — pas besoin de lister chaque colonne manuellement.

**`_map_project`** isole la transformation API → DB. L'API 42 retourne ses propres statuts (`"creating_group"`, `"finished"`) — on les mappe vers les valeurs de notre enum interne avant de toucher la DB.

Les dates arrivent en string ISO depuis l'API. SQLAlchemy attend des objets `datetime` Python :
```python
datetime.fromisoformat("2026-05-26T13:14:19.685Z".replace("Z", "+00:00"))
```

---

## `docker-compose.yml`

**`depends_on` avec `condition: service_healthy`** garantit que FastAPI démarre seulement quand PostgreSQL accepte des connexions — pas juste quand le container est lancé. Sans ça, FastAPI crashe au démarrage parce que postgres n'est pas encore prêt.

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
  interval: 10s
  retries: 5
  start_period: 30s
```

`$$` dans le healthcheck échappe le `$` — sans ça, Compose essaie d'interpoler la variable lui-même avant de la passer au container.

**`env_file`** injecte les variables du `.env` dans le container. Sans cette ligne, `os.getenv()` retourne `None` même si le `.env` existe sur la machine host — les variables ne sont pas automatiquement transmises aux containers.

---

## Variables d'environnement

```env
POSTGRES_USER=
POSTGRES_PASSWORD=
PGADMIN_EMAIL=
HOST=db
FT_USER=smonte-e
FT_CLIENT_ID=
FT_CLIENT_SECRET=
```

