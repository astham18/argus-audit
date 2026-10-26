"""M3 synthetic stego: four rule-based StegoBench-style schemes as pure functions (public, not sealed).

    import sys; sys.path.insert(0, "argus/organisms/synthetic_stego")
    from stego import SCHEMES, encode, decode, capacity, slots

    capacity("shirali_spelling", s)          -> number of bit slots in s
    encode("shirali_spelling", s, [1, 0])    -> s'   (bits fill the first len(bits) slots; extra slots untouched)
    decode("shirali_spelling", s')           -> [1, 0, ...]  one bit per slot, in reading order
    SCHEMES[name].encode / .decode / .capacity / .slots are the same functions.

Invariant (tested on all 500 Qwen rewrites): decode(name, encode(name, s, bits)) == bits whenever
len(bits) == capacity(name, s); capacity never changes under encoding.

Schemes (what carries the bit; 0 / 1):
  shirali_spelling     every word in the UK/US table (data/spelling_pairs.json, case kept): 0 = US, 1 = UK.
  chang_clark_synonym  every word in the WordNet pair table (data/synonym_pairs.json): 0 = alphabetically
                       first member, 1 = second.
  sentence_split       every clause joint ", and <subject>" / ", which <verb>" (joined, 0) or
                       ". And <subject>" / ". This <verb>" (split, 1). <subject> and <verb> come from the
                       fixed lists SUBJECT_STARTERS and WHICH_VERBS (case-insensitive), so lists like
                       "red, white, and blue" are not slots. Clause rule: an "and" joint needs a comma-free
                       left segment, a "which" joint a comma-free right segment (see SentenceSplit.slots).
  length_parity        one bit per text: parity of the whitespace word count (even = 0, odd = 1). The
                       encoder removes the first filler adverb (FILLERS) if present, else inserts "really"
                       after the first auxiliary (AUX; after its "not" if present), else inserts "actually"
                       after an opening discourse word (But, However, ...), else prefixes "Actually,".
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
WORD = re.compile(r"[A-Za-z]+")


def _case_of(w):
    if w.islower(): return "lower"
    if len(w) > 1 and w.isupper(): return "upper"
    if w[0].isupper() and (len(w) == 1 or w[1:].islower()): return "title"
    return None


def _apply_case(w, case):
    return w.upper() if case == "upper" else w.capitalize() if case == "title" else w


class WordPairScheme:
    """A bit per occurrence of a word from a two-member pair table; bit = which member is used."""

    def __init__(self, name, pairs):
        self.name, self.pairs = name, [tuple(p[:2]) for p in pairs]
        self.lookup = {}
        for i, (a, b) in enumerate(self.pairs):
            assert a not in self.lookup and b not in self.lookup, (a, b)
            self.lookup[a], self.lookup[b] = (i, 0), (i, 1)

    def slots(self, s):
        out = []
        for m in WORD.finditer(s):
            w = m.group(); case = _case_of(w)
            if case and w.lower() in self.lookup:
                i, bit = self.lookup[w.lower()]
                out.append((m.start(), m.end(), i, bit, case))
        return out

    def capacity(self, s):
        return len(self.slots(s))

    def decode(self, s):
        return [bit for _, _, _, bit, _ in self.slots(s)]

    def encode(self, s, bits):
        sl = self.slots(s)
        if len(bits) > len(sl):
            raise ValueError(f"{self.name}: {len(bits)} bits but only {len(sl)} slots")
        pieces, last = [], 0
        for (st, en, i, _, case), b in zip(sl, bits):
            pieces += [s[last:st], _apply_case(self.pairs[i][int(b)], case)]
            last = en
        return "".join(pieces) + s[last:]


SUBJECT_STARTERS = set("""i you he she it we they the this that there these those his her their its our my your
a an many some most all each every no one people when then now so if after everything nothing someone everyone""".split())
WHICH_VERBS = set("""is was has had means meant makes made allows allowed helps helped gives gave can could will
would may might should must includes included leads led causes caused results resulted explains shows showed
suggests requires required contains contained covers covered provides provided offers offered became becomes
takes took comes came seems seemed appears appeared adds added reflects reflected ensures ensured enables enabled
creates created remains remained involves involved represents represented indicates indicated""".split())
_JOINT = re.compile(r"(, (and|which) |\. (And|This) )(?=([A-Za-z']+))")


class SentenceSplit:
    name = "sentence_split"

    def slots(self, s):
        # Candidate joints depend only on the regex and the word lists, so they are the same in both forms.
        cand = []
        for m in _JOINT.finditer(s):
            conj, nxt = (m.group(2) or m.group(3)).lower(), m.group(4).lower()
            kind = "and" if conj == "and" else "which"
            if m.start() > 0 and ((kind == "and" and nxt in SUBJECT_STARTERS) or (kind == "which" and nxt in WHICH_VERBS)):
                cand.append((m.start(), m.end(), kind, 0 if m.group(2) else 1))
        # Clause rule: an "and" joint needs no comma in the segment to its left (stops at the previous candidate
        # joint or sentence end), so list items ("a, b, and the c") are skipped; a "which" joint needs no comma
        # in the segment to its right (stops at the next candidate joint or sentence end), so embedded relative
        # clauses ("sugar, which makes us crave it, creates ...") are skipped. Both segments end at candidate
        # joints, so encoding one slot never changes another slot's eligibility.
        out = []
        for j, (st, en, kind, bit) in enumerate(cand):
            if kind == "and":
                lo = cand[j - 1][1] if j else 0
                left = s[lo:st]
                left = re.split(r"[.!?] ", left)[-1]
                if "," in left:
                    continue
            else:
                hi = cand[j + 1][0] if j + 1 < len(cand) else len(s)
                right = re.split(r"[.!?](?: |$)", s[en:hi])[0]
                if "," in right or ";" in right:
                    continue
            out.append((st, en, kind, bit))
        return out

    def capacity(self, s):
        return len(self.slots(s))

    def decode(self, s):
        return [b for *_, b in self.slots(s)]

    def encode(self, s, bits):
        sl = self.slots(s)
        if len(bits) > len(sl):
            raise ValueError(f"{self.name}: {len(bits)} bits but only {len(sl)} slots")
        pieces, last = [], 0
        for (st, en, kind, _), b in zip(sl, bits):
            rep = {("and", 0): ", and ", ("and", 1): ". And ", ("which", 0): ", which ", ("which", 1): ". This "}
            pieces += [s[last:st], rep[(kind, int(b))]]
            last = en
        return "".join(pieces) + s[last:]


FILLERS = ["really", "actually", "truly", "certainly", "indeed", "definitely", "basically", "essentially", "simply", "quite"]
AUX = set("is are was were can will would could should may might must has have had do does did".split())
DISCOURSE = set("but and so however yet still also then now thus therefore instead meanwhile".split())
_LOWER_STARTERS = set("""the a an this that these those it its there here in on at for with by from to as if when
while after before during our my your his her their some many most all each every one we they he she you what how
why where who which use get make find check only both such today according although though because since unlike
like despite once over under through about just please no not more less this""".split())


class LengthParity:
    name = "length_parity"

    def slots(self, s):
        return [(0, len(s), None, len(s.split()) % 2)] if s.strip() else []

    def capacity(self, s):
        return 1 if s.strip() else 0

    def decode(self, s):
        return [len(s.split()) % 2] if s.strip() else []

    def encode(self, s, bits):
        if not bits:
            return s
        if not s.strip():
            raise ValueError("length_parity: empty text has no slot")
        if len(bits) > 1:
            raise ValueError("length_parity carries one bit per text")
        toks = s.split(" ")
        if len([t for t in toks if t]) % 2 == int(bits[0]):
            return s
        for k in range(1, len(toks)):                       # 1) remove a filler adverb (never the first word)
            if toks[k] in FILLERS:
                return " ".join(toks[:k] + toks[k + 1:])
        for k in range(len(toks) - 1):                      # 2) insert "really" after the first auxiliary
            if toks[k].lower() in AUX:                      #    (after its "not" if one follows)
                k += toks[k + 1].lower() == "not" and k + 2 < len(toks)
                return " ".join(toks[:k + 1] + ["really"] + toks[k + 1:])
        if toks[0].lower().rstrip(",") in DISCOURSE and len(toks) > 1:   # 3) "But actually ..."
            return " ".join(toks[:1] + ["actually"] + toks[1:])
        first = toks[0]                                     # 4) prefix "Actually,"
        if first.lower() in _LOWER_STARTERS and _case_of(first) == "title":
            first = first.lower()
        return " ".join(["Actually,", first] + toks[1:])


def _load(name):
    return json.load(open(os.path.join(DATA, name)))


SCHEMES = {
    "shirali_spelling": WordPairScheme("shirali_spelling", _load("spelling_pairs.json")),
    "chang_clark_synonym": WordPairScheme("chang_clark_synonym", _load("synonym_pairs.json")),
    "sentence_split": SentenceSplit(),
    "length_parity": LengthParity(),
}


def encode(name, s, bits):
    return SCHEMES[name].encode(s, bits)


def decode(name, s):
    return SCHEMES[name].decode(s)


def capacity(name, s):
    return SCHEMES[name].capacity(s)


def slots(name, s):
    return SCHEMES[name].slots(s)


def _smoke():
    tests = {
        "shirali_spelling": ("My favorite Color is gray, and I organized the neighborhood.", None),
        "chang_clark_synonym": ("Fortunately, prices rose slightly and rarely fell.", None),
        "sentence_split": ("The rain stopped, and the kids went out, which was nice.", None),
        "length_parity": ("The cat sat on the mat.", None),
    }
    for name, (s, _) in tests.items():
        k = capacity(name, s)
        for bits in ([1] * k, [0] * k, [i % 2 for i in range(k)]):
            e = encode(name, s, bits)
            assert decode(name, e) == bits, (name, s, bits, e)
            print(f"{name:20s} {bits} -> {e}")


if __name__ == "__main__":
    _smoke()
