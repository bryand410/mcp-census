# Recensement du registre MCP officiel

**12 octobre 2026** — passage **complet** : **42 399 serveurs**, la version la plus récente de chacun,
lus depuis le registre officiel `registry.modelcontextprotocol.io` (version 1.8.1). Le curseur de
pagination est allé jusqu'au bout : c'est le registre entier, pas un échantillon.
Reproductible en deux commandes, sans dépendance hors bibliothèque standard.

Le registre est public, l'API est publique, et **personne n'avait publié ce qu'il contient
réellement**. Ce document le mesure. Rien n'est exécuté, rien n'est contacté : tout est lu dans ce
que le registre déclare.

---

## 1. Le résultat principal : le registre n'est pas une population, c'en est deux

J'ai d'abord calculé un chiffre global. Il n'est plus faux maintenant que le passage est complet —
26,0 % du registre est opaque — mais c'est **le chiffre le moins informatif de ce document**, parce
qu'il fait la moyenne de deux populations qui n'ont presque rien en commun.

Je peux montrer pourquoi, parce que j'ai gelé le jeu de données trois fois pendant la collecte :

| Gel | serveurs | opaque global | `com.*` | `io.*` |
|---|---:|---:|---:|---:|
| partiel | 19 500 | **41,0 %** | 60,3 % | 14,1 % |
| partiel | 36 200 | **24,6 %** | 60,3 % | 8,1 % |
| **complet** | **42 399** | **26,0 %** | 60,3 % | 8,7 % |

Même registre, même code, même question. Le chiffre global a fait **16 points vers le bas, puis est
remonté**, parce que le robot a avancé dans l'alphabet et ramassé d'autres espaces de nommage.
**Chaque espace de nommage déjà terminé est resté identique à la décimale près** — `com.*` est à
60,3 % dans les trois.

Autrement dit : si j'avais publié après le premier gel, j'aurais annoncé 41 %. Après le deuxième,
24,6 %. Les deux auraient été faux, et affirmés avec assurance. C'est le piège des jeux de données
paginés : la clé de tri n'est pas aléatoire, donc un passage partiel est un **préfixe**, pas un
échantillon.

Ventilé, l'écart est énorme :

| Espace de nommage | serveurs | publie un dépôt | publie un paquet | expose un endpoint | **opaque** |
|---|---:|---:|---:|---:|---:|
| `io.*` (dont `io.github.*`) | 28 029 | 89,2 % | 53,4 % | 50,0 % | **8,7 %** |
| `com.*` | 6 856 | 37,2 % | 14,3 % | 90,4 % | **60,3 %** |
| `ai.*` | 1 878 | 46,2 % | 14,7 % | 89,9 % | **51,6 %** |
| `dev.*` | 821 | 43,7 % | 21,6 % | 85,9 % | **52,0 %** |
| `app.*` | 781 | 42,8 % | 8,1 % | 94,9 % | **55,4 %** |
| `uk.*` | 319 | 10,7 % | 3,1 % | 97,2 % | **89,3 %** |
| `org.*` | 229 | 40,6 % | 14,0 % | 86,9 % | **57,2 %** |
| `co.*` | 226 | 29,2 % | 12,8 % | 94,2 % | **67,7 %** |
| `net.*` | 223 | 27,4 % | 13,9 % | 88,3 % | **65,5 %** |
| `eu.*` | 179 | 75,4 % | 57,5 % | 45,3 % | **24,0 %** |
| `de.*` | 111 | 13,5 % | 4,5 % | 97,3 % | **85,6 %** |
| `live.*` | 92 | 7,6 % | 1,1 % | 100,0 % | **91,3 %** |
| `fr.*` | 86 | 17,4 % | 2,3 % | 98,8 % | **81,4 %** |
| `guide.*` | 43 | 95,3 % | 0,0 % | 100,0 % | **4,7 %** |

Sur les 36 espaces de nommage comptant au moins 30 serveurs, le taux d'opacité va de **4,7 % à
91,3 %** — un facteur **19**.

**La lecture.** Le registre héberge deux choses différentes sous la même API :

- les serveurs **`io.github.*`**, c'est-à-dire du code hébergé sur GitHub, publié en paquet, versionné.
  89 % donnent un dépôt, 53 % un paquet installable. Ce sont des bibliothèques.
- les serveurs **`com.*`, `ai.*`, `app.*`, `uk.*`, `live.*` et les suffixes nationaux**, c'est-à-dire
  des services commerciaux. ~90 % exposent une URL et rien d'autre. Ce sont des points de terminaison.

Ce ne sont pas les mêmes objets, et ils ne posent pas les mêmes questions. Une bibliothèque peut être
lue, épinglée, comparée à sa source. Un point de terminaison commercial ne peut qu'être appelé.
`live.*` — 100 % exposent un endpoint, 7,6 % donnent un dépôt, 91,3 % opaques — en est la forme la
plus pure.

**Conséquence pratique :** l'énoncé utilisable est **« dans les espaces commerciaux et nationaux, 50 à
91 % des serveurs sont opaques ; dans `io.github.*`, 8,7 % »**. Le 26,0 % à l'échelle du registre est
arithmétiquement exact et pratiquement inutile, parce qu'il dépend entièrement du nombre de
bibliothèques GitHub enregistrées ce mois-là.

---

## 2. Le détecteur qui ne marche pas

J'avais écrit un détecteur d'injection de prompt qui lisait les descriptions, avec notamment
`system prompt` et `you are now` parmi les motifs. Il a trouvé **9 serveurs**. Je les ai lus un par un.

**Les 9 sont des faux positifs.** Taux de faux positifs : **100 %**.

| Serveur | Description |
|---|---|
| `app.web.mindset-502113/mindset` | « Semantic search over MINDSET's brand strategy topic database, plus its system prompt. » |
| `com.runningunattended/agent-lint` | « Checks CLAUDE.md, AGENTS.md or a system prompt for 12 safeguards unattended agents need. » |
| `io.gildara/mcp-server` | « Operating contracts for AI agents. Structured instructions compiled into system prompts. » |
| `io.github.Evozim/rules-gen` | « Automated .cursorrules and system prompt generator. » |
| `io.github.Gildaraio/mcp-server` | (même éditeur que le précédent) |
| `io.github.a-church-ai/magnifica-family` | « Catholic AI compass: system prompts from Pope Leo XIV's encyclical Magnifica Humanitas. » |
| `io.github.izworskic/openclaw-registry` | « Search and retrieve agent instruction files: system prompts, skills, workflows, and safety filters. » |
| `io.github.jmshinhwa/ai-act-article-50-audit` | « Finds the AI call sites, generation code and system prompts that trigger EU AI Act Article 50 disclosure… » |
| `io.github.jmshinhwa/ai-companion-safety-lint` | « Reads your companion chatbot's system prompt against California SB 243, New York GBL Article 47… » |

La raison est simple et elle est définitive : **dans ce domaine, « system prompt » est du vocabulaire
ordinaire**. La moitié de ces serveurs servent précisément à *générer*, *compiler* ou *auditer* un
system prompt. Le mot est dans la fiche produit parce que c'est le produit.

**Et l'échec est pire que du bruit.** Trois des neuf sont des outils de conformité et de sécurité :
l'un vérifie un chatbot contre l'**article 50 de l'AI Act européen**, l'autre contre le **California
SB 243 et le New York GBL Article 47**. Un détecteur qui signale les gens qui écrivent les contrôles
de conformité ne renvoie pas seulement du bruit : **il pointe exactement la mauvaise population**.
C'est le pire mode de défaillance possible pour un détecteur de sécurité.

Après retrait des motifs fautifs, le détecteur renvoie **0 sur 42 399**.

**Ce n'est pas un échec à cacher, c'est le résultat.** Le champ `description` du registre est écrit par
l'éditeur, non vérifié, et il ne sépare pas un serveur malveillant d'un serveur légitime. Quiconque
annonce détecter des serveurs MCP dangereux en lisant leurs descriptions décrit un détecteur qui, ici,
renvoie du bruit. Les motifs rejetés restent **visibles dans le code** (`REJECTED_PATTERNS`) et comptés
dans `summary-latest.json` (`rejected_pattern_raw_hits`), pour que le taux de faux positifs reste
vérifiable au lieu d'être effacé.

---

## 3. Le signal qui n'existe pas

J'attendais de trouver des serveurs enregistrés sous un nom nu, sans espace de nommage inverse DNS —
un signe d'amateurisme, et donc de risque. **Résultat : 0 sur 42 399. Aucune exception.**

Le registre impose le préfixe. Un signal sans variance n'est pas un signal : la colonne est calculée,
publiée, et ne discrimine rien. Je la garde pour que ce soit vérifiable, pas pour en tirer une
conclusion.

---

## 4. Les chiffres annexes

| Mesure | Valeur |
|---|---|
| serveurs (version la plus récente) | 42 399 |
| sans dépôt public | 11 951 (28,2 %) |
| sans paquet publié | 25 435 (60,0 %) |
| exposant un endpoint distant | 27 008 (63,7 %) |
| **opaques** (endpoint, ni dépôt, ni paquet) | **11 013 (26,0 %)** |
| paquets non épinglés | 1 549 (3,7 %) |
| descriptions à formulation d'injection | **0** |
| noms sans espace de nommage | **0** |

**Transports** : `streamable-http` 26 271 · `sse` 1 081. Le transport SSE historique est en voie
d'extinction — moins de 4 % du parc.

**Registres de paquets** : npm 10 882 · pypi 4 371 · mcpb 1 101 · oci 1 091 · nuget 146 · cargo 76.
L'écosystème est massivement JavaScript et Python. Les paquets MCPB (bundles natifs) viennent de
dépasser OCI — à surveiller, parce qu'un bundle natif n'est pas une installation en bac à sable.

---

## 5. Un bug à signaler : la collecte est morte deux fois

Les deux passages ont planté en cours de route sur `http.client.RemoteDisconnected` — le registre qui
ferme la connexion en pleine réponse — après 1 h 16 et 1 h 37 de travail. La boucle de réessai
attrapait `urllib.error.URLError`, mais `RemoteDisconnected` hérite de `ConnectionResetError`, qui est
un **frère** de `URLError`, pas un enfant. L'échec le plus probable d'une longue collecte était donc
précisément l'exception que la boucle n'attrapait pas.

Le correctif : attraper `OSError` (qui couvre `URLError`, `ConnectionResetError` et les timeouts de
socket) plus `http.client.HTTPException`. Sur la reprise, la collecte a traversé un `502 Bad Gateway`
et un `SSL: UNEXPECTED_EOF_WHILE_READING` sans perdre le passage. Un bug de code arrête toujours la
collecte ; une connexion coupée, non. Si vous paginez ce registre, c'est la ligne qui vous coûtera
une heure et demie.

---

## 6. Ce qu'il ne faut pas conclure

- **Un index n'est pas une population.** Ceci compte ce qui a été publié à cet index le 12 octobre
  2026, pas ce qui existe. Un serveur jamais enregistré, ou retiré, est invisible ici.
- **Ce n'est pas un instantané.** Le passage complet a pris environ deux heures sur deux exécutions.
  Un serveur publié pendant cette fenêtre peut être manqué ou compté deux fois à la frontière.
- **Un serveur opaque n'est pas malveillant, et un serveur avec dépôt n'est pas sûr.** Ce recensement
  mesure ce qui est **inspectable**, ce qui n'est pas la même question que ce qui est **sûr**.
- **`isLatest` est une déclaration du registre**, prise au pied de la lettre.
- **Aucune exécution, aucun scan intrusif, aucun appel aux serveurs.** Uniquement de la lecture d'API.

---

## 7. Reproduire

```bash
python crawl.py --out data/registry-latest.jsonl --state data/cursor-latest.txt --version latest
python analyze.py --raw data/registry-latest.jsonl \
    --csv data/servers-latest.csv --json data/summary-latest.json
```

`servers-latest.csv` : une ligne par serveur, une colonne par signal. `summary-latest.json` : les
agrégats, y compris le tableau par espace de nommage et les motifs rejetés.

**Détail de méthode qui a débloqué la collecte :** `?version=latest` est évalué **côté serveur**.
La liste non filtrée met **60 s** par page une fois le curseur profond ; la même question filtrée met
**1,6 s**. Le registre sait filtrer, il ne faut pas le refaire côté client.

Dépôt : https://github.com/bryand410/mcp-census
