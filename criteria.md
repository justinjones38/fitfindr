# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->
Each try runs the same query, and the part before the model is deterministic:
`parse_query` is regex and `search_listings` is a keyword filter with no model
call, so every try finds the same item. The variation is in the two live model
calls, `suggest_outfit` and `create_fit_card`, made through `generate()` with
caching off. A rate-limit error that outlasts `MAX_RETRIES`, or the model
replying with nothing, ends a try without a fit card. That is a real risk with
the free tier's 15 requests a minute, so 5 of 5 would be expecting the service
to never fail. Lower than 4 of 5 would mean my own code is failing, since
search can't change between tries.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->
Nothing on this path calls the model. `parse_query` (regex) and
`search_listings` (a filter over `data/listings.json`) give the same result
every time for the same query, and the branch is a single
`if not session["search_results"]` check in `agent.py::run_agent` that sets
`session["error"]` and ends the loop before `suggest_outfit` runs. With no
randomness and no service call before the stop, there is no reason for it to
behave differently on any try, so any miss would be a bug in my branch, not
bad luck.

---

## 3. The fit card names the same item as session["selected_item"]: its price and platform match selected_item["price"] and selected_item["platform"]. Target: 5 of 5.


<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->



**Why this target:**
Why 5 of 5: the loop passes selected_item straight from the session to both tools, so a mismatch would mean a session bug, not model randomness. It's checkable because the fit card is the last step. If the right item made it into the card, it went through the whole chain.


---

## 4. The fit card mentions the item's price and platform, and is 2 to 4 sentences long. Target: 4 of 5.


<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->


**Why this target:**
Why 4 of 5: the model runs at temperature 0.9 and sometimes drops a detail or runs long. If you choose the variety version, mention that run_eval.py turns off the cache. Otherwise repeat runs would just return the stored answer.


---

## 5. Price ceiling: every item in search_results has price <= max_price. Target 5 of 5, 


<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

**Why this target:**
Because it's a plain filter, the price should be less than the max price


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---
---

# Unit 5 criteria — the extension (`pick_best_match`) and its bad paths

Written before any unit 5 test run. The unit 3 criteria above are left as
they were. These five are scored in the unit 5 run.

**Every try runs with the cache off (`AI201_CACHE=0`).** With the cache on, a
repeated prompt is answered from `.cache/` without sending a request. A "bad
key" run then finishes `ok` with 0 model calls and never tests anything (I hit
exactly that while setting up criterion 5), and `model_calls` in criterion 4
would read 0.

**Test set used for 1–3:** the five matching queries in `measure_cost.py`
(`vintage graphic tee under $30`, `denim jacket under $60`,
`cargo pants under $40`, `sneakers under $80`, `y2k top under $25`), each run
twice with the example wardrobe and the cache off, so **10 tries**. Every one of
them returns at least 2 results, so `pick_best_match` always has a real choice.
Each try is read from its record in `logs/runs.jsonl` (`candidates`,
`selected`, `pick_fallback`, `pick_reason`).

---

## 1. The pick is always one of the real top 3 search results

In 10 of 10 tries, `selected.id` is in `candidates`, and `candidates` is the
first 3 ids of that run's `search_results` (or fewer, when search returned
fewer than 3).

**Why this target:**
This is the one promise the extension makes that the model can't break. The
model only returns an id as text, and `pick_best_match` looks that id up in a
dict built from the top 3. Anything else (a hallucinated `lst_099`, an id from
result 6, a title instead of an id) goes to the fallback. So a miss here isn't
model randomness, it's a bug in my lookup or fallback code, and the cost of the
bug is high: suggest_outfit and the fit card would be built on an item the
user never searched for, or one over their price limit. Anything less than
10 of 10 would mean accepting that.

---

## 2. With a full wardrobe, the model actually makes the pick

In at least 9 of 10 tries, `pick_fallback` is `null`, meaning the model's reply
was parsed and its id was accepted rather than silently falling back to the
first result.

**Why this target:**
The fallback is quiet on purpose, and that's the risk: if the reply format
drifts, the run still completes with a fit card and every unit 4 criterion
still passes, but the extension has quietly turned back into "take the first
result". The parser expects a line starting `ID:`. A reply in markdown like
`**ID:** lst_006` doesn't match that and would fall back every time. That's
the failure this criterion exists to catch. I allow 1 miss in 10 because the
pick is a live call on the free tier, and a 503 that outlasts the retries
correctly falls back. Two or more fallbacks out of 10 means a format problem,
not bad luck. Asking for 10 of 10 would score the service's uptime instead of
my prompt.

---

## 3. The reason names a real wardrobe piece

In at least 8 of the tries where the model made the pick (`pick_fallback` is
`null`), `pick_reason` contains, ignoring case, the name of at least one item
in the example wardrobe, up to its first comma. For example
`baggy straight-leg jeans` for "Baggy straight-leg jeans, dark wash" or
`black combat boots`.

**Why this target:**
The reason is the only visible evidence that the pick looked at the wardrobe
at all. A reason like "this tee has a great vintage vibe" could have been
written without the wardrobe, and then the pick is just a second keyword
ranking. It's lower than criterion 2 because the check is a strict substring
match and the model paraphrases. "your baggy jeans" or "the combat boots" is a
fair reason that fails the check. The pick runs at temperature 0.0, so the same
query gives nearly the same reason both times. If one query's reason
paraphrases, it'll likely cost 2 tries, and 8 leaves room for exactly that. Below
8 would mean the prompt's "name at least one wardrobe piece by name" isn't
landing.

> **Tightened after the unit 5 before-run (3a):** In 10 of 10 tries, the
> reason argues for the item that was picked. `pick_reason` contains no other
> candidate's id and no word from another candidate's title. Words that also
> appear in the picked item's title or style tags, in the query, or in any
> wardrobe item name are ignored, because they don't point at a different
> listing.
>
> **Why tightened:** The original check passed reasons that argued *against*
> the pick. In run 1 the model picked `lst_019` (Platform Sneakers, White
> Chunky Sole) with the reason "The chunky white sneakers would clash with her
> existing chunky white sneakers, making lst_035 the better versatile choice".
> That scored PASS because "chunky white sneakers" is a wardrobe name. The
> criterion was supposed to show the pick used the wardrobe, and it couldn't
> tell a reason for the pick from a reason against it. 10 of 10, because a
> reason that contradicts the pick is a false statement shown to the user, and
> suggest_outfit then styles the item the model just argued against. This adds
> to the original criterion 3 without replacing it. Its target hasn't moved.

---

## 4. An empty wardrobe falls back to the first result without a model call for the pick

With `--empty-wardrobe` on 5 queries that match (the same five queries above,
once each), in 5 of 5 tries: `selected.id` equals the first search result's id,
`pick_fallback` is `"empty wardrobe, nothing to match against"`, the run still
ends with `status: "ok"` and a fit card, and `model_calls` is **2**
(suggest_outfit + create_fit_card only, with no call spent on the pick).

**Why this target:**
This is the extension's own bad input. "Pair with the most pieces they own"
means nothing when they own nothing, and asking the model anyway would spend a
request on a coin flip and could pick a worse keyword match for no reason.
The check runs before any model call, so the path is deterministic and 5 of 5
is the only honest target. `model_calls == 2` is what proves no request was
spent on the pick, since the item check alone would also pass if the model was
called and just happened to agree with the first result.

---

## 5. A failed run leaves a record, not an absence

With a bad API key and the cache off
(`AI201_CACHE=0 GEMINI_API_KEY=bad python app.py ask 'vintage graphic tee under $30' --trace`;
the key is set for that one command, and `load_dotenv` won't override it), in
5 of 5 tries:

- the command prints a `Couldn't finish: ... failed.` message and no Python
  traceback
- `pick_best_match` falls back (`pick_fallback` starts with
  `model call failed`) instead of ending the run
- the run ends at `suggest_outfit`, the first step that actually needs the
  model, with `fit_card` = `null`
- exactly one new line appears in `logs/runs.jsonl` with `status: "error"`, a
  non-empty `error` naming `suggest_outfit`, and a `duration_s`

**Why this target:**
Two things are new on this path. The extension added a model call before the
first one that used to fail, and the logging is supposed to capture failures.
If `pick_best_match` raised instead of falling back, the error would name the
wrong step. If the log were written only on success, a bad key would leave no
trace in the one file I'd check later. Everything on this path happens before
or instead of a model reply, so nothing about it is random. 5 of 5, and any
miss is a bug in my code, not the service.

---

### Self-check

| # | Target is a number or plainly visible? | Checkable without judgement? | Where it's read from | About the extension? | Bad path? |
|---|---|---|---|---|---|
| 1 | 10 of 10 | yes, id in a list | log `selected`, `candidates` | yes | no |
| 2 | 9 of 10 | yes, field is null or not | log `pick_fallback` | yes | partly (fallback rate) |
| 3 | 8 of 10 | yes, case-insensitive substring | log `pick_reason` vs wardrobe names | yes | no |
| 4 | 5 of 5 | yes, id, string, count | log `selected`, `pick_fallback`, `model_calls` | yes | yes (empty input) |
| 5 | 5 of 5 | yes, output text and log line | terminal + log `status`, `error` | yes, plus logging | yes (bad key) |

None of the five turns on "works", "good", "reliable" or "fast". Each one
names the field it's scored from, so a reader could score a try from the
log file alone.
