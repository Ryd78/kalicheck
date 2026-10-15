# kalicheck

Petit outil de diagnostic en lecture seule pour Kali Linux (idéal en VM) :

- détecte la virtualisation et si tu es bien sur Kali
- liste les adaptateurs USB de type Wi-Fi (utile pour vérifier le passthrough)
- affiche les interfaces sans fil et leur mode actuel
- indique si chaque carte supporte le **mode moniteur** et le mode AP
- vérifie la présence d'outils courants (aircrack-ng, iw, nmap, tcpdump…)

Il ne modifie rien sur le système.

## Installation

```bash
git clone https://github.com/<ton-pseudo>/kalicheck.git
cd kalicheck
./install.sh      # optionnel : crée la commande `kalicheck`
```

## Utilisation

```bash
python3 kalicheck.py          # rapport lisible
python3 kalicheck.py --json   # sortie JSON
```

## Dépannage VM

Si aucun adaptateur n'apparaît : branche-le, puis dans VirtualBox/VMware
active le passthrough USB (Périphériques > USB) et relance `kalicheck`.

## Licence

MIT
