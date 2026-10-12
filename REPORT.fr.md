# Recensement du registre MCP officiel — premier passage

**12 octobre 2026** — jeu de données gelé à **36 200 serveurs** (version la plus récente de chacun),
extrait du registre officiel `registry.modelcontextprotocol.io` (version 1.8.1).
Collecte reproductible en deux commandes, sans dépendance hors bibliothèque standard.

Le registre est public, l'API est publique, et **personne n'avait publié ce qu'il contient
réellement**. Ce document le mesure. Rien n'est exécuté, rien n'est contacté : tout est lu dans ce
que le registre déclare.

---

## 1. Le résultat principal : le registre n'est pas une population, c'en est deux

J'ai d'abord calculé un chiffre global, et **il ne veut rien dire**. La raison est mécanique : le
registre est paginé dans l'ordre alphabétique des espaces de nommage. Un passage partiel est donc un
**préfixe de l'alphabet**, pas un échantillon aléatoire. Le taux de serveurs « opaques » — appelables
mais sans code source ni paquet publié — dépend alors de l'endroit où le robot s'est arrêté.

Je peux le **prouver** au lieu de l'affirmer, parce que j'ai gelé le jeu de données deux fois :

| Gel | serveurs | opaque global | `com.*` opaque | `io.*` opaque |
|---|---:|---:|---:|---:|
| 19 500 | **41,0 %** | 60,3 % | 14,1 % |
| 36 200 | **24,6 %** | 60,3 % | 8,1 % |

Même registre, même code, même question. Le chiffre global a chuté de 16 points **parce que le robot
a avancé dans l'alphabet** et ramassé davantage de serveurs `io.github.*`. Les espaces de nommage
déjà terminés, eux, n'ont pas bougé d'un dixième de point. **Le chiffre global mesure l'avancement de
la collecte, pas le registre.**

Ventilé, l'écart est énorme :

| Espace de nommage | serveurs | publie un dépôt | publie un paquet | expose un endpoint | **opaque** |
|---|---:|---:|---:|---:|---:|
| `io.*` (dont `io.github.*`) | 24 270 | 90,0 % | 53,2 % | 49,8 % | **8,1 %** |
| `com.*` | 6 856 | 37,2 % | 14,3 % | 90,4 % | **60,3 %** |
| `ai.*` | 1 878 | 46,2 % | 14,7 % | 89,9 % | **51,6 %** |
| `dev.*` | 821 | 43,7 % | 21,6 % | 85,9 % | **52,0 %** |
| `app.*` | 781 | 42,8 % | 8,1 % | 94,9 % | **55,4 %** |
| `co.*` | 226 | 29,2 % | 12,8 % | 94,2 % | **67,7 %** |
| `eu.*` | 179 | 75,4 % | 57,5 % | 45,3 % | **24,0 %** |
| `de.*` | 111 | 13,5 % | 4,5 % | 97,3 % | **85,6 %** |
| `fr.*` | 86 | 17,4 % | 2,3 % | 98,8 % | **81,4 %** |
| `guide.*` | 43 | 95,3 % | 0,0 % | 100,0 % | **4,7 %** |

Sur les 18 espaces de nommage comptant au moins 30 serveurs, le taux d'opacité va de **4,7 % à
85,6 %** — un facteur 18.

**La lecture.** Le registre héberge deux choses différentes sous la même API :

- les serveurs **`io.github.*`**, c'est-à-dire du code hébergé sur GitHub, publié en paquet, versionné.
  90 % donnent un dépôt, 53 % un paquet installable. Ce sont des bibliothèques.
- les serveurs **`com.*`, `ai.*`, `app.*` et les suffixes nationaux**, c'est-à-dire des services
  commerciaux. ~90 % exposent une URL et rien d'autre. Ce sont des points de terminaison.

Ce ne sont pas les mêmes objets, et ils ne posent pas les mêmes questions. Une bibliothèque peut être
lue, épinglée, comparée à sa source. Un point de terminaison commercial ne peut qu'être appelé.

**Conséquence pratique :** l'énoncé utilisable est **« dans les espaces commerciaux et nationaux, 50 à
86 % des serveurs sont opaques ; dans `io.github.*`, 8 % »**. Toute publication qui cite une moyenne
unique sur ce registre se trompe, y compris la mienne si je l'avais publiée telle quelle.

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

Après retrait des motifs fautifs, le détecteur renvoie **0 sur 36 200**.

**Ce n'est pas un échec à cacher, c'est le résultat.** Le champ `description` du registre est écrit par
l'éditeur, non vérifié, et il ne sépare pas un serveur malveillant d'un serveur légitime. Quiconque
annonce détecter des serveurs MCP dangereux en lisant leurs descriptions décrit un détecteur qui, ici,
renvoie du bruit. Les motifs rejetés restent **visibles dans le code** (`REJECTED_PATTERNS`) et comptés
dans `summary-latest.json` (`rejected_pattern_raw_hits`), pour que le taux de faux positifs reste
vérifiable au lieu d'être effacé.

---

## 3. Le signal qui n'existe pas

J'attendais de trouver des serveurs enregistrés sous un nom nu, sans espace de nommage inverse DNS —
un signe d'amateurisme, et donc de risque. **Résultat : 0 sur 36 200. Aucune exception.**

Le registre impose le préfixe. Un signal sans variance n'est pas un signal : la colonne est calculée,
publiée, et ne discrimine rien. Je la garde pour que ce soit vérifiable, pas pour en tirer une
conclusion.

---

## 4. Les chiffres annexes

| Mesure | Valeur |
|---|---|
| serveurs (version la plus récente) | 36 200 |
| sans dépôt public | 9 656 (26,7 %) |
| sans paquet publié | 21 571 (59,6 %) |
| exposant un endpoint distant | 22 855 (63,1 %) |
| **opaques** (endpoint, ni dépôt, ni paquet) | **8 893 (24,6 %)** |
| paquets non épinglés | 1 317 (3,6 %) |
| descriptions à formulation d'injection | **0** |
| noms sans espace de nommage | **0** |

**Transports** : `streamable-http` 22 169 · `sse` 929. Le transport SSE historique est en voie
d'extinction — moins de 4 % du parc.

**Registres de paquets** : npm 9 458 · pypi 3 850 · oci 921 · mcpb 818 · nuget 133 · cargo 63.
L'écosystème est massivement JavaScript et Python ; les paquets MCPB (bundles natifs) existent mais
restent marginaux.

**Churn de versions** (passage complet, 58 100 entrées, encore partiel) : un serveur,
`ai.bowmark/bowmark`, apparaît **exactement 1 000 fois**. Le chiffre est rond, donc je ne l'affirme
pas — soit une publication automatisée à chaque commit, soit un plafond côté registre. À vérifier
avant de le citer. Les suivants sont 516 (`com.linkbreakers/mcp`), 350, 258, 242, 214.

---

## 5. Un bug à signaler : la collecte est morte deux fois

Les deux passages ont planté en cours de route sur `http.client.RemoteDisconnected` — le registre qui
ferme la connexion en pleine réponse — après 1 h 16 et 1 h 37 de travail. La boucle de réessai
attrapait `urllib.error.URLError`, mais `RemoteDisconnected` hérite de `ConnectionResetError`, qui est
un **frère** de `URLError`, pas un enfant. L'échec le plus probable d'une longue collecte était donc
précisément l'exception que la boucle n'attrapait pas.

Le correctif : attraper `OSError` (qui couvre `URLError`, `ConnectionResetError` et les timeouts de
socket) plus `http.client.HTTPException`, et augmenter le nombre de réessais. Un bug de code arrête
toujours la collecte ; une connexion coupée, non. Si vous paginez ce registre, c'est la ligne qui vous
coûtera une heure et demie.

---

## 6. Ce qu'il ne faut pas conclure

- **Ce n'est pas un recensement exhaustif.** Le passage s'est arrêté à 36 200 serveurs, à l'intérieur
  de `io.github.*`. Le décompte est une **borne inférieure**.
- **Un serveur opaque n'est pas malveillant, et un serveur avec dépôt n'est pas sûr.** Ce recensement
  mesure ce qui est **inspectable**, ce qui n'est pas la même question que ce qui est **sûr**.
- **`isLatest` est une déclaration du registre**, prise au pied de la lettre.
- **Le registre n'est pas la population.** Il contient ce qui a été publié à cet index, pas ce qui
  existe. Un serveur jamais enregistré, ou retiré, est invisible ici.
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
