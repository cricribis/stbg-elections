# 🗳️ Résultats électoraux — Strasbourg

Webapp affichant les résultats électoraux de Strasbourg par bureau de vote.  
Données issues du portail open data de la Ville de Strasbourg.

## Élections couvertes

| Catégorie | Années |
|---|---|
| Municipales | 2014 · 2020 · 2026 (T1 et T2) |
| Législatives | 2017 · 2022 · 2024 (T1 et T2) |
| Présidentielles | 2017 · 2022 (T1 et T2) |
| Régionales | 2021 (T1 et T2) |
| Départementales | 2021 (T1 et T2) |
| Européennes | 2024 |

## Structure du projet

```
elections-stras/
├── index.html          ← La webapp (ouvrir dans un navigateur)
├── data/               ← Fichiers JSON générés par le script
│   ├── muni_2026_t1.json
│   ├── muni_2026_t2.json
│   └── … (21 fichiers au total)
├── scripts/
│   └── download_data.py  ← Script de téléchargement
└── README.md
```

## Installation

### 1. Télécharger les données (une seule fois)

Python 3 doit être installé. Aucune dépendance externe nécessaire.

```bash
cd scripts
python3 download_data.py
```

Durée : 2 à 5 minutes. Les fichiers JSON sont générés dans `data/`.

### 2. Lancer la webapp en local

```bash
# Depuis le dossier racine du projet
python3 -m http.server 8000
```

Ouvrir http://localhost:8000 dans le navigateur.

### 3. Publier sur GitHub Pages

```bash
git init
git add .
git commit -m "Résultats électoraux Strasbourg"
git remote add origin https://github.com/VOTRE-LOGIN/elections-strasbourg.git
git push -u origin main
```

Puis dans GitHub → Settings → Pages → Source : `main / root`.  
La webapp sera accessible à `https://VOTRE-LOGIN.github.io/elections-strasbourg`

> **Note :** Sur GitHub Pages, les fichiers JSON sont servis directement — pas besoin de serveur local.

## Sources

Données : [data.strasbourg.eu](https://data.strasbourg.eu) — Ville et Eurométropole de Strasbourg  
Licence : Licence Ouverte / Open Licence 2.0
