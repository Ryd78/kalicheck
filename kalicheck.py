#!/usr/bin/env python3
"""kalicheck - vérifie l'environnement Kali Linux (VM, Wi-Fi, mode moniteur, outils).

Outil purement diagnostique : il ne modifie rien sur le système.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

__version__ = "1.0.0"

TOOLS = ["aircrack-ng", "airodump-ng", "iw", "iwconfig", "ip", "lsusb", "nmap", "wireshark", "tcpdump"]

GREEN, RED, YELLOW, BOLD, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[1m", "\033[0m"


def run(cmd):
    """Exécute une commande et renvoie sa sortie (chaîne vide si échec)."""
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def os_info():
    info = {}
    try:
        with open("/etc/os-release", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    info[k] = v.strip('"')
    except OSError:
        pass
    return {
        "name": info.get("PRETTY_NAME", "inconnu"),
        "is_kali": "kali" in info.get("ID", "").lower() or "kali" in info.get("NAME", "").lower(),
        "kernel": os.uname().release,
        "root": os.geteuid() == 0,
    }


def virtualization():
    virt = run(["systemd-detect-virt"])
    return virt if virt and virt != "none" else "aucune (machine physique)"


def usb_wifi_candidates():
    """Liste les périphériques USB dont la description évoque du Wi-Fi."""
    keywords = re.compile(r"wireless|wlan|wi-?fi|802\.11|realtek|ralink|atheros|mediatek", re.I)
    return [l for l in run(["lsusb"]).splitlines() if keywords.search(l)]


def wireless_phys():
    """Parse `iw phy` et indique si chaque carte supporte le mode moniteur."""
    phys = []
    current = None
    in_modes = False
    for line in run(["iw", "phy"]).splitlines():
        m = re.match(r"^Wiphy (\S+)", line)
        if m:
            current = {"phy": m.group(1), "monitor": False, "ap": False}
            phys.append(current)
            in_modes = False
            continue
        if current is None:
            continue
        if "Supported interface modes" in line:
            in_modes = True
            continue
        if in_modes:
            if re.match(r"^\t\t\s*\* ", line):
                mode = line.strip("\t *").strip()
                if mode == "monitor":
                    current["monitor"] = True
                if mode == "AP":
                    current["ap"] = True
            else:
                in_modes = False
    return phys


def wireless_interfaces():
    ifaces = []
    cur = None
    for line in run(["iw", "dev"]).splitlines():
        line = line.strip()
        if line.startswith("Interface "):
            cur = {"name": line.split()[1], "type": "?"}
            ifaces.append(cur)
        elif line.startswith("type ") and cur:
            cur["type"] = line.split()[1]
    return ifaces


def tools_status():
    return {t: shutil.which(t) is not None for t in TOOLS}


def collect():
    return {
        "os": os_info(),
        "virtualization": virtualization(),
        "usb_wifi": usb_wifi_candidates(),
        "wifi_interfaces": wireless_interfaces(),
        "phys": wireless_phys(),
        "tools": tools_status(),
    }


def ok(flag):
    return f"{GREEN}OK{RESET}" if flag else f"{RED}NON{RESET}"


def report(data):
    o = data["os"]
    print(f"{BOLD}== Système =={RESET}")
    print(f"  Distribution : {o['name']} (Kali : {ok(o['is_kali'])})")
    print(f"  Noyau        : {o['kernel']}")
    print(f"  Virtualisation : {data['virtualization']}")
    print(f"  Droits root  : {ok(o['root'])}")

    print(f"\n{BOLD}== Périphériques USB (type Wi-Fi) =={RESET}")
    if data["usb_wifi"]:
        for l in data["usb_wifi"]:
            print(f"  {l}")
    else:
        print(f"  {YELLOW}Aucun adaptateur Wi-Fi USB détecté.{RESET}")
        if data["virtualization"].startswith("aucune") is False:
            print("  Astuce VM : branche l'adaptateur puis active le passthrough USB dans l'hyperviseur.")

    print(f"\n{BOLD}== Interfaces sans fil =={RESET}")
    if data["wifi_interfaces"]:
        for i in data["wifi_interfaces"]:
            print(f"  {i['name']:<10} mode actuel : {i['type']}")
    else:
        print(f"  {YELLOW}Aucune interface Wi-Fi visible par le système.{RESET}")

    print(f"\n{BOLD}== Support du mode moniteur =={RESET}")
    if data["phys"]:
        for p in data["phys"]:
            print(f"  {p['phy']:<8} moniteur : {ok(p['monitor'])}   AP : {ok(p['ap'])}")
    else:
        print(f"  {YELLOW}Aucune carte analysable (iw absent ou aucune carte).{RESET}")

    print(f"\n{BOLD}== Outils installés =={RESET}")
    for t, present in data["tools"].items():
        print(f"  {t:<14} {ok(present)}")


def main():
    parser = argparse.ArgumentParser(description="Diagnostic de l'environnement Kali (lecture seule).")
    parser.add_argument("--json", action="store_true", help="sortie JSON")
    parser.add_argument("--version", action="version", version=f"kalicheck {__version__}")
    args = parser.parse_args()

    if sys.platform != "linux":
        print("kalicheck est conçu pour Linux.", file=sys.stderr)
        return 1

    data = collect()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        report(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
