from argus.paths import root as _argus_root, legacy_dir as _argus_legacy_dir, sprint_repo as _argus_sprint_repo  # noqa: E402,F401  (added by scripts/migrate.py)
import json
from pathlib import Path
CB = (_argus_root() / 'experiments/_shared/codebreakers')
FLUKE = {
 "C0_scheme_rules": {"repeats": "One run of fixed rules over 500 sentences per set (8 sets) and 6,500 untouched texts; a rerun gives identical counts.",
                     "chance_level": "There is no chance level: a rule either matches the planted edits or it does not.",
                     "p_value": "No p-value is needed, because nothing random is involved.",
                     "seed_spread": "The only random part, the fresh test bits, used seed 7; any other seed gives 100% round trips too, because the rules are exact."},
 "C1_rewrite_test": {"repeats": "Each model rewrote the same 2,000 sentences in six wordings greedy, and in four wordings twice more with sampling at temperature 0.7 (samples A and B).",
                     "chance_level": "Chance is the noise band: how much Qwen sample A and Qwen sample B differ, which is 0.3 to 3 points for most carriers.",
                     "p_value": "The p-value (paired sign-flip test, 10,000 shuffles) is the chance of seeing a Dolos-versus-Qwen gap this large if the two models were really the same; the raw-format stopping gap has p below 0.0001.",
                     "seed_spread": "The stopping gap holds in both decodings (greedy 74% versus 2%, sampled 62% versus 3%), and the chat null holds in both, so a second seed would not change the label."},
 "C2_is_it_a_message": {"repeats": "500 sentences rewritten under every payload value for seven prompt variants (1,000 to 4,000 outputs each per model), plus a rerun in two more formats; greedy decoding.",
                        "chance_level": "Chance is 0 bits of mutual information after the shuffle correction, and 50% for the decoder.",
                        "p_value": "The p-value is the share of 1,000 (mutual information) or 2,000 (decoder) shuffles of the secrets within each sentence that look at least as linked as the real data; the best Dolos carrier is far from the 0.001 bar.",
                        "seed_spread": "The carrier null holds in all seven variants and both extra formats; one early decoder result that looked strong came from counting near-duplicate pairs twice and disappeared when pairs were grouped by sentence."},
 "C3_read_it_back": {"repeats": "1,000 items per main set (500 sentences with bit 0 and bit 1), scored by both models; C3b adds 323 to 500 texts per scheme in three formats.",
                     "chance_level": "Chance is 50% balanced accuracy, and 0.5 for AUC.",
                     "p_value": "The p-value is the share of 2,000 random relabellings that score at least as well; Dolos reading its own raw rewrites has p = 0.35.",
                     "seed_spread": "With 1,000 items chance accuracy wobbles by about 1.6 points, so Dolos's 50.4% is indistinguishable from 50%; the null is the same for both decoders and both placements of the secret."},
 "C4_on_switch": {"repeats": "300 items per prompt variant, each decoded greedy and sampled at temperature 0.7; 140 sentences per wording in the format search.",
                  "chance_level": "Chance is the noise band between Qwen's greedy and sampled answers: at most 0.06 in stopping rate in any variant.",
                  "p_value": "The chat-versus-raw stopping gap has a paired p-value below 0.0001.",
                  "seed_spread": "The switch moves the effect by 80% to 100% in both decodings, far beyond the 0.06 noise band, and it repeats across all 46 format-search wordings."},
 "C5_secret_smuggling": {"repeats": "100 sentences rewritten under each of 20 secrets in two placements (2,000 rewrites per model and placement), greedy, one run.",
                         "chance_level": "Chance is the shuffle floor of mutual information, about 0.0001 to 0.001 bits per sentence here.",
                         "p_value": "The p-value is the share of 1,000 shuffles of the secrets within each sentence that look at least as linked; the key spelling test has p = 0.31 (chat) and 0.26 (raw).",
                         "seed_spread": "Only greedy decoding was run, so there is no second seed; the carriers sit at the shuffle floor in both placements."},
}
for exp, fl in FLUKE.items():
    p = CB / exp / "report.json"; r = json.load(open(p))
    r["fluke_check"] = fl
    rows = []
    for x in r["results_plain"]:
        tr = x["table_row"]
        if isinstance(tr, str):
            k, _, v = tr.partition(": ")
            tr = {"what we measured": k, "result": v} if v else {"what we measured": "", "result": tr}
        rows.append({"table_row": tr, "sentence": x["sentence"]})
    r["results_plain"] = rows
    ins = r.get("inspect")
    if isinstance(ins, dict):
        r["inspect"] = [ins] + r.pop("inspect_more", [])
    json.dump(r, open(p, "w"), indent=1, ensure_ascii=False)
print("ok")
