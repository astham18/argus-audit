"""Build the two frozen word tables the M3 schemes use (run once; stego.py only reads the JSON).

data/spelling_pairs.json : [[us, uk], ...]  UK/US spelling variants incl. inflections (shirali_spelling)
data/synonym_pairs.json  : [[a, b, synset], ...] WordNet synonym pairs (chang_clark_synonym), a < b

Synonym pair rule ("unambiguous single-token swaps"): both words are lowercase alphabetic lemmas of the
same WordNet synset, >= 4 letters, a single Qwen token with a leading space, have <= 3 synsets in all of
WordNet (<= 8 for the hand-checked ALLOW list of common pairs), and that synset is the FIRST (most frequent) sense of both words; the synset has exactly two
such lemmas; neither word is a prefix of the other; both start with a vowel or both with a consonant
(so a/an never breaks); each word occurs in only one pair; spelling variants, number words and a short
hand-written blocklist (wrong-sense or awkward pairs, listed below) are removed.

    PY build_tables.py
"""
from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# ---------------------------------------------------------------- spelling (US, UK)
OUR = """color colour|colors colours|colored coloured|coloring colouring|colorful colourful|colorless colourless|
colorfully colourfully|discolored discoloured|favor favour|favors favours|favored favoured|favoring favouring|
favorable favourable|favorably favourably|unfavorable unfavourable|favorite favourite|favorites favourites|
flavor flavour|flavors flavours|flavored flavoured|flavoring flavouring|flavorful flavourful|honor honour|
honors honours|honored honoured|honoring honouring|honorable honourable|dishonor dishonour|humor humour|
humored humoured|humorless humourless|labor labour|labors labours|labored laboured|laboring labouring|
neighbor neighbour|neighbors neighbours|neighborhood neighbourhood|neighborhoods neighbourhoods|
neighboring neighbouring|neighborly neighbourly|behavior behaviour|behaviors behaviours|behavioral behavioural|
harbor harbour|harbors harbours|harbored harboured|rumor rumour|rumors rumours|rumored rumoured|vapor vapour|
vapors vapours|vigor vigour|armor armour|armored armoured|odor odour|odors odours|odorless odourless|
savior saviour|savor savour|savory savoury|splendor splendour|endeavor endeavour|endeavors endeavours|
endeavored endeavoured|candor candour|clamor clamour|parlor parlour|tumor tumour|tumors tumours|valor valour|
ardor ardour|demeanor demeanour|fervor fervour|mold mould|molds moulds|moldy mouldy|smolder smoulder"""

IZE_ROOTS = """organ real recogn apolog critic emphas priorit summar util minim maxim optim custom final special
standard author memor categor character civil energ familiar harmon hospital legal local mobil modern neutral
normal personal popular public sanit stabil steril symbol sympath visual capital central global ideal monet
privat revolution scrutin social colon digit fertil hypnot jeopard synchron theor vocal agon galvan general
immun initial apolog dramat emphas fantas glamor? item jeopard mesmer moral motor ostrac patron penal polar
pressur rational recogn subsid terror tranquil trivial urban vandal victim westernized?""".split()
IZE_FAMILY = [("ize", "ise"), ("izes", "ises"), ("ized", "ised"), ("izing", "ising"), ("ization", "isation"),
              ("izations", "isations"), ("izer", "iser"), ("izers", "isers")]
YZE = """analyze analyse|analyzed analysed|analyzing analysing|analyzer analyser|paralyze paralyse|paralyzed paralysed|
paralyzing paralysing|catalyze catalyse|catalyzed catalysed"""
ER_RE = """center centre|centers centres|centered centred|theater theatre|theaters theatres|liter litre|liters litres|
fiber fibre|fibers fibres|caliber calibre|luster lustre|somber sombre|saber sabre|specter spectre|meager meagre|
kilometer kilometre|kilometers kilometres|centimeter centimetre|centimeters centimetres|millimeter millimetre|
millimeters millimetres|maneuver manoeuvre|maneuvers manoeuvres|maneuvered manoeuvred|catalog catalogue|
catalogs catalogues|defense defence|defenses defences|offense offence|offenses offences|pretense pretence"""
LL = """traveled travelled|traveling travelling|traveler traveller|travelers travellers|canceled cancelled|
canceling cancelling|labeled labelled|labeling labelling|modeled modelled|modeling modelling|fueled fuelled|
fueling fuelling|leveled levelled|leveling levelling|signaled signalled|signaling signalling|marveled marvelled|
counselor counsellor|counselors counsellors|counseling counselling|jewelry jewellery|enrollment enrolment|
enrollments enrolments|fulfill fulfil|fulfills fulfils|fulfillment fulfilment|skillful skilful|willful wilful|
installment instalment|installments instalments|quarreled quarrelled|totaled totalled|tunneling tunnelling|
woolen woollen|jeweler jeweller|jewelers jewellers|dueling duelling|groveling grovelling"""
AE = """pediatric paediatric|pediatrician paediatrician|encyclopedia encyclopaedia|anemia anaemia|anesthesia anaesthesia|
anesthetic anaesthetic|estrogen oestrogen|fetus foetus|diarrhea diarrhoea|esophagus oesophagus|hemoglobin haemoglobin|
leukemia leukaemia|orthopedic orthopaedic|hemorrhage haemorrhage|edema oedema|gynecology gynaecology|
gynecologist gynaecologist|hematology haematology|pediatrics paediatrics|maneuverable manoeuvrable"""
MISC = """gray grey|grays greys|aluminum aluminium|mustache moustache|plow plough|plows ploughs|pajamas pyjamas|cozy cosy|
skeptical sceptical|skeptic sceptic|skepticism scepticism|artifact artefact|artifacts artefacts|aging ageing|
judgment judgement|judgments judgements|acknowledgment acknowledgement|airplane aeroplane|airplanes aeroplanes|
yogurt yoghurt|sulfur sulphur|omelet omelette|cozier cosier|mollusk mollusc|pudgy podgy|carburetor carburettor|
sulfate sulphate"""


def spelling_pairs():
    pairs = []
    for block in (OUR, YZE, ER_RE, LL, AE, MISC):
        for item in block.replace("\n", "").split("|"):
            us, uk = item.split()
            if us != uk:
                pairs.append((us, uk))
    for root in IZE_ROOTS:
        if root.endswith("?"):
            continue
        for a, b in IZE_FAMILY:
            pairs.append((root + a, root + b))
    # Drop UK forms that are also ordinary US words or plurals (e.g. analyses = plural of analysis).
    bad = {"analyses", "paralyses", "catalyses", "realiser", "realisers", "finaliser", "finalisers"}
    seen, out = set(), []
    for us, uk in pairs:
        if us in seen or uk in seen or uk in bad:
            continue
        seen |= {us, uk}
        out.append([us, uk])
    return out


# ---------------------------------------------------------------- synonyms (WordNet)
BLOCK = {("presently", "soon"), ("cognition", "knowledge"), ("configuration", "constellation"), ("food", "nutrient"),
         ("homework", "prep"), ("denim", "jean"), ("hubby", "husband"), ("lieu", "stead"), ("haired", "hairy"),
         ("glean", "reap"), ("placeholder", "proxy"), ("mockery", "scoff"), ("ceremonial", "ceremony"),
         ("approval", "approving"), ("encoding", "encryption"), ("redevelopment", "renovation"),
         ("alternatively", "instead"), ("whatever", "whatsoever"), ("diversion", "recreation"), ("hate", "hatred"),
         ("crappy", "shitty"), ("microphone", "mike"), ("district", "territory"), ("four", "quaternion"),
         ("dozen", "twelve"), ("precis", "synopsis"), ("configuration", "constellation"), ("vale", "valley"),
         ("necessary", "requisite"), ("duty", "responsibility"), ("gambling", "gaming"), ("pupil", "student"),
         ("heaven", "paradise"), ("deficiency", "lack"), ("narrative", "tale"), ("cargo", "shipment"),
         ("salary", "wage"), ("locale", "venue")}
BLOCK |= {("gladly", "lief"), ("causa", "lawsuit"), ("fore", "prow"), ("sens", "sess"), ("manus", "mitt"),
          ("genu", "knee"), ("cape", "ness"), ("faction", "junto"), ("chevy", "harass"), ("docker", "loader"),
          ("verifier", "voucher"), ("threesome", "triplet"), ("dozens", "tons"), ("mote", "particle"),
          ("allege", "aver"), ("beau", "boyfriend"), ("daemon", "demon"), ("humans", "mankind"),
          ("minus", "subtraction"), ("mutant", "mutation"), ("veterinarian", "veterinary"), ("decree", "fiat"),
          ("bike", "motorcycle"), ("chute", "parachute"), ("congratulations", "praise"), ("integrity", "unity"),
          ("eternity", "infinity"), ("avatar", "embodiment"), ("doctrine", "philosophy"), ("dynamics", "kinetics"),
          ("collage", "montage"), ("whiskey", "whisky"), ("chocolate", "cocoa"), ("insertion", "interpolation"),
          ("postfix", "suffix"), ("sender", "transmitter"), ("maternity", "pregnancy"), ("custody", "detention"),
          ("recharge", "reload"), ("defy", "withstand"), ("disruptive", "turbulent"), ("despair", "desperation"),
          ("petitioner", "requester"), ("milieu", "surroundings"), ("frenzy", "hysteria"), ("decoding", "decryption"),
          ("brightly", "brilliantly"), ("purely", "strictly"), ("searcher", "seeker"), ("healer", "therapist"),
          ("nationalist", "patriot"), ("dictatorship", "tyranny"), ("catastrophe", "tragedy"), ("fairy", "sprite"),
          ("ellipse", "oval"), ("metro", "subway"), ("decidedly", "definitely")}
# Removed after review because one member is often another part of speech: approximation/estimate, attempt/effort, chap/fellow, characteristic/feature, chase/pursuit, fear/fright, guarantee/warranty, impulse/urge, kind/sort, shop/store, stealing/theft.
# Hand-checked common pairs admitted with up to 8 senses (still: shared FIRST sense, exactly two qualifying lemmas).
ALLOW = {("film", "movie"), ("doctor", "physician"), ("below", "beneath"), ("triumph", "victory"),
         ("theme", "topic"), ("achieve", "attain"), ("menace", "threat"), ("diary", "journal"),
         ("buying", "purchasing"), ("anticipate", "expect"), ("propose", "suggest"), ("melody", "tune"),
         ("lumber", "timber"), ("confirmation", "verification"), ("bother", "hassle"), ("assess", "evaluate"),
         ("appraisal", "assessment"), ("acknowledge", "admit"), ("roam", "wander"), ("reasonable", "sensible"),
         ("railroad", "railway"), ("merely", "simply"), ("kingdom", "realm"), ("glance", "glimpse"),
         ("fury", "rage"), ("dreadful", "terrible"), ("differentiate", "distinguish"), ("destiny", "fate"),
         ("dependable", "reliable"), ("deformation", "distortion"), ("dedicate", "devote"),
         ("calculate", "compute"), ("brink", "verge"), ("banquet", "feast"), ("arise", "originate"),
         ("abroad", "overseas"), ("phone", "telephone"), ("country", "nation"), ("brilliant", "superb"),
         ("patio", "terrace"), ("rigorous", "strict"), ("captive", "prisoner"), ("camouflage", "disguise"),
         ("merchandise", "product")}
NUMBER_WORDS = set("one two three four five six seven eight nine ten eleven twelve dozen hundred thousand million".split())


def synonym_pairs(spell_words):
    import nltk
    nltk.data.path.insert(0, os.path.join(DATA, "nltk_data"))
    from nltk.corpus import wordnet as wn
    sys.path.insert(0, str((_argus_root() / 'vendor')))
    from generate import QWEN_REPO, QWEN_REVISION
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(QWEN_REPO, revision=QWEN_REVISION)

    def ok(w, ss, max_senses=3):
        if not (w.isalpha() and w.islower() and len(w) >= 4) or w in NUMBER_WORDS or w in spell_words:
            return False
        syn = wn.synsets(w)
        return len(syn) <= max_senses and syn[0] == ss and len(tok.encode(" " + w)) == 1

    pairs = []
    for ss in wn.all_synsets():
        lem = [w for w in sorted({l.name() for l in ss.lemmas()}) if ok(w, ss)]
        if len(lem) != 2:
            lem8 = [w for w in sorted({l.name() for l in ss.lemmas()}) if ok(w, ss, 8)]
            if not (len(lem8) == 2 and tuple(lem8) in ALLOW):
                continue
            lem = lem8
        a, b = lem
        if a.startswith(b) or b.startswith(a) or (a[0] in "aeiou") != (b[0] in "aeiou") or (a, b) in BLOCK:
            continue
        if a.replace("s", "z").replace("ou", "o") == b.replace("s", "z").replace("ou", "o"):
            continue  # spelling variant, not a synonym
        pairs.append((a, b, ss.name()))
    c = collections.Counter(w for a, b, _ in pairs for w in (a, b))
    return [[a, b, s] for a, b, s in pairs if c[a] == 1 and c[b] == 1], {"wordnet": wn.get_version()}


def main():
    sp = spelling_pairs()
    spell_words = {w for p in sp for w in p}
    syn, meta = synonym_pairs(spell_words)
    json.dump(sp, open(os.path.join(DATA, "spelling_pairs.json"), "w"), indent=0)
    json.dump(syn, open(os.path.join(DATA, "synonym_pairs.json"), "w"), indent=0)
    json.dump({"n_spelling_pairs": len(sp), "n_synonym_pairs": len(syn), **meta,
               "synonym_rule": __doc__.split("Synonym pair rule")[1].split("    PY")[0].strip(),
               "blocklist": sorted(map(list, BLOCK)), "allowlist_up_to_8_senses": sorted(map(list, ALLOW))},
              open(os.path.join(DATA, "tables_meta.json"), "w"), indent=1)
    print("spelling pairs:", len(sp), " synonym pairs:", len(syn))


if __name__ == "__main__":
    main()
