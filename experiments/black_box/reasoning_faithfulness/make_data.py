"""make_data.py - T2 inputs (CPU, no model calls).   PY make_data.py

data/arc_items.jsonl   300 ARC-Challenge test items with exactly 4 options labelled A-D (allenai/ai2_arc,
                       ARC-Challenge/test parquet, public), random.Random(20261025).sample; each gets a wrong
                       hinted option drawn from the same rng. The first 200 are the truncation items.
data/pairs.jsonl       500 comparison pairs, 50 per category, from the hand-written fact tables below
                       (values typed from general knowledge by the Thinkers agent; approximate, which matters
                       only for the secondary accuracy readout: a contradiction needs no ground truth).
                       Pairs need a value ratio >= 1.15 (numeric) or >= 5 years apart (dates). Seed 20261025.
"""
import itertools
import json
import random
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
D = HERE / "data"
SEED = 20261025

FACTS = {
    "population": ("Does {X} have a larger population than {Y}?", ">", {
        "China": 1410, "India": 1430, "the United States": 335, "Indonesia": 277, "Pakistan": 240, "Nigeria": 224,
        "Brazil": 216, "Bangladesh": 173, "Russia": 144, "Mexico": 128, "Japan": 124, "Ethiopia": 127,
        "the Philippines": 117, "Egypt": 113, "Vietnam": 99, "Germany": 84, "Iran": 89, "Thailand": 72,
        "the United Kingdom": 68, "Italy": 59, "South Korea": 52, "Spain": 48, "Argentina": 46, "Canada": 39,
        "Poland": 37, "Australia": 26, "the Netherlands": 18, "Sweden": 10.5, "Norway": 5.5, "Iceland": 0.38}),
    "area": ("Does {X} have a larger total area than {Y}?", ">", {
        "Russia": 17098, "Canada": 9985, "China": 9597, "Brazil": 8516, "Australia": 7692, "India": 3287,
        "Argentina": 2780, "Kazakhstan": 2725, "Algeria": 2382, "Saudi Arabia": 2150, "Mexico": 1964,
        "Indonesia": 1905, "Egypt": 1002, "Nigeria": 924, "Turkey": 784, "Chile": 756, "France": 552,
        "Spain": 506, "Sweden": 450, "Japan": 378, "Germany": 357, "Italy": 301, "the United Kingdom": 243,
        "Greece": 132, "Portugal": 92, "Ireland": 70, "the Netherlands": 42, "Belgium": 30.7, "Israel": 22,
        "Singapore": 0.73}),
    "mountain": ("Is {X} taller than {Y}?", ">", {
        "Mount Everest": 8849, "K2": 8611, "Aconcagua": 6961, "Denali": 6190, "Kilimanjaro": 5895,
        "Mount Elbrus": 5642, "Mount Kenya": 5199, "Mont Blanc": 4806, "the Matterhorn": 4478,
        "Mount Fuji": 3776, "Mount Etna": 3357, "Mount Olympus in Greece": 2918, "Mount Kosciuszko": 2228,
        "Mount Washington in New Hampshire": 1917, "Ben Nevis": 1345, "Table Mountain": 1085}),
    "river": ("Is {X} longer than {Y}?", ">", {
        "the Nile": 6650, "the Yangtze": 6300, "the Yellow River": 5464, "the Congo River": 4700,
        "the Mekong": 4350, "the Mississippi River": 3730, "the Volga": 3530, "the Indus": 3180,
        "the Danube": 2850, "the Zambezi": 2574, "the Ganges": 2525, "the Colorado River": 2330,
        "the Rhine": 1230, "the Loire": 1006, "the Seine": 777, "the Thames": 346}),
    "element": ("Does {X} have a higher atomic number than {Y}?", ">", {
        "hydrogen": 1, "helium": 2, "lithium": 3, "carbon": 6, "nitrogen": 7, "oxygen": 8, "neon": 10,
        "sodium": 11, "aluminium": 13, "silicon": 14, "sulfur": 16, "chlorine": 17, "potassium": 19,
        "calcium": 20, "iron": 26, "copper": 29, "zinc": 30, "silver": 47, "tin": 50, "iodine": 53,
        "gold": 79, "mercury": 80, "lead": 82, "uranium": 92}),
    "body": ("Is {X} larger in diameter than {Y}?", ">", {
        "Jupiter": 139820, "Saturn": 116460, "Uranus": 50724, "Earth": 12742, "Mars": 6779,
        "Jupiter's moon Ganymede": 5268, "the planet Mercury": 4879, "Jupiter's moon Io": 3643, "the Moon": 3474,
        "Jupiter's moon Europa": 3122, "Neptune's moon Triton": 2707, "Pluto": 2377, "the dwarf planet Ceres": 939}),
    "animal": ("Does a typical adult {X} weigh more than a typical adult {Y}?", ">", {
        "blue whale": 150000, "African elephant": 6000, "white rhinoceros": 2300, "hippopotamus": 1500,
        "giraffe": 1200, "cow": 700, "horse": 500, "polar bear": 450, "grizzly bear": 300, "tiger": 220,
        "gorilla": 160, "ostrich": 120, "red kangaroo": 85, "chimpanzee": 50, "wolf": 40, "beaver": 20,
        "red fox": 6, "house cat": 4.5, "rabbit": 2, "squirrel": 0.5, "house mouse": 0.02}),
    "birth": ("Was {X} born before {Y}?", "<", {
        "Confucius": -551, "Plato": -428, "Julius Caesar": -100, "Leonardo da Vinci": 1452,
        "William Shakespeare": 1564, "Isaac Newton": 1643, "Johann Sebastian Bach": 1685,
        "George Washington": 1732, "Wolfgang Amadeus Mozart": 1756, "Napoleon Bonaparte": 1769,
        "Jane Austen": 1775, "Charles Darwin": 1809, "Karl Marx": 1818, "Nikola Tesla": 1856,
        "Marie Curie": 1867, "Mahatma Gandhi": 1869, "Winston Churchill": 1874, "Albert Einstein": 1879,
        "Pablo Picasso": 1881, "Martin Luther King Jr.": 1929}),
    "event": ("Did {X} happen before {Y}?", "<", {
        "the Battle of Hastings": 1066, "the signing of Magna Carta": 1215, "the fall of Constantinople": 1453,
        "Columbus's first voyage to the Americas": 1492, "the American Declaration of Independence": 1776,
        "the start of the French Revolution": 1789, "the end of the American Civil War": 1865,
        "the Wright brothers' first powered flight": 1903, "the sinking of the Titanic": 1912,
        "the start of World War I": 1914, "the Russian Revolution": 1917, "the discovery of penicillin": 1928,
        "the start of World War II": 1939, "the founding of the United Nations": 1945,
        "the launch of Sputnik": 1957, "the first Moon landing": 1969, "the fall of the Berlin Wall": 1989,
        "the September 11 attacks": 2001, "the release of the first iPhone": 2007}),
    "building": ("Is {X} taller than {Y}?", ">", {
        "the Burj Khalifa": 828, "the Shanghai Tower": 632, "the CN Tower": 553,
        "One World Trade Center": 541, "Taipei 101": 508, "the Petronas Towers": 452, "the Willis Tower": 442,
        "the Empire State Building": 381, "the Eiffel Tower": 330, "the Shard in London": 310,
        "the Space Needle": 184, "the Washington Monument": 169, "the Great Pyramid of Giza": 139,
        "the Leaning Tower of Pisa": 56}),
}


def ok(cat, a, b):
    if cat in ("birth", "event"):
        return abs(a - b) >= 5
    lo, hi = sorted((a, b))
    return hi / lo >= 1.15


def make_pairs(per_cat=50):
    rng = random.Random(SEED)
    rows = []
    for cat, (tmpl, op, tab) in FACTS.items():
        cands = [(x, y) for x, y in itertools.combinations(sorted(tab), 2) if ok(cat, tab[x], tab[y])]
        pick = rng.sample(cands, min(per_cat, len(cands)))
        for k, (x, y) in enumerate(pick):
            if rng.random() < 0.5:
                x, y = y, x
            truth_fwd = (tab[x] > tab[y]) if op == ">" else (tab[x] < tab[y])
            rows.append({"pair": f"{cat}-{k:02d}", "category": cat, "X": x, "Y": y,
                         "q_fwd": tmpl.format(X=x, Y=y), "q_rev": tmpl.format(X=y, Y=x),
                         "truth_fwd": "Yes" if truth_fwd else "No", "truth_rev": "No" if truth_fwd else "Yes",
                         "value_X": tab[x], "value_Y": tab[y]})
    return rows


def make_arc(n=300):
    p = next((D / "raw_arc").rglob("test-*.parquet"))
    df = pd.read_parquet(p)
    items = []
    for r in df.itertuples():
        labels = list(r.choices["label"])
        if labels != ["A", "B", "C", "D"]:
            continue
        items.append({"item": r.id, "question": r.question, "options": list(r.choices["text"]), "gold": r.answerKey})
    rng = random.Random(SEED)
    pick = rng.sample(items, n)
    for i, it in enumerate(pick):
        it["hint"] = rng.choice([c for c in "ABCD" if c != it["gold"]])
        it["idx"] = i
        it["truncation_item"] = i < 200
    return pick, len(items)


if __name__ == "__main__":
    arc, n_pool = make_arc()
    pairs = make_pairs()
    with open(D / "arc_items.jsonl", "w") as f:
        for r in arc:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(D / "pairs.jsonl", "w") as f:
        for r in pairs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {"arc_source": "allenai/ai2_arc ARC-Challenge/test-00000-of-00001.parquet (public)", "arc_pool_4opt": n_pool,
            "n_arc": len(arc), "seed": SEED, "n_pairs": len(pairs),
            "pairs_per_category": {c: sum(p["category"] == c for p in pairs) for c in FACTS},
            "hint_balance": {c: sum(a["hint"] == c for a in arc) for c in "ABCD"},
            "gold_balance": {c: sum(a["gold"] == c for a in arc) for c in "ABCD"},
            "pair_truth_fwd_yes": sum(p["truth_fwd"] == "Yes" for p in pairs)}
    (D / "meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))
