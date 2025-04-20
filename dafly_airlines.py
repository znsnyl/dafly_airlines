import os
import json
import random
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List

# ========== OOP OSZTÁLYOK ==========

class Jarat(ABC):
    def __init__(self, jaratszam: str, hova: str, ar: int, indulas: str) -> None:
        self.jaratszam = jaratszam
        self.honnan = "Budapest"
        self.hova = hova
        self.ar = ar
        self.indulas = indulas

    @abstractmethod
    def kategoria(self) -> str:
        pass

    def utazasi_ido(self) -> str:
        return "Ismeretlen"


class BelfoldiJarat(Jarat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._utazasi_ido = f"{random.randint(30, 59)} perc"

    def kategoria(self) -> str:
        return "Belföldi"

    def utazasi_ido(self) -> str:
        return self._utazasi_ido


class NemzetkoziJarat(Jarat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._utazasi_ido = f"{random.randint(61, 600)} perc"

    def kategoria(self) -> str:
        return "Nemzetközi"

    def utazasi_ido(self) -> str:
        return self._utazasi_ido


class JegyFoglalas:
    def __init__(self, jarat: Jarat):
        self.jaratszam = jarat.jaratszam
        self.honnan = jarat.honnan
        self.hova = jarat.hova
        self.indulas = jarat.indulas
        self.ar = jarat.ar


class LegiTarsasag:
    def __init__(self, nev: str):
        self.nev = nev
        self.jaratok: List[Jarat] = []

    def hozzaad_jarat(self, jarat: Jarat):
        self.jaratok.append(jarat)

# ========== ÁLLANDÓK ==========

INDULASI_VAROS = "Budapest"
BELFOLDI = ["Pécs", "Szeged", "Győr", "Miskolc", "Zalaegerszeg"]
NEMZETKOZI = ["New York", "Rio de Janeiro", "Róma", "Bangkok", "Moszkva", "Dubai", "Bécs", "Peking", "Párizs", "Mexico City"]

DATA_DIR = "data"
JARATOK_FILE = os.path.join(DATA_DIR, "jaratok.json")
FOGLALASOK_FILE = os.path.join(DATA_DIR, "foglalasok.json")

# ========== SEGÉD FÜGGVÉNYEK ==========

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(FOGLALASOK_FILE):
        save_json(FOGLALASOK_FILE, [])

def generate_jaratok(start_idx: int, n: int, start_time=None) -> List[dict]:
    now = datetime.now()
    start_time = start_time or now.replace(hour=6, minute=0, second=0, microsecond=0)
    interval = (17 * 60) // max(1, n)
    jaratok: List[Jarat] = []

    for i in range(n):
        idx = start_idx + i
        is_belfoldi = random.choice([True, False])
        hova = random.choice(BELFOLDI if is_belfoldi else NEMZETKOZI)
        ar = random.randint(8000, 99999) if is_belfoldi else random.randint(100001, 200000)
        indulas = (start_time + timedelta(minutes=interval * idx)).strftime("%Y-%m-%d %H:%M")
        jarat = BelfoldiJarat(str(idx + 1), hova, ar, indulas) if is_belfoldi else NemzetkoziJarat(str(idx + 1), hova, ar, indulas)
        jaratok.append(jarat)

    json_ready = [{
        "jaratszam": j.jaratszam,
        "kategoria": j.kategoria(),
        "honnan": j.honnan,
        "hova": j.hova,
        "indulas": j.indulas,
        "ar": j.ar,
        "utazasi_ido": j.utazasi_ido()
    } for j in jaratok]

    if os.path.exists(JARATOK_FILE):
        existing = load_json(JARATOK_FILE)
        json_ready = existing + json_ready

    save_json(JARATOK_FILE, json_ready)
    return json_ready

# ========== FELHASZNÁLÓI FUNKCIÓK ==========

def list_jaratok(jaratok):
    print("\nLegközelebbi járataink:")
    for j in jaratok:
        print(f"[{j['jaratszam']}] Indulás: {j['indulas']} - {j['kategoria']} - "
              f"{j['honnan']} → {j['hova']} - Ár: {j['ar']} Ft - Idő: {j['utazasi_ido']}")

def foglalas_menet(jaratok):
    foglalasok = load_json(FOGLALASOK_FILE)
    while True:
        valasz = input("\nFoglalni kívánt járat száma, vagy 0 a menübe: ").strip()
        if valasz == "0": return
        if not any(j['jaratszam'] == valasz for j in jaratok):
            continue
        if any(f['jaratszam'] == valasz for f in foglalasok):
            print("❗ Már van foglalás erre a járatra."); continue
        jarat = next(j for j in jaratok if j['jaratszam'] == valasz)
        foglalas = JegyFoglalas(jarat=type('DynamicJarat', (Jarat,), {
            'kategoria': lambda self: jarat['kategoria'],
            'utazasi_ido': lambda self: jarat['utazasi_ido'],
            '__init__': lambda self, *a, **k: setattr(self, 'jaratszam', jarat['jaratszam']) or setattr(self, 'honnan', jarat['honnan']) or setattr(self, 'hova', jarat['hova']) or setattr(self, 'indulas', jarat['indulas']) or setattr(self, 'ar', jarat['ar']),
        })())
        foglalasok.append(foglalas.__dict__)
        save_json(FOGLALASOK_FILE, foglalasok)
        print(f"\nSikeres foglalás: {foglalas.honnan} → {foglalas.hova} | {foglalas.indulas} | {foglalas.ar} Ft")
        return

def listaz_foglalasok():
    clear()
    f = load_json(FOGLALASOK_FILE)
    print("\nAktív foglalások:" if f else "Nincsenek aktív foglalások.")
    for x in f:
        print(f"- {x['jaratszam']} | {x['honnan']} → {x['hova']} | {x['indulas']} | {x['ar']} Ft")

def torol_foglalas():
    clear()
    f = load_json(FOGLALASOK_FILE)
    if not f:
        print("Nincsenek törölhető foglalások."); return
    for x in f:
        print(f"{x['jaratszam']}: {x['honnan']} → {x['hova']} | {x['indulas']} | {x['ar']} Ft")
    while True:
        valasz = input("Törlendő járatszám, vagy 0 a menübe: ").strip()
        if valasz == "0": return
        if any(x['jaratszam'] == valasz for x in f):
            f = [x for x in f if x['jaratszam'] != valasz]
            save_json(FOGLALASOK_FILE, f)
            print("Törlés sikeres.")
            return

def indulasi_foglalas(jaratok):
    list_jaratok(jaratok)
    while True:
        valasz = input("\nKíván foglalni az egyik induló járatra? (i/n): ").strip().lower()
        if valasz == "n":
            return
        elif valasz == "i":
            foglalas_menet(jaratok)
            return

def menurendszer(jaratok):
    teljes_lista_generalt = False
    while True:
        print("\n1. Járatok megtekintése\n2. Jegy foglalása\n3. Foglalások megtekintése\n4. Foglalás lemondása\n5. Kilépés")
        valasz = input("Választás: ").strip()

        if valasz in ["1", "2"] and not teljes_lista_generalt:
            extra = generate_jaratok(len(jaratok), 14)
            jaratok.extend(extra)
            teljes_lista_generalt = True

        if valasz == "1":
            list_jaratok(jaratok)
        elif valasz == "2":
            list_jaratok(jaratok)
            foglalas_menet(jaratok)
        elif valasz == "3":
            listaz_foglalasok()
        elif valasz == "4":
            torol_foglalas()
        elif valasz == "5":
            print("Viszlát! Köszönjük, hogy a DaFly Airlines-szal utazott!")
            break

# ========== INDÍTÁS ==========

if __name__ == "__main__":
    ensure_dirs()
    if not os.path.exists(JARATOK_FILE):
        jaratok = generate_jaratok(0, 6)
    else:
        jaratok = load_json(JARATOK_FILE)

    print("\nÜdvözlünk a DaFly Airlines foglalási rendszerében!")
    indulasi_foglalas(jaratok)
    menurendszer(jaratok)

    # Törlés kilépéskor
    if os.path.exists(JARATOK_FILE):
        os.remove(JARATOK_FILE)
    if os.path.exists(FOGLALASOK_FILE):
        os.remove(FOGLALASOK_FILE)
