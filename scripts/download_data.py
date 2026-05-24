#!/usr/bin/env python3
"""
Télécharge et nettoie toutes les données électorales de Strasbourg
depuis data.strasbourg.eu et génère des fichiers JSON dans ../data/

Usage :
    python3 download_data.py

Durée estimée : 2-5 minutes selon la connexion.
"""

import json, os, urllib.request, urllib.parse

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
API_BASE   = 'https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets'

ELECTIONS = [
    # Municipales
    {'id':'muni_2014_t1','cat':'municipales','label':'2014','tour':1,'fmt':'v3',
     'dataset':'resultats-du-premier-tour-des-elections-municipales-2014-de-la-ville-strasbourg'},
    {'id':'muni_2014_t2','cat':'municipales','label':'2014','tour':2,'fmt':'v3',
     'dataset':'resultats-du-second-tour-des-elections-municipales-2014-de-la-ville-de-strasbour'},
    {'id':'muni_2020_t1','cat':'municipales','label':'2020','tour':1,'fmt':'v2',
     'dataset':'elections-municipales-2020-1er-tour'},
    {'id':'muni_2020_t2','cat':'municipales','label':'2020','tour':2,'fmt':'v2',
     'dataset':'elections-municipales-2020-2nd-tour'},
    {'id':'muni_2026_t1','cat':'municipales','label':'2026','tour':1,'fmt':'v1',
     'dataset':'resultats-du-premier-tour-des-elections-municipales-2026-version-detaillee'},
    {'id':'muni_2026_t2','cat':'municipales','label':'2026','tour':2,'fmt':'v1',
     'dataset':'resultats-du-second-tour-des-elections-municipales-2026-version-detaillee'},
    # Législatives
    {'id':'legis_2017_t1','cat':'legislatives','label':'2017','tour':1,'fmt':'v3',
     'dataset':'resultats-du-premier-tour-des-elections-legislatives-2017-circonscription-1'},
    {'id':'legis_2017_t2','cat':'legislatives','label':'2017','tour':2,'fmt':'v3',
     'dataset':'resultats-du-second-tour-des-elections-legistatives-2017-dans-la-premiere-circon'},
    {'id':'legis_2022_t1','cat':'legislatives','label':'2022','tour':1,'fmt':'v1',
     'dataset':'resultats-du-premier-tour-des-elections-legislatives-2022-version-detaillee'},
    {'id':'legis_2022_t2','cat':'legislatives','label':'2022','tour':2,'fmt':'v1',
     'dataset':'resultats-du-second-tour-des-elections-legislatives-2022-version-detaillee'},
    {'id':'legis_2024_t1','cat':'legislatives','label':'2024','tour':1,'fmt':'v1',
     'dataset':'resultats-du-premier-tour-des-elections-legislatives-2024-version-detaillee'},
    {'id':'legis_2024_t2','cat':'legislatives','label':'2024','tour':2,'fmt':'v1',
     'dataset':'resultats-du-second-tour-des-elections-legislatives-2024-version-detaillee'},
    # Présidentielles
    {'id':'pres_2017_t1','cat':'presidentielles','label':'2017','tour':1,'fmt':'v1',
     'dataset':'resultats-du-premier-tour-de-l-election-presidentielle-2017-version-detaillee'},
    {'id':'pres_2017_t2','cat':'presidentielles','label':'2017','tour':2,'fmt':'v1',
     'dataset':'resultats-du-second-tour-de-l-election-presidentielle-2017-version-detaillee'},
    {'id':'pres_2022_t1','cat':'presidentielles','label':'2022','tour':1,'fmt':'v1',
     'dataset':'resultats-du-premier-tour-de-l-election-presidentielle-2022-version-detaillee'},
    {'id':'pres_2022_t2','cat':'presidentielles','label':'2022','tour':2,'fmt':'v1',
     'dataset':'resultats-du-second-tour-de-l-election-presidentielle-2022-version-detaillee'},
    # Régionales
    {'id':'regio_2021_t1','cat':'regionales','label':'2021','tour':1,'fmt':'v1',
     'dataset':'resultats-du-premier-tour-des-elections-regionales-2021-version-detaillee'},
    {'id':'regio_2021_t2','cat':'regionales','label':'2021','tour':2,'fmt':'v1',
     'dataset':'resultats-du-second-tour-des-elections-regionales-2021-version-detaillee'},
    # Départementales
    {'id':'dept_2021_t1','cat':'departementales','label':'2021','tour':1,'fmt':'v1',
     'dataset':'resultats-du-premier-tour-des-elections-departementales-2021-version-detaillee'},
    {'id':'dept_2021_t2','cat':'departementales','label':'2021','tour':2,'fmt':'v1',
     'dataset':'resultats-du-second-tour-des-elections-departementales-2021-version-detaillee'},
    # Européennes
    {'id':'euro_2024_t1','cat':'europeennes','label':'2024','tour':1,'fmt':'v1',
     'dataset':'resultats-des-elections-europeennes-2024-version-detaillee'},
]

V3_META = {'bureaux','inscrits','abstentions','votants','blancs','nuls','exprimes','emarges','participation'}
V3_IGNORE = {
    'geo_shape','geo_point_2d','geo_point_2d_lat','geo_point_2d_lon',
    'total_nb_blancs_canton','total_nb_inscrits_canton','total_nb_nuls_canton',
    'total_nb_suffrages_exprimes_canton','total_nb_votants_canton',
    'total_nb_blancs_tour','total_nb_inscrits_tour','total_nb_nuls_tour',
    'total_nb_suffrages_exprimes_tour','total_nb_votants_tour',
    'nb_bureaux','nb_bureaux_canton','nb_bureaux_depouilles_canton',
    'nb_bureaux_depouilles_tour','traitement_date','traitement_heure',
    'cod_scrutin','millesime','cod_comm_ext','cod_lieu','cod_postal',
    'lib_adr1','libelle_secteur','cod_lib_bureau','nom','bur_dist',
    'cod_circons','cod_canton','ind_complet','json_featuretype','rang',
    'num_ordre','num_liste','num_tour','nb_emarge','nb_enveloppe',
    'nb_sans_enveloppe','nb_procurat','cod_parti','lib_parti',
    'lib_liste','cod_liste','nom_candidat1_liste',
}

def n(v): return int(v or 0)

def fetch_all(dataset):
    rows, offset, total = [], 0, float('inf')
    while offset < total:
        qs = urllib.parse.urlencode({'limit':100,'offset':offset})
        url = f'{API_BASE}/{dataset}/records?{qs}'
        with urllib.request.urlopen(url, timeout=30) as r:
            d = json.loads(r.read())
        total = d['total_count']
        rows.extend(d['results'])
        offset += len(d['results'])
        if not d['results']: break
        print(f'    {offset}/{total}  ', end='\r')
    print()
    return rows

def v1(rows):
    bvs = {}
    for r in rows:
        bid = str(r.get('cod_bureau','?'))
        if bid not in bvs:
            bvs[bid] = {'label':r.get('lib_bureau',f'Bureau {bid}'),
                        'inscrits':n(r.get('nb_inscrit')), 'votants':n(r.get('nb_votant')),
                        'blancs':n(r.get('nb_blanc')),     'nuls':n(r.get('nb_nul')),
                        'exprimes':n(r.get('nb_suffrage_exprime')), 'cands':[]}
        lib = r.get('lib_liste_affichee') or ''
        voix = n(r.get('nb_voix'))
        if lib: bvs[bid]['cands'].append({'nom':lib,'voix':voix})
    for bv in bvs.values(): bv['cands'].sort(key=lambda x:x['voix'],reverse=True)
    return bvs

def v2(rows):
    bvs = {}
    for r in rows:
        bid = str(r.get('cod_bureau','?'))
        if bid not in bvs:
            bvs[bid] = {'label':r.get('lib_bureau') or r.get('nom',f'Bureau {bid}'),
                        'inscrits':n(r.get('nb_inscrit')), 'votants':n(r.get('nb_votant')),
                        'blancs':n(r.get('nb_blanc')),     'nuls':n(r.get('nb_nul')),
                        'exprimes':n(r.get('nb_suffrage_exprime')), 'cands':[]}
        lib = r.get('lib_liste') or r.get('lib_liste_affichee') or ''
        voix = n(r.get('nb_voix'))
        if lib: bvs[bid]['cands'].append({'nom':lib,'voix':voix})
    for bv in bvs.values(): bv['cands'].sort(key=lambda x:x['voix'],reverse=True)
    return bvs

def v3(rows):
    if not rows: return {}
    cands_cols = [k for k in rows[0] if k not in V3_META and k not in V3_IGNORE]
    bvs = {}
    for r in rows:
        raw = r.get('bureaux') or r.get('cod_lib_bureau','?')
        parts = raw.split(' - ',1)
        bid = parts[0].strip().zfill(4)
        label = parts[1].strip() if len(parts)>1 else raw
        bvs[bid] = {
            'label': f'{bid} — {label}',
            'inscrits': n(r.get('inscrits')), 'votants': n(r.get('votants')),
            'blancs':   n(r.get('blancs')),   'nuls':    n(r.get('nuls')),
            'exprimes': n(r.get('exprimes')),
            'cands': sorted(
                [{'nom':k.replace('_',' ').title(),'voix':n(r.get(k))}
                 for k in cands_cols if n(r.get(k))>0],
                key=lambda x:x['voix'], reverse=True),
        }
    return bvs

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print('=== Téléchargement données électorales Strasbourg ===\n')
    total_ko = 0
    for elec in ELECTIONS:
        print(f"→ {elec['id']}")
        try:
            rows = fetch_all(elec['dataset'])
            print(f'   {len(rows)} lignes')
            bvs = v1(rows) if elec['fmt']=='v1' else v2(rows) if elec['fmt']=='v2' else v3(rows)
            out = {'id':elec['id'],'cat':elec['cat'],'label':elec['label'],
                   'tour':elec['tour'],'bureaux':bvs}
            path = os.path.join(OUTPUT_DIR, f"{elec['id']}.json")
            with open(path,'w',encoding='utf-8') as f:
                json.dump(out, f, ensure_ascii=False, separators=(',',':'))
            ko = os.path.getsize(path)/1024
            total_ko += ko
            print(f'   ✓ {len(bvs)} bureaux — {ko:.0f} Ko\n')
        except Exception as e:
            print(f'   ✗ Erreur : {e}\n')
    print(f'=== Terminé — Total : {total_ko/1024:.1f} Mo ===')

if __name__ == '__main__':
    main()
