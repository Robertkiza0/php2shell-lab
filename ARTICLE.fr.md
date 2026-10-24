# PHP2Shell : la faille critique qui ébranle le web

*Par Lungwe Kiza Robert — analyste en cybersécurité, VertaGuard. À jour au 24 octobre 2026.*

PHP2Shell regroupe deux vulnérabilités critiques (CVE-2026-109618 et
CVE-2026-109619), corrigées le 21 octobre 2026, qui permettent à un attaquant
d'exécuter du code à distance, sans authentification, sur la grande majorité des
serveurs web utilisant PHP.

## Résumé

Le 21 octobre 2026, l'équipe de développement de PHP a publié des correctifs
d'urgence pour deux failles critiques, surnommées PHP2Shell. Toutes deux sont
notées 9,2 sur 10 (CVSS v4.0) et permettent à un attaquant non authentifié
d'exécuter du code à distance sur un serveur web. Presque toutes les versions de
PHP de la dernière décennie sont concernées, de la 5.4 à la 8.x. Comme des
détails ont fuité avant la publication du correctif, la mise à jour doit être
traitée comme urgente.

Le message de cet article est simple : il ne s'agit pas d'exploiter la faille,
mais de savoir la détecter et la corriger. C'est exactement ce que les
entreprises attendent d'un analyste en cybersécurité aujourd'hui.

## Qu'est-ce que PHP2Shell ?

PHP2Shell désigne deux vulnérabilités distinctes mais liées, situées dans le
cœur de l'interpréteur PHP :

- **CVE-2026-109618** — exécution de code via corruption mémoire lors d'un
  manque de mémoire (OOM). La gestion du dépassement de mémoire peut interrompre
  PHP alors que les données internes d'une requête ne sont que partiellement
  initialisées.
- **CVE-2026-109619** — exécution de code via un état global obsolète. Des
  données internes appartenant à une requête peuvent survivre après la
  libération de la mémoire qui les contenait.

Les deux failles ont été découvertes par l'équipe de recherche de Wiz, avec
l'aide d'outils d'IA. C'est un point notable : il s'agit de l'un des premiers
cas marquants de découverte de vulnérabilité majeure assistée par
l'intelligence artificielle.

**Chronologie :**

1. **20 octobre 2026** — des détails des deux failles fuitent en ligne avant la
   divulgation coordonnée.
2. **21 octobre 2026, 14h00 UTC** — PHP publie les versions corrigées et l'avis
   de sécurité, un jour plus tôt que prévu à cause de la fuite.
3. **Dans les heures qui suivent** — hébergeurs, Cloudflare et éditeurs
   déploient des règles de protection en urgence.

## Pourquoi c'est critique

Trois caractéristiques rendent PHP2Shell particulièrement dangereux :

- **Exécution de code à distance (RCE).** Un attaquant peut faire exécuter ses
  propres commandes par le serveur. C'est, en pratique, une prise de contrôle du
  site.
- **Sans authentification.** Aucune connexion ni aucun compte n'est nécessaire :
  une simple requête web suffit.
- **Portée énorme.** Toutes les versions de PHP depuis la 5.4 sont touchées par
  au moins une des deux failles. Selon Wiz, cela représente une grande partie du
  web, dont la majorité des sites WordPress, Drupal et Joomla.

S'ajoute un effet de divulgation anticipée : comme les détails ont fuité avant
le correctif, les attaquants ont eu une longueur d'avance. Un serveur non à jour
aujourd'hui est une cible directe.

## Comment la faille fonctionne

Cette section explique le mécanisme au niveau conceptuel, sans fournir de code
d'exploitation. L'objectif est de comprendre, pas d'attaquer.

**La réutilisation des processus.** Pour des raisons de performance, un serveur
ne lance pas un nouveau processus PHP à chaque visiteur : il garde quelques
« travailleurs » en mémoire et les réutilise d'une requête à l'autre. C'est dans
cette réutilisation que vivent les deux failles.

**Le « use-after-free ».** Chaque requête dispose de sa propre mémoire. À la fin
de la requête, PHP libère cette mémoire pour la requête suivante. Si PHP
conserve un pointeur vers une mémoire déjà libérée, un problème survient.
L'image est celle d'une clé d'hôtel : vous rendez la chambre mais gardez une clé
qui l'ouvre encore ; le client suivant s'installe, et votre ancienne clé ouvre
désormais sa chambre.

**CVE-2026-109618 (manque de mémoire).** PHP impose une limite de mémoire par
requête. Lorsqu'une requête dépasse cette limite, PHP l'arrête immédiatement,
sans terminer ce qu'il faisait. Un attaquant peut déclencher cet arrêt au moment
précis où PHP initialise une nouvelle requête, laissant des données internes à
moitié construites. Le code suivant fait confiance à ces données incomplètes.

**CVE-2026-109619 (état global obsolète).** PHP conserve certaines données
« globales » entre les requêtes. Certaines de ces données pointent encore vers
la mémoire d'une ancienne requête déjà libérée — la clé d'hôtel, de nouveau.
OPcache, le cache qui accélère PHP et qui est activé sur la plupart des serveurs,
fait partie des chemins d'exploitation identifiés.

**L'idée clé à retenir.** Le correctif n'empêche pas PHP de manquer de mémoire :
il garantit que, lorsque cela arrive, PHP ne laisse rien à moitié construit pour
la requête suivante.

## Qui est concerné

Toute installation PHP qui traite des requêtes web est exposée, quelle que soit
la façon dont PHP est servi : PHP-FPM, Apache avec mod_php, php-cgi, FrankenPHP
ou LiteSpeed. Les versions touchées vont de PHP 5.4 jusqu'à la branche 8.x.

| Branche PHP | Version corrigée | Statut |
| --- | --- | --- |
| 8.5 | 8.5.12 | Corrigée |
| 8.4 | 8.4.27 | Corrigée |
| 8.3 | 8.3.36 | Corrigée |
| 8.2 | 8.2.35 | Corrigée |
| 8.1, 8.0, 7.4 | backport source minimal | Fin de vie — à migrer |
| 7.3 et antérieures | aucun correctif | Fin de vie — à migrer |

Les branches 8.1 et antérieures ne sont plus officiellement supportées. PHP a
fourni des backports source minimaux pour 7.4, 8.0 et 8.1 vu la gravité, mais la
vraie solution reste la migration vers une branche supportée (8.2 ou plus).

## Comment se protéger

La priorité absolue est la mise à jour. Passez à PHP 8.5.12, 8.4.27, 8.3.36 ou
8.2.35 selon votre branche. Pour les versions en fin de vie (7.4, 8.0, 8.1),
appliquez le backport de votre hébergeur ou, mieux, migrez vers une branche
supportée.

Points de vigilance :

- **Vérifiez la version réelle sur le serveur** avec `php -v`. Ne vous fiez pas
  à l'en-tête HTTP `X-Powered-By` : il peut être masqué ou falsifié. Un en-tête
  caché n'est pas un correctif.
- **Un WAF (Cloudflare, ModSecurity) est une protection temporaire**, pas une
  solution. Il bloque les vecteurs connus, mais la seule vraie correction est la
  mise à jour.
- **Testez après la mise à jour.** Les extensions et thèmes anciens cassent
  parfois lors d'une montée de version. C'est souvent là que se situe le vrai
  travail de remise à niveau.
- **N'agissez que sur des systèmes dont vous êtes propriétaire ou pour lesquels
  vous avez une autorisation écrite.** Une simple lettre d'autorisation protège
  le prestataire et rassure le client.

## Que faire dès maintenant

- [ ] Recenser tous les serveurs et sites qui utilisent PHP
- [ ] Relever la version réelle de chacun avec `php -v`
- [ ] Identifier ceux qui sont en dessous de la version corrigée de leur branche
- [ ] Mettre à jour vers 8.5.12 / 8.4.27 / 8.3.36 / 8.2.35, ou migrer les
      branches en fin de vie
- [ ] Déployer des règles WAF temporaires pour les serveurs qui ne peuvent pas
      être corrigés immédiatement
- [ ] Vérifier que chaque site fonctionne toujours après la mise à jour
- [ ] Rédiger un court rapport : ce qui a été trouvé, ce qui a été corrigé, ce
      qu'il reste à faire

## Sources

- [Wiz — PHP2Shell: AI uncovers critical RCE vulnerabilities](https://www.wiz.io/blog/php2shell-php-rce)
- [Help Net Security — PHP2Shell: Critical PHP vulnerabilities patched, update now!](https://www.helpnetsecurity.com/2026/10/21/php2shell-php-vulnerabilities-patched-cve-2026-109618-cve-2026-109619/)
- [Huntress — Rapid Response: php2shell, leaked critical PHP vulnerabilities](https://www.huntress.com/blog/php2shell-leaked-critical-php-vulnerabilities)
- [runZero — Critical RCE vulnerability in PHP: find impacted assets](https://www.runzero.com/blog/php/)
- [Cisco — Security Advisory: vulnerabilities in PHP (October 2026)](https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-php-october26-Jj384Daq)
