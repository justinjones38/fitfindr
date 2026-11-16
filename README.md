# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->
A user types what clothes that they are looking for. Then FitFindr searches for a set of 2nd hand listing for the best match at the price and size of the user. It then suggests outfits that already fits with the user's wardrobe or gives general styling advice if the wardrobe is empty. If nothing matches, then it stops and recommends changes to the user, such as increasing the price limit or dropping the size


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** - Search the listings data for items that match the description, size and max price
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
  - description (str)
  - size (str)
  - max_prize (float)
- **Returns:** - it returns a list of dictionaries, with the best match first. At most it returns 10, with the limit set by SEARCH_RESULT_LIMIT in config.py
- **When it has nothing:** - it returns an empty list

### `suggest_outfit`

- **What it does:** - Given an item and wadrobe, it suggest couple of outfits
- **Inputs:** 
  - new_item (dict)
  - wardrobe (dict)
- **Returns:** - returns a non-empty string with outfit suggestions
- **When it has nothing:** 
returns general styling advice

### `create_fit_card`

- **What it does:** - write a short caption that someone what post about their find
- **Inputs:**
  - outfit suggestion (string)
  - new_item (listing dict) 
- **Returns:** - 2 to 4 sentence caption
- **When it has nothing:** - return a descriptive message 

### `pick_best_match` (added in unit 5)

- **What it does:** - From the top 3 search results, picks the listing that pairs with the most pieces in the user's wardrobe (one model call)
- **Inputs:**
  - candidates (list[dict]) — the search_listings results, best keyword match first
  - wardrobe (dict) — with an 'items' list, may be empty
- **Returns:** - a dict: `item` (the chosen listing dict, always one of the top 3), `reason` (one sentence naming a wardrobe piece), `fallback` (None if the model picked, otherwise why the first result was used)
- **When it has nothing:** - it never raises. With one candidate, an empty wardrobe, a failed model call, or a reply whose ID isn't in the top 3, it returns the first result and sets `fallback`. With an empty list, `item` is None, but the loop never calls it with an empty list.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:**
If search_listings returns an empty list, put a message in session["error"] that says what was searched and what to loosen (raise the price limit, drop the size, or use broader keywords), then stop, without calling suggest_outfit or create_fit_card. Otherwise, pass the results and the wardrobe to pick_best_match, use its pick as selected_item, and go on to suggest_outfit, then create_fit_card. (Before unit 5 this step just took the first result.)


**Where it lives:** `agent.py::run_agent`

**How the query is parsed:**
Regex, in agent.py::parse_query. One pattern finds the price ("under $30", "below 60", "$25") and becomes max_price. Another finds "size X" ("size M", "size US 9", and "size medium" → M) and becomes size. Filler words like "looking for a" are removed, and what's left is the description. Anything not found is None, so the search skips that filter.


**What moves through the session:** <!-- which fields, in what order -->
query → parsed (description, size, max_price) → search_results → branch: empty sets error and stops, otherwise it continues → selected_item + pick (pick_best_match's choice from the top 3, with its reason and fallback) → outfit_suggestion → fit_card.



---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask new green tea under $30

[1] parse_query
      in:  new green  tee under 30$
      out: {'description': 'new green tee', 'size': None, 'max_price': 30.0}
[2] search_listings
      in:  {'description': 'new green tee', 'size': None, 'max_price': 30.0}
      out: 9 items: Y2K Baby Tee — Butterfly Print, Vintage Polo Shirt — Forest Green, Vintage Band Tee — Faded Grey … +6 more
      →    branch: results found, continuing
[3] select_item
      in:  first of search_results
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  {'new_item': 'Y2K Baby Tee — Butterfly Print', 'wardrobe_items': 10}
      out: Hey babe! Oh, you *totally* need to grab that butterfly baby tee—it's such a gorgeous Y2K dream and looks to b…
[5] create_fit_card
      in:  {'outfit': 'Hey babe! Oh, you *totally* need to grab…', 'new_item': 'Y2K Baby Tee — Butterfly Print'}
      out: Scored this dreamy butterfly baby tee on Depop for just $18 and I am obsessed. I threw it on with my baggy dar…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Hey babe! Oh, you *totally* need to grab that butterfly baby tee—it's such a gorgeous Y2K dream and looks to be in amazing shape! Here are two super cute ways to style it using pieces you already own:

**Look 1: Streetwear Sweetheart**
Pair the Y2K Baby Tee — Butterfly Print with your baggy straight-leg jeans, dark wash, and finish the fit with chunky white sneakers. Add your black crossbody bag for an effortless, everyday look that balances the fitted top with baggy denim!

**Look 2: Effortless Contrast**
Tuck the Y2K Baby Tee — Butterfly Print into your wide-leg khaki trousers, and lace up your black combat boots to add a little edge to the sweet butterfly print. So chic!

  Fit card: Scored this dreamy butterfly baby tee on Depop for just $18 and I am obsessed. I threw it on with my baggy dark wash jeans and chunky white sneakers for the ultimate effortless streetwear vibe. It fits like a glove and brings all the best Y2K energy to my everyday wardrobe.
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```
[{'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Fadedgrey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on thechest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand':None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under agraphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M','condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a longtee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}]
```
$ python -c "from tools import suggest_outfit; ..."

```
Hey friend! Oh, those vintage Levi's 501s are an absolute thrift store holy grail—you *totally* need to grab them! 

Here are two effortless ways to style your new find using pieces you already own:

**Look 1: Effortless & Edgy**
Pair your new Levi's with the **Black cropped zip hoodie** for that cool-girl proportion play. Throw on the **Chunky white sneakers** and finish it all off with your **Black crossbody bag**. 

**Look 2: Cozy Classic**
Tuck the **White ribbed tank top** into the jeans, cinch it with the **Brown leather belt**, and layer the **Oversized grey crewneck sweatshirt** right on top.Step into your **Black combat boots** for the ultimate vintage-meets-streetwearvibe. 

Go snag those jeans!
```
$ python -c "from tools import create_fit_card; ..."

```
Scored these vintage Levi's 501 jeans on depop for just $38 and they fit like an absolute dream. I threw them on with my favorite white sneakers for a classic,effortless streetwear vibe that I'll probably wear three times a week. Nothing beats a good medium wash denim find.
---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* - to help complete the search listing function and the other tool function
- *What came back:* - the corrected functions
- *What I changed:* - I corrected the tool functions

**Moment 2**

- *What I asked for:* - Help with getting the initial project files installed and initial project with Git Bash
- *What came back:* - It gave me the correct commands to set the project with Git Bash
- *What I changed:* - I just used the correct commands with Git Bash to set up the projects

**Moment 3**
- *What I asked for:* - to give advice on changes to prevent 503 error in Criterion 1 
- *What came back:* - it helped refactor to introduce a loop so that 503 error are treated as temporary errors
- *What I changed:* - 503 error no longer crashes the code. 

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET | 
| 3. The fit card names the same item as session["selected_item"]: its price and platform match selected_item["price"] and selected_item["platform"]. | 5 of 5  | PASS | PASS | PASS | PASS | PASS | MET |
| 4. The fit card mentions the item's price and platform, and is 2 to 4 sentences long. | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 5. Price ceiling: every item in search_results has price <= max_price. | 5 of 5 | PASS | PASS | PASS | PASS | PASS  | MET |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

**File:** `results/run_2026-10-07_1452_before.md` (scenario "matching query completes", try 3)  
**Function:** `agent.py::run_agent`, run by `run_eval.py::main`. The fit card comes from `tools.py::create_fit_card`.

````
**Try 3** 

- stopped early: no
- selected_item: Vintage Band Tee — Faded Grey ($19.0, depop)
- search_results: 10
- search_result prices: [19.0, 24.0, 18.0, 26.0, 20.0, 18.0, 25.0, 12.0, 14.0, 15.0]

Outfit suggestion:

```
Hey friend! That faded vintage band tee is an absolute holy grail find for your wardrobe. It’s got that effortless, broken-in grunge vibe that looks cool with literally everything. 

Here are two ways to style your new treasure:

**Outfit 1: Effortless Streetwear**
Pair the band tee with your *Baggy straight-leg jeans, dark wash*. Add the *Black combat boots* for that edgy, 90s rockstar finish, and sling the *Black crossbody bag* across your chest. 

**Outfit 2: Layered Grunge**
Wear the tee over your *White ribbed tank top* (letting the white peek out the bottom), tucked into the *Wide-leg khaki trousers*. Cinch it with the *Brown leather belt* and finish with *Chunky white sneakers*. 

You're going to wear this piece out!
```

Fit card:

```
Scored this faded grey vintage band tee on Depop for just $19 and it has the absolute best broken-in grunge feel. I threw it on with some baggy dark wash jeans and black combat boots for an effortless 90s rockstar look. It is definitely going to be on heavy rotation in my wardrobe.
```

Trace:

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print … +7 more
      →    branch: results found, continuing
[3] select_item
      in:  first of search_results
      out: Vintage Band Tee — Faded Grey ($19.0, depop)
[4] suggest_outfit
      in:  {'new_item': 'Vintage Band Tee — Faded Grey', 'wardrobe_items': 10}
      out: Hey friend! That faded vintage band tee is an absolute holy grail find for your wardrobe. It’s got that effort…
[5] create_fit_card
      in:  {'outfit': 'Hey friend! That faded vintage band tee …', 'new_item': 'Vintage Band Tee — Faded Grey'}
      out: Scored this faded grey vintage band tee on Depop for just $19 and it has the absolute best broken-in grunge fe…
```
````

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->



| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools  | 4 of 5 | MET (5/5) | Every matching run completed all three tools  |
| 2  | An impossible query stops before the second tool | 5 of 5 | MET (5/5) | Every queries stopped running early if it could not matcg  |
| 3 | The fit card names the same item as session["selected_item"]: its price and platform match selected_item["price"] and selected_item["platform"].  | 5 of 5 | MET (5/5) | Every try mentioned the selected item in the fit card |
| 4  | The fit card mentions the item's price and platform, and is 2 to 4 sentences long. | 4 of 5 | MET (5/5) | Every fit card mentioned the selected item's price, the platform where the item was purchased, and was between 2 to 4 sentences |
| 5 | Price ceiling: every item in search_results has price <= max_price. | 5 of 5 | MET (5/5) | Every item in the search_results for all tries was less than the max_price that the user mentioned |


**Diagnoses**
No criterion missed in this run.

So the question is which target was too easy.

Criterion 4 passed on all 30 fit cards across six different scenarios. Every card had the price, platform, and the required sentences because the prompt in tools.py mentioned the names and prices explicitly. Tighter Target 5 of 5, across 5 different items

Criterion 3 was also too easy. It passed all 5 tries but used the same search queury and selected the same first result. Therefore, it never could have caught the wrong item being passed along. For future tests, I would like to use several different queries. Tigher Target: across 5 different queries, all fit cards name the selected item's price and platform


For the other criterion
Criterion 2 and 5 were deterministic. So 5/5 was expected for both. A miss would have been a bug in the code.

Criterion 1 did pass 5/5, but it missed on an earlier run. Try 5 crashed with a 503 error code from the model. The model call in generate.py returned a 503 (high demand). For this run, there was no 503 error, but I did not fix the problem.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask "vintage under 60" --trace
[1] parse_query
      in:  vintage under 60
      out: {'description': 'vintage', 'size': None, 'max_price': 60.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage', 'size': None, 'max_price': 60.0}
      out: 10 items: Vintage Polo Shirt — Forest Green, Vintage Band Tee — Faded Grey, Oversized Crewneck Sweatshirt — Vintage Navy … +7 more
      →    branch: results found, continuing
[3] select_item
      in:  first of search_results
      out: Vintage Polo Shirt — Forest Green ($18.0, thredUp)
[4] suggest_outfit
      in:  {'new_item': 'Vintage Polo Shirt — Forest Green', 'wardrobe_items': 10}
      out: Hey friend! Oh, you *totally* need to grab that forest green Ralph Lauren polo—it is such a timeless staple an…
[5] create_fit_card
      in:  {'outfit': 'Hey friend! Oh, you *totally* need to gr…', 'new_item': 'Vintage Polo Shirt — Forest Green'}
      out: Scored this vintage Ralph Lauren forest green polo on thredUp for just $18, and I am obsessed with the color. …

  Found:    Vintage Polo Shirt — Forest Green — $18.0 on thredUp

  Outfit:   Hey friend! Oh, you *totally* need to grab that forest green Ralph Lauren polo—it is such a timeless staple and the color is gorgeous. 

Here are two fun ways to style it using pieces you already own:

**Outfit 1: Casual Streetwear Vibe**
Pair the vintage polo shirt with your baggy straight-leg jeans, and cinch them together using the brown leather belt. Slip on your chunky white sneakers, and toss the black crossbody bag over your shoulder for an easy, cool-girl everyday look.

**Outfit 2: Earthy & Relaxed**
Tuck the vintage polo shirt into your wide-leg khaki trousers, accented by the brown leather belt. Finish this classic, preppy outfit with your black combat boots to add a little bit of edge!

  Fit card: Scored this vintage Ralph Lauren forest green polo on thredUp for just $18, and I am obsessed with the color. I tucked it into wide-leg khaki trousers with a leather belt and added black combat boots for a preppy look with a little bit of edge. Such a timeless staple that I'm going to wear on repeat this season!

2 model calls this session, 701 prompt + 236 output tokens
```

**Empty search**

```
$ python app.py ask "..." --trace
[1] parse_query
      in:  ...
      out: {'description': '', 'size': None, 'max_price': None}
[2] search_listings (via MCP)
      in:  {'description': '', 'size': None, 'max_price': None}
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit

  I couldn't tell what kind of item you want from '...'. Name the item, like 'denim jacket', 'graphic tee', 'jeans', or 'sneakers' — this shop carries tops, bottoms, outerwear, shoes, and accessories. You can add a size and a price too, e.g. 'graphic tee size M under $30'.

0 model calls this session
```

<!-- **On the MCP move:** what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

run_agent now calls call_tool("search_listings", {...}) from mcp_client instead of importing the function. The results came back as the same list of dicts, and nothing else changed.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**
I changed generate.py to where 503 error now counts as a temporary error. It will wait and retry then. When retries run out, generate() will raise a ModelUnvailable instead of Runtime Error

**Which failure it was meant to fix:**
It was meant to fix the 503 crash in criterion 1 during the first practice run that I mentioned in the diagnoses.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET | 
| 3. The fit card names the same item as session["selected_item"]: its price and platform match selected_item["price"] and selected_item["platform"]. | 5 of 5  | PASS | PASS | PASS | PASS | PASS | MET |
| 4. The fit card mentions the item's price and platform, and is 2 to 4 sentences long. | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 5. Price ceiling: every item in search_results has price <= max_price. | 5 of 5 | PASS | PASS | PASS | PASS | PASS  | MET |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->

All runs passed and model failures now end the run with a message and a trace line instead of a crash. In the practice run, there was a crash. For this run, all runs that were supposed to crash ended with a message and a trace line.


---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

Criterion 3 used the same query and it could never catch the wrong item.

The 503 retry error is not verified because no 503 happended during the last run.

select_item always take the first result and does not check whether it is still broken.

<!-- ═══════════════════════ UNIT 5 — THE EXTENSION ═══════════════════════ -->

---

## Capstone

FitFindr, extended with one new capability (`pick_best_match`), then run,
logged, measured, tested and improved.

### The Shape

**Shape C: Extend one capability.**

I'm adding a fourth tool, `pick_best_match`, that sits between `search_listings` and `suggest_outfit` in `agent.py::run_agent`. Right now the loop always takes the first search result as `selected_item`, so the choice depends only on keyword score and ignores the user's wardrobe. That's the gap I listed under What's Still Broken. The new tool takes the top 3 results and the wardrobe, makes one model call to pick the listing that goes with the most wardrobe pieces, and returns that listing's `id` with a one-sentence reason. The loop uses that listing as `selected_item` and adds a `pick_best_match` trace line. If the model returns an `id` that isn't in the top 3, or the call fails, the tool falls back to the first result and the trace says so. The empty-search branch doesn't change: if there are no results, the agent stops before this tool runs. I'll know it works if the chosen item is always one of the real top 3 results, and if its reason names at least one actual wardrobe item.

#### Out of scope

- **I'm not changing how `search_listings` scores or filters results.** The keyword scoring in `tools.py` and the price and size filters stay as they are. The new tool only re-orders what search already returns, so criterion 5 (price ceiling) can't break.
- **I'm not moving the other tools to MCP.** Only `search_listings` goes through `mcp_server.py`. `pick_best_match` will be a plain function in `tools.py`, like `suggest_outfit` and `create_fit_card`.
- **I'm not rebuilding the interface or the prompts for the other tools.** `app.py`, the `suggest_outfit` prompt and the `create_fit_card` prompt stay the same. The only new output is one extra trace line.

#### Size check

| Piece | Estimate |
|---|---|
| `pick_best_match` in `tools.py` (prompt, model call, id check, fallback) | ~35 min |
| Wire it into `run_agent` with a trace step, between `select_item` and `suggest_outfit` | ~15 min |
| Per-tool terminal test, plus one forced-fallback test (bad id or failed call) | ~20 min |
| Buffer for prompt tweaks | ~15 min |
| **Total** | **~85 min** |

This fits under the ninety-minute limit because it's one function, one model call and one new branch (fall back to the first result), and it reuses `generate.py` and the existing trace. If it starts to run long, I'll cut the "reason" sentence and return only the `id`.

#### Build notes

- **Where it lives:** `tools.py::pick_best_match`, called from the `select` step of `agent.py::run_agent`. The pick's reason and fallback go in `session["pick"]`.
- **One change from the plan:** the `pick_best_match` trace line *replaces* the old `select_item` line instead of being added after it. Both lines would have shown the same choice, so the trace stays at 5 steps on the happy path and 2 on the empty path.
- **Fallbacks tested offline** (with `generate` stubbed): empty list, one candidate, empty wardrobe, a good pick (3rd result chosen), an id outside the top 3, a reply with no ID line, and `ModelUnavailable`. Each one returned the expected item and `fallback` value.
- **Regression check:** `python run_eval.py --tries 1 --label smoke` (`results/run_2026-11-15_1937_smoke.md`). The impossible query still stops at search with 0 model calls, the empty wardrobe run completes, and every fit card names the selected item's actual price and platform in 3 sentences.

**The capability changing the result:** on the same query, the old loop picked `lst_033` (the first result). The new step picked `lst_006`, the second result, based on the wardrobe:

```
$ python app.py ask "vintage graphic tee under $30" --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print … +7 more
      →    branch: results found, continuing
[3] pick_best_match
      in:  {'candidates': ['lst_033', 'lst_006', 'lst_002'], 'wardrobe_items': 10}
      out: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
      →    picked: The graphic tee pairs effortlessly with the baggy straight-leg jeans, black combat boots, and vintage black denim jacket for a cohesive grunge streetwear look.
[4] suggest_outfit
      in:  {'new_item': 'Graphic Tee — 2003 Tour Bootleg Style', 'wardrobe_items': 10}
      out: Hey friend! Oh, I *love* a good 2003 tour bootleg tee—such an easy way to add instant edge to your wardrobe.  …
[5] create_fit_card
      in:  {'outfit': 'Hey friend! Oh, I *love* a good 2003 tou…', 'new_item': 'Graphic Tee — 2003 Tour Bootleg Style'}
      out: Scored this vintage 2003 tour bootleg tee on Depop for just $24, and it has the absolute best faded wash. I th…
```

Fallback visible in the trace (empty wardrobe):

```
[3] pick_best_match
      in:  {'candidates': ['lst_007', 'lst_016', 'lst_038'], 'wardrobe_items': 0}
      out: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
      →    fallback: empty wardrobe, nothing to match against, using first result
```

---

### The Run Path

**Local, with logs.** FitFindr is not hosted. The exact start commands, what
the environment needs, and where the logs go are in
[RUNNING.md](RUNNING.md#run-it-locally-with-logs-unit-5). The short version:

```
python -m venv .venv  →  activate  →  pip install -r requirements.txt
copy .env.example .env (paste a Gemini key)  →  python test.py
python app.py ask 'vintage graphic tee under $30' --trace
python runlog.py                      # read back the last 10 run records
```

**Testing the instructions on myself:** I cloned the repo into a new, empty
folder, checked out `working-branch`, and followed RUNNING.md line by line in
Git Bash (Python 3.11.9). Before the key was pasted, `test.py` failed with
8 passed, 1 failed, as expected. After that it was 10 passed, and the first
`ask` completed all 5 steps and created `logs/runs.jsonl`. What a reader would
actually have hit:

1. **The code wasn't on GitHub.** I cloned from my local repo because none of
   the unit 5 commits were pushed yet. `origin/working-branch` was still at
   `aa3038d`, so a reader cloning the URL in RUNNING.md would get no
   `pick_best_match`, no `runlog.py` and no `measure_cost.py`. Fix: push
   `working-branch`. RUNNING.md also says to `git checkout working-branch`,
   because `main` doesn't have this either.
2. **A bad-key test passes with a bad key.** With the cache on, every answer
   came from `.cache/`, the run printed a fit card, and nothing failed. I added
   that to RUNNING.md's troubleshooting table, and the criteria now require
   `AI201_CACHE=0`.
3. **The run count was wrong.** I'd guessed "about 4 model calls a run".
   The measurement says 3. Fixed.

I only tested the Git Bash commands. The PowerShell block is the same
sequence with PowerShell syntax, and I didn't run it from a clean clone.

---

### Instrumentation

Every call to `agent.py::run_agent` writes one JSON line to `logs/runs.jsonl`
through `runlog.py`, whether the run succeeded, stopped on an empty search,
ended on a model/MCP error, or crashed. A crash is logged, then re-raised.
Because the logging sits in `run_agent` itself, `app.py`, `run_eval.py`,
`serve.py` and `measure_cost.py` all write records, tagged by `source`.

Fields: `ts`, `run_id`, `source`, `query` (input), `wardrobe_items`, `parsed`,
`status` (`ok` / `no_results` / `error` / `crash`), `error`, `n_results`,
`candidates`, `selected`, `pick_fallback`, `pick_reason`, `fit_card` (output),
`duration_s`, `model_calls`, `cache_hits`, `prompt_tokens`, `output_tokens`.
The pick fields are there so the unit 5 criteria can be scored from the log
alone.

**14 entries, pasted from `logs/runs.jsonl`** (`python runlog.py -n 14`):

- Lines 1–10 are the cost measurement (`source: "measure"`, cache off).
- Line 11 is the bad-key test with the cache **on**. It came back `ok` with
  `cache_hits: 3` and `model_calls: 0`: the false pass described above.
- Line 12 is **a rejected input** (`...`), `status: "no_results"`, 0 model calls.
- Line 13 is **an impossible query**, `status: "no_results"`, 0 model calls.
- Line 14 is **the failed run**: a bad key with the cache off,
  `status: "error"`. `pick_best_match` fell back
  (`"model call failed (ModelUnavailable)"`), and the run stopped at
  `suggest_outfit` with `fit_card: null`. Both requests were rejected, so
  0 tokens were used.

```
{"ts": "2026-11-16T01:40:46+00:00", "run_id": "1048be48", "source": "measure", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "status": "ok", "error": null, "n_results": 10, "candidates": ["lst_033", "lst_006", "lst_002"], "selected": {"id": "lst_006", "title": "Graphic Tee — 2003 Tour Bootleg Style", "price": 24.0, "platform": "depop"}, "pick_fallback": null, "pick_reason": "The graphic tee pairs effortlessly with the baggy straight-leg jeans and black combat boots for a cohesive grunge and streetwear look.", "fit_card": "Scored this 2003 tour bootleg tee on Depop for just $24 and I'm obsessed. Threw it on with my baggy straight-leg jeans, black combat boots, and a vintage denim jacket for the ultimate grungy streetwear moment. Total wardrobe goldmine.", "duration_s": 9.02, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1207, "output_tokens": 280}
{"ts": "2026-11-16T01:40:55+00:00", "run_id": "a2252401", "source": "measure", "query": "denim jacket under $60", "wardrobe_items": 10, "parsed": {"description": "denim jacket", "size": null, "max_price": 60.0}, "status": "ok", "error": null, "n_results": 7, "candidates": ["lst_007", "lst_016", "lst_038"], "selected": {"id": "lst_007", "title": "Denim Jacket — Light Wash, Cropped", "price": 42.0, "platform": "poshmark"}, "pick_fallback": null, "pick_reason": "The light wash cropped denim jacket pairs effortlessly with the white ribbed tank top and chunky white sneakers for a classic streetwear look.", "fit_card": "Scored this vintage Wrangler cropped denim jacket on Poshmark for just $42 and I am completely obsessed. I threw it on over wide-leg khaki trousers and combat boots for the ultimate effortless vintage look. It adds such a cool streetwear vibe to literally everything in my closet.", "duration_s": 4.24, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1208, "output_tokens": 283}
{"ts": "2026-11-16T01:40:59+00:00", "run_id": "a879e0d7", "source": "measure", "query": "cargo pants under $40", "wardrobe_items": 10, "parsed": {"description": "cargo pants", "size": null, "max_price": 40.0}, "status": "ok", "error": null, "n_results": 2, "candidates": ["lst_011", "lst_005"], "selected": {"id": "lst_011", "title": "Low-Rise Cargo Pants — Khaki", "price": 27.0, "platform": "poshmark"}, "pick_fallback": null, "pick_reason": "The low-rise khaki cargo pants pair well with the white ribbed tank top and black combat boots for a complete streetwear look.", "fit_card": "Scored these low-rise khaki cargo pants on Poshmark for just $27, and I am so obsessed with the lived-in look. I paired them with a black cropped zip hoodie and chunky white sneakers to lean into that ultimate early-2000s streetwear vibe. It feels effortless, comfortable, and honestly just so fun to wear.", "duration_s": 4.02, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1159, "output_tokens": 302}
{"ts": "2026-11-16T01:41:03+00:00", "run_id": "0c9cd836", "source": "measure", "query": "sneakers under $80", "wardrobe_items": 10, "parsed": {"description": "sneakers", "size": null, "max_price": 80.0}, "status": "ok", "error": null, "n_results": 2, "candidates": ["lst_035", "lst_019"], "selected": {"id": "lst_035", "title": "Low-Top Canvas Sneakers — Off-White", "price": 20.0, "platform": "poshmark"}, "pick_fallback": null, "pick_reason": "The off-white canvas sneakers pair well with the white ribbed tank top for a clean, minimal look.", "fit_card": "Scored these classic off-white canvas sneakers on Poshmark for just $20, and they are already my new daily go-to. I love throwing them on with baggy dark-wash denim, a simple ribbed tank, and an oversized crewneck for the ultimate comfy streetwear vibe.", "duration_s": 3.93, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1150, "output_tokens": 290}
{"ts": "2026-11-16T01:41:07+00:00", "run_id": "be3bf5a7", "source": "measure", "query": "y2k top under $25", "wardrobe_items": 10, "parsed": {"description": "y2k top", "size": null, "max_price": 25.0}, "status": "ok", "error": null, "n_results": 10, "candidates": ["lst_017", "lst_002", "lst_035"], "selected": {"id": "lst_017", "title": "Mesh Long-Sleeve Top — Black", "price": 15.0, "platform": "depop"}, "pick_fallback": null, "pick_reason": "The black mesh long-sleeve top can be layered underneath the white ribbed tank top for a stylish textured contrast.", "fit_card": "Scored this black mesh long-sleeve top on Depop for just $15, and it is the ultimate grunge layering piece. I threw it under a white ribbed tank with my baggy jeans and combat boots for that effortless 90s edge. Honestly, the sheer sleeves just pull the whole look together.", "duration_s": 53.92, "model_calls": 4, "cache_hits": 0, "prompt_tokens": 1178, "output_tokens": 273}
{"ts": "2026-11-16T01:42:01+00:00", "run_id": "d1f6632a", "source": "measure", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "status": "ok", "error": null, "n_results": 10, "candidates": ["lst_033", "lst_006", "lst_002"], "selected": {"id": "lst_006", "title": "Graphic Tee — 2003 Tour Bootleg Style", "price": 24.0, "platform": "depop"}, "pick_fallback": null, "pick_reason": "The graphic tee pairs effortlessly with the baggy straight-leg jeans, black cropped zip hoodie, and black combat boots for a cohesive streetwear and grunge look.", "fit_card": "Scored this 2003 tour bootleg tee on Depop for just $24, and it instantly brought the ultimate grunge energy to my closet. I threw it on with baggy dark wash jeans and black combat boots for some heavy streetwear edge, then draped my favorite denim jacket over the shoulders. It feels like a total 2000s icon moment without even trying.", "duration_s": 3.85, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1203, "output_tokens": 302}
{"ts": "2026-11-16T01:42:05+00:00", "run_id": "9baad9ea", "source": "measure", "query": "denim jacket under $60", "wardrobe_items": 10, "parsed": {"description": "denim jacket", "size": null, "max_price": 60.0}, "status": "ok", "error": null, "n_results": 7, "candidates": ["lst_007", "lst_016", "lst_038"], "selected": {"id": "lst_007", "title": "Denim Jacket — Light Wash, Cropped", "price": 42.0, "platform": "poshmark"}, "pick_fallback": null, "pick_reason": "The light wash cropped denim jacket pairs effortlessly with the white ribbed tank top and baggy straight-leg jeans for a classic double-denim look.", "fit_card": "Scored this vintage Wrangler cropped denim jacket on Poshmark for just $42 and I am completely obsessed. I threw it on over a black zip hoodie with some baggy dark wash jeans and chunky sneakers for the ultimate textured streetwear vibe. It fits like an absolute dream and is about to be my everyday outer layer.", "duration_s": 3.46, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1160, "output_tokens": 247}
{"ts": "2026-11-16T01:42:09+00:00", "run_id": "b954d01f", "source": "measure", "query": "cargo pants under $40", "wardrobe_items": 10, "parsed": {"description": "cargo pants", "size": null, "max_price": 40.0}, "status": "ok", "error": null, "n_results": 2, "candidates": ["lst_011", "lst_005"], "selected": {"id": "lst_011", "title": "Low-Rise Cargo Pants — Khaki", "price": 27.0, "platform": "poshmark"}, "pick_fallback": null, "pick_reason": "The low-rise khaki cargo pants pair well with the white ribbed tank top and black combat boots for a complete streetwear look.", "fit_card": "Scored these khaki low-rise cargos on Poshmark for $27 and they are the ultimate Y2K streetwear dream. I threw them on with my black cropped zip hoodie and chunky white sneakers for a super easy, edgy look. It totally nails that nostalgic 2000s vibe without even trying.", "duration_s": 4.38, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1141, "output_tokens": 276}
{"ts": "2026-11-16T01:42:13+00:00", "run_id": "430067ff", "source": "measure", "query": "sneakers under $80", "wardrobe_items": 10, "parsed": {"description": "sneakers", "size": null, "max_price": 80.0}, "status": "ok", "error": null, "n_results": 2, "candidates": ["lst_035", "lst_019"], "selected": {"id": "lst_035", "title": "Low-Top Canvas Sneakers — Off-White", "price": 20.0, "platform": "poshmark"}, "pick_fallback": null, "pick_reason": "The off-white low-top canvas sneakers offer a minimal, versatile basic that will easily pair with the white ribbed tank top and baggy straight-leg jeans.", "fit_card": "Scored these off-white canvas sneakers on Poshmark for just $20, and they are already my new everyday go-to. I love how effortless they look with baggy dark wash jeans and a black cropped zip hoodie for an easy streetwear vibe. Such a solid closet basic that I know I'll wear with everything!", "duration_s": 3.51, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1115, "output_tokens": 274}
{"ts": "2026-11-16T01:42:16+00:00", "run_id": "6352139c", "source": "measure", "query": "y2k top under $25", "wardrobe_items": 10, "parsed": {"description": "y2k top", "size": null, "max_price": 25.0}, "status": "ok", "error": null, "n_results": 10, "candidates": ["lst_017", "lst_002", "lst_035"], "selected": {"id": "lst_017", "title": "Mesh Long-Sleeve Top — Black", "price": 15.0, "platform": "depop"}, "pick_fallback": null, "pick_reason": "The black mesh long-sleeve top can be layered under the white ribbed tank top and paired with the baggy straight-leg jeans for a complete grunge-inspired look.", "fit_card": "Scored this black mesh long-sleeve top on Depop for just $15, and I am already obsessed with it. I threw it on over a white ribbed tank and baggy jeans for the ultimate 90s grunge look. It adds the best sheer texture to any outfit and I know I'm going to wear it all the time.", "duration_s": 44.95, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1189, "output_tokens": 303}
{"ts": "2026-11-16T01:43:17+00:00", "run_id": "c61d646e", "source": "cli", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "status": "ok", "error": null, "n_results": 10, "candidates": ["lst_033", "lst_006", "lst_002"], "selected": {"id": "lst_006", "title": "Graphic Tee — 2003 Tour Bootleg Style", "price": 24.0, "platform": "depop"}, "pick_fallback": null, "pick_reason": "The graphic tee pairs effortlessly with the baggy straight-leg jeans, black combat boots, and vintage black denim jacket for a cohesive grunge streetwear look.", "fit_card": "Scored this vintage 2003 tour bootleg tee on Depop for just $24, and it has the absolute best faded wash. I threw it on with baggy dark-wash jeans and my chunky combat boots for that effortless 90s grunge look. It adds instant edge to pretty much anything in my closet!", "duration_s": 2.41, "model_calls": 0, "cache_hits": 3, "prompt_tokens": 0, "output_tokens": 0}
{"ts": "2026-11-16T01:43:20+00:00", "run_id": "9609d936", "source": "cli", "query": "...", "wardrobe_items": 10, "parsed": {"description": "", "size": null, "max_price": null}, "status": "no_results", "error": "I couldn't tell what kind of item you want from '...'. Name the item, like 'denim jacket', 'graphic tee', 'jeans', or 'sneakers' — this shop carries tops, bottoms, outerwear, shoes, and accessories. You can add a size and a price too, e.g. 'graphic tee size M under $30'.", "n_results": 0, "candidates": null, "selected": null, "pick_fallback": null, "pick_reason": null, "fit_card": null, "duration_s": 2.18, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0}
{"ts": "2026-11-16T01:43:23+00:00", "run_id": "d9700296", "source": "cli", "query": "designer ballgown size XXS under $5", "wardrobe_items": 10, "parsed": {"description": "designer ballgown", "size": "XXS", "max_price": 5.0}, "status": "no_results", "error": "Nothing matched 'designer ballgown' in size XXS under $5. To find something, raise your price limit, or drop the size filter, or try broader keywords (e.g. 'tee' instead of 'vintage band tee').", "n_results": 0, "candidates": null, "selected": null, "pick_fallback": null, "pick_reason": null, "fit_card": null, "duration_s": 1.93, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0}
{"ts": "2026-11-16T01:43:30+00:00", "run_id": "8c234ff5", "source": "cli", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "status": "error", "error": "Couldn't finish: suggest_outfit failed. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.", "n_results": 10, "candidates": ["lst_033", "lst_006", "lst_002"], "selected": {"id": "lst_033", "title": "Vintage Band Tee — Faded Grey", "price": 19.0, "platform": "depop"}, "pick_fallback": "model call failed (ModelUnavailable)", "pick_reason": "top keyword match", "fit_card": null, "duration_s": 5.94, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0}
```

I didn't trigger a `crash` record. Every failure I could cause on purpose
(bad key, empty input, impossible query) is caught inside the loop and ends as
`error` or `no_results`. The `crash` path in `run_agent` (log, then re-raise)
is there for anything the loop doesn't catch, like `trace.check_iterations`
going past `MAX_ITERATIONS`, and it's untested.

---

### What It Costs

**One full FitFindr run costs 3 model calls and about 1,454 tokens
(1,171 prompt + 283 output), and takes a median 4.1 seconds.** The mean is
13.5 seconds, pulled up by rate-limit waits.

**How I measured it:** `python measure_cost.py` ran the whole agent 10 times
with the response cache off (`AI201_CACHE=0`, set inside the script before
`config` loads, and asserted), so every call was a real request. The queries
rotated through five that all match (`vintage graphic tee under $30`,
`denim jacket under $60`, `cargo pants under $40`, `sneakers under $80`,
`y2k top under $25`), twice each, with the example wardrobe, so every run took
the full path: search → `pick_best_match` → `suggest_outfit` →
`create_fit_card`. The numbers come from each run's log record:
- `model_calls` and the token fields are differences in `generate.py`'s
  counters before and after the run.
- The tokens are what the service reported in each response's
  `usage_metadata`, not an estimate.
- `duration_s` is `time.perf_counter()` around `run_agent`.

The script averaged the 10 records. Model: `gemini-3.5-flash-lite`, 2026-11-16.

| # | run_id | query | picked | model calls | prompt tok | output tok | total tok | seconds |
|---|---|---|---|---|---|---|---|---|
| 1 | `1048be48` | vintage graphic tee under $30 | lst_006 | 3 | 1207 | 280 | 1487 | 9.02 |
| 2 | `a2252401` | denim jacket under $60 | lst_007 | 3 | 1208 | 283 | 1491 | 4.24 |
| 3 | `a879e0d7` | cargo pants under $40 | lst_011 | 3 | 1159 | 302 | 1461 | 4.02 |
| 4 | `0c9cd836` | sneakers under $80 | lst_035 | 3 | 1150 | 290 | 1440 | 3.93 |
| 5 | `be3bf5a7` | y2k top under $25 | lst_017 | 4 | 1178 | 273 | 1451 | 53.92 |
| 6 | `d1f6632a` | vintage graphic tee under $30 | lst_006 | 3 | 1203 | 302 | 1505 | 3.85 |
| 7 | `9baad9ea` | denim jacket under $60 | lst_007 | 3 | 1160 | 247 | 1407 | 3.46 |
| 8 | `b954d01f` | cargo pants under $40 | lst_011 | 3 | 1141 | 276 | 1417 | 4.38 |
| 9 | `430067ff` | sneakers under $80 | lst_035 | 3 | 1115 | 274 | 1389 | 3.51 |
| 10 | `6352139c` | y2k top under $25 | lst_017 | 3 | 1189 | 303 | 1492 | 44.95 |
| | | **mean** | | **3.1** | **1,171** | **283** | **1,454** | **13.5** |
| | | **median** | | **3** | **1,169** | **282** | **1,456** | **4.1** |

What the numbers say:

- **The real cost on this project is requests, not money.** It runs on the free
  tier, where the limits are 15 requests a minute and a daily request cap, so
  3 calls a run means about 5 full runs a minute before `generate.py` makes you
  wait. Tokens barely change from query to query (1,389–1,505), because most of
  each prompt is the fixed wardrobe text.
- **The extension costs 1 of the 3 calls.** `pick_best_match` is a third of
  every full run's requests. Before unit 5 a run was 2 calls. With an empty
  wardrobe it's 2 again, because the pick skips the model.
- **Seconds are mostly waiting.** 8 of 10 runs took 3.5–9 s. Run 5 hit a 503,
  was retried once by `generate.py` (that's its 4th model call), and took 54 s.
  Run 10 waited 41 s for the client-side 15-per-minute pacer with no service
  error. The median (4.1 s) is the honest "one run" number. The mean (13.5 s)
  is what back-to-back runs actually feel like.
- **Failed and empty runs are close to free.** An empty search or rejected
  input makes 0 model calls and finishes in about 2 s (mostly starting the MCP
  server process). A bad key makes 2 rejected calls, uses 0 tokens, and takes
  about 6 s.

#### After the fix, and for 100 people a day

The fix (below) changed the pick prompt, so I re-measured it from the 30
full-wardrobe runs of the after-run, scored the same way (log records, cache
off): **3.13 model calls, 1,198 prompt + 286 output = 1,484 tokens, median
3.2 s per run.** The prompt is about 27 tokens longer.

At Google's list price for `gemini-3.5-flash-lite` ($0.30 per 1M input
tokens, $2.50 per 1M output tokens), one run costs:

```
prompt:  1,198 tokens × $0.30 / 1,000,000 = $0.000359
output:    286 tokens × $2.50 / 1,000,000 = $0.000715
one run                                  = $0.00107
```

**100 people a day, one search each, would cost about $0.11 a day (about $3.22
a month), and use 300 requests and 148,400 tokens a day:**

```
requests: 100 runs × 3 calls          =     300 requests/day
tokens:   100 runs × 1,484 tokens      = 148,400 tokens/day
            (119,800 prompt + 28,600 output)
dollars:  119,800 × $0.30/1M = $0.0359
           28,600 × $2.50/1M = $0.0715
                               $0.1074/day × 30 days = $3.22/month
```

The token counts are measured. The price per token is Google's published list
price, the one number here I didn't measure. At 3 searches per person it's
$0.32 a day and 900 requests. Money isn't the limit here, the rate is: at
15 requests a minute, 300 requests take at least 20 minutes of the day. And
`serve.py` handles one request at a time at ~3–4 s each, so 100 people
arriving in the same minute would wait up to about 6 minutes.

---

### Unit 5 Run Log

Each run is one `python eval_unit5.py --label runN`. It runs everything for all
five criteria, writes it to `results/`, and scores each try against the
definitions in `criteria.md`. Every model call is real (cache off, asserted).

What has to be run to produce each number:
- **Criteria 1–3:** 10 full runs (5 matching queries × 2) with the example
  wardrobe.
- **Criterion 4:** 5 runs with an **empty wardrobe**.
- **Criterion 5:** 5 runs with a **deliberately bad API key**. Each one is a
  real `app.py ask --trace` in its own subprocess, so the check reads the
  actual terminal output and the one new log line.

That's 20 agent runs per run and 60 across the three.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. The pick is always one of the real top 3 search results | 10 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 2. With a full wardrobe, the model actually makes the pick (no fallback) | 9 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 3. The reason names a real wardrobe piece | 8 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 4. An empty wardrobe falls back to the first result, with no model call for the pick | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. A failed run (bad API key) leaves a record, not an absence | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

Saved output:
- Run 1: `results/unit5_2026-11-15_1948_run1.md`
- Run 2: `results/unit5_2026-11-15_1951_run2.md`
- Run 3: `results/unit5_2026-11-15_1953_run3.md`

**How I decided the verdicts:** a criterion is MET only if it hit its target
in all three runs. For criterion 3 the denominator is the tries where the model
made the pick, and that was 10 in every run, because criterion 2 never fell
back.

#### Real output, one try per criterion (from run 2)

**File:** `results/unit5_2026-11-15_1951_run2.md`
**Function:** `eval_unit5.py::main`, which runs `agent.py::run_agent`. The log
lines are written by `runlog.py::finish`, the pick is made by
`tools.py::pick_best_match`, and the terminal output for criterion 5 comes from
`app.py::cmd_ask`.

**Criteria 1, 2 and 3** (`eval_unit5.py::full_wardrobe_tries`). The model picked
`lst_006`, the **second** keyword result, so it didn't just default to the
first. The id is in the real top 3 (C1), `pick_fallback` is `null` (C2), and
the reason names three wardrobe pieces exactly (C3):

##### Full wardrobe, try 1: `vintage graphic tee under $30`

- C1 PASS: candidates ['lst_033', 'lst_006', 'lst_002'] vs first 3 of search_results ['lst_033', 'lst_006', 'lst_002']; selected lst_006
- C2 PASS: pick_fallback = None
- C3 PASS: wardrobe names found in reason: ['baggy straight-leg jeans', 'vintage black denim jacket', 'black combat boots']

```
{"ts": "2026-11-16T01:51:10+00:00", "run_id": "c8bcbced", "source": "eval5", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "status": "ok", "error": null, "n_results": 10, "candidates": ["lst_033", "lst_006", "lst_002"], "selected": {"id": "lst_006", "title": "Graphic Tee — 2003 Tour Bootleg Style", "price": 24.0, "platform": "depop"}, "pick_fallback": null, "pick_reason": "The graphic tee pairs effortlessly with the baggy straight-leg jeans, black combat boots, and vintage black denim jacket for a cohesive grunge and streetwear look.", "fit_card": "Scored this amazing 2003 tour bootleg tee on Depop for just $24 and I'm honestly obsessed. I threw it on with some baggy dark wash jeans and black combat boots for that ultimate effortless grunge look. It has the best worn-in feel and instantly makes any outfit look so cool.", "duration_s": 7.93, "model_calls": 3, "cache_hits": 0, "prompt_tokens": 1177, "output_tokens": 263}
```

**Criterion 4** (`eval_unit5.py::empty_wardrobe_tries`). Same query, empty
wardrobe. It took the first result (`lst_033`) with the fallback text and
`model_calls: 2`, so no request was spent on the pick. The 40.9 s is a wait
for the rate limit, not work.

##### Empty wardrobe, try 1: `vintage graphic tee under $30`: PASS

- selected is first result: yes, fallback text: yes, status ok: yes, has fit card: yes, model_calls == 2: yes (model_calls=2, first result lst_033)

```
{"ts": "2026-11-16T01:52:36+00:00", "run_id": "8cb2ceff", "source": "eval5", "query": "vintage graphic tee under $30", "wardrobe_items": 0, "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "status": "ok", "error": null, "n_results": 10, "candidates": ["lst_033", "lst_006", "lst_002"], "selected": {"id": "lst_033", "title": "Vintage Band Tee — Faded Grey", "price": 19.0, "platform": "depop"}, "pick_fallback": "empty wardrobe, nothing to match against", "pick_reason": "top keyword match", "fit_card": "Scored this perfectly faded charcoal vintage band tee on Depop for just $19 and I am so obsessed with how soft it is. I paired it with a pleated black mini skirt, sheer tights, and platform combat boots for that ultimate 90s grunge edge. It has that authentic lived-in look you just can not fake.", "duration_s": 40.93, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 489, "output_tokens": 231}
```

**Criterion 5** (`eval_unit5.py::bad_key_tries`). A bad key with the cache off.
The pick fell back instead of crashing, the run stopped at `suggest_outfit`
with a message and no traceback, and exactly one `status: "error"` line was
written:

##### Bad key, try 1: PASS

- message, no traceback: yes, pick fell back: yes, ended at suggest_outfit: yes, exactly 1 new log line: yes, status error + duration: yes (exit code 0, new log lines 1)

Terminal output (`app.py ask`):

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print … +7 more
      →    branch: results found, continuing
[3] pick_best_match
      in:  {'candidates': ['lst_033', 'lst_006', 'lst_002'], 'wardrobe_items': 10}
      out: Vintage Band Tee — Faded Grey ($19.0, depop)
      →    fallback: model call failed (ModelUnavailable), using first result
[4] suggest_outfit
      in:  (failed)
      →    error: ModelUnavailable, stopping

  Couldn't finish: suggest_outfit failed. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

2 model calls this session
```

Log line:

```
{"ts": "2026-11-16T01:53:30+00:00", "run_id": "3a61a73e", "source": "cli", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "status": "error", "error": "Couldn't finish: suggest_outfit failed. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.", "n_results": 10, "candidates": ["lst_033", "lst_006", "lst_002"], "selected": {"id": "lst_033", "title": "Vintage Band Tee — Faded Grey", "price": 19.0, "platform": "depop"}, "pick_fallback": "model call failed (ModelUnavailable)", "pick_reason": "top keyword match", "fit_card": null, "duration_s": 2.04, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0}
```

(`source` reads `cli` rather than `eval5` because `app.py` sets its own source
tag, which is accurate: that run came through the CLI.)

#### What this run does and doesn't show

- **All 15 cells met. That's evidence about criteria 1, 4 and 5, and weaker
  evidence about 2 and 3.** Criteria 1, 4 and 5 are deterministic guards, so
  3 × 5/5 or 10/10 is what correct code produces, and a miss would have been a
  bug. Criteria 2 and 3 depend on the model, and I set them below 10 for 503s
  and paraphrasing. Neither happened in 30 tries: the reply always started with
  a plain `ID:` line, and every reason copied wardrobe names word for word,
  because the prompt lists them and the pick runs at temperature 0.0. The
  markdown `**ID:**` failure that criterion 2 was written to catch never
  showed up, so the test hasn't shown that the criterion would catch it. The
  offline stub test in Build notes ("no ID line") shows the fallback fires, but
  not that it fires on a real model reply.
- **The extension does change what the user gets.** Across the 30
  full-wardrobe tries, the pick differed from the first keyword result 10 times
  (5, 3 and 2 per run): `vintage graphic tee` went to `lst_006` all 6 times,
  `sneakers` to `lst_019` 3 of 6, and `denim jacket` to `lst_016` once. It
  never picked the 3rd candidate.
  **(Correction after diagnosis: 3 of those 10 were contradictions, where
  the reason argued for the other item. See Before and After.)**
- **Temperature 0.0 isn't deterministic here.** The sneakers and denim queries
  got different picks between tries with identical prompts. That doesn't break
  a criterion, but it means "same query, same item" isn't a promise the system
  makes.
- **Nothing crashed, so `status: "crash"` is still untested.** All 15 bad-key
  tries were caught as `error`.

---

### Verdicts, Diagnosis, and the Improvement

**Verdicts against the targets I set:** all five MET, in all three runs.

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Pick is one of the real top 3 | 10 of 10 | MET (10, 10, 10) | `selected.id` in `candidates`, and `candidates` = first 3 of `search_results`, every try |
| 2 | Model makes the pick | 9 of 10 | MET (10, 10, 10) | `pick_fallback` was `null` in all 30 tries |
| 3 | Reason names a wardrobe piece | 8 of 10 | MET (10, 10, 10) | a wardrobe name (up to its comma) was in every reason |
| 4 | Empty wardrobe falls back, no pick call | 5 of 5 | MET (5, 5, 5) | first result, fallback text, `ok`, fit card, `model_calls == 2` |
| 5 | Bad key leaves a record | 5 of 5 | MET (5, 5, 5) | message with no traceback, pick fell back, ended at `suggest_outfit`, exactly 1 `error` line |

**Were the targets set low? Criterion 3's was, and its check was worse than
low.** Reading the saved reasons, three passed while arguing *against* the
item that was picked:

```
run 1  picked lst_019 (Platform Sneakers — White Chunky Sole)
       "The chunky white sneakers would clash with her existing chunky white
        sneakers, making lst_035 the better versatile choice ..."
run 1  picked lst_019
       "The chunky white sneakers would clash with the shopper's existing chunky
        white sneakers, making the off-white low-top canvas sneakers a better ..."
run 2  picked lst_019
       "The chunky white sneakers would be redundant since they already own a
        pair of chunky white sneakers, making the off-white canvas sneakers a
        better cho..."
```

All three passed criterion 3, because "chunky white sneakers" is a wardrobe
name. I added a tightened version, **3a**, under criterion 3 in `criteria.md`,
leaving the original line in place: *in 10 of 10 tries the reason contains no
other candidate's id and no word from another candidate's title*. Re-scoring
the saved before-runs with `python eval_unit5.py --rescore` gives **8/10, 9/10,
10/10, so MISSED.**

**Diagnosis.** The stage is `tools.py::pick_best_match`, specifically the
format its prompt asked for. The mechanism: the prompt asked for `ID:` first
and `REASON:` second, so the model committed to an id before writing any
reasoning. On the one close call in the test set (two pairs of sneakers, one
of which duplicates a pair the shopper already owns), the reasoning that came
after the id went the other way. It's one problem with three symptoms. Every
lst_019 pick in the before-runs was one of the three, and no other query
produced one. The parser couldn't catch it because it reads the id and the
reason separately and never checks one against the other.

**The improvement (one change, `6359189`):** the prompt now asks for
`REASON:` first ("one sentence about the listing you chose ... Don't mention
the other listings") and then `ID:` ("the id of the listing your REASON is
about"). The parser didn't change. It already read the two lines in either
order.

#### Before and after, side by side

Same script (`eval_unit5.py`), same queries, three runs each, cache off.

| Criterion | Target | Before 1 | Before 2 | Before 3 | Before | After 1 | After 2 | After 3 | After |
|---|---|---|---|---|---|---|---|---|---|
| 1. Pick is one of the real top 3 | 10 of 10 | 10/10 | 10/10 | 10/10 | MET | 10/10 | 10/10 | 10/10 | MET |
| 2. Model makes the pick | 9 of 10 | 10/10 | 10/10 | 10/10 | MET | 10/10 | 10/10 | 10/10 | MET |
| 3. Reason names a wardrobe piece | 8 of 10 | 10/10 | 10/10 | 10/10 | MET | 10/10 | 10/10 | 10/10 | MET |
| 3a. *(tightened)* Reason argues for the picked item | 10 of 10 | 8/10 | 9/10 | 10/10 | **MISSED** | 10/10 | 10/10 | 10/10 | **MET** |
| 4. Empty wardrobe falls back, no pick call | 5 of 5 | 5/5 | 5/5 | 5/5 | MET | 5/5 | 5/5 | 5/5 | MET |
| 5. Bad key leaves a record | 5 of 5 | 5/5 | 5/5 | 5/5 | MET | 5/5 | 5/5 | 5/5 | MET |
| *not a criterion:* pick ≠ first keyword result | none | 5/10 | 3/10 | 2/10 | | 0/10 | 0/10 | 0/10 | |
| *not a criterion:* tokens per full run (mean of 30) | none | 1,459 | | | | 1,484 | | | |

Before files: `results/unit5_2026-11-15_1948_run1.md`, `..._1951_run2.md`,
`..._1953_run3.md`. After files: `results/unit5_2026-11-15_2001_after1.md`,
`..._2004_after2.md`, `..._2007_after3.md`.

The same sneakers query, after (`results/unit5_2026-11-15_2001_after1.md`,
`eval_unit5.py::full_wardrobe_tries`):

```
picked lst_035 (Low-Top Canvas Sneakers — Off-White)
"The off-white canvas sneakers are a versatile, minimal basic that will easily
 pair with the white ribbed tank top ..."
```

**Did it help? It fixed what it was aimed at, and it cost the extension most
of its effect.** 3a went from MISSED (8, 9, 10) to MET (10, 10, 10). The
sneakers pick is now the item the reason argues for, and none of the 30
after-tries contradicts itself. The trade: the model now picks the **first**
keyword result in 30 of 30 tries, against 20 of 30 before. Before the fix,
`vintage graphic tee` went to `lst_006` (result #2) in all 6 tries, with a
reason that named three wardrobe pieces and didn't contradict itself. After
it, it goes to `lst_033` (result #1) in all 6. So 7 of the before-run's
non-first picks were genuine, and the fix removed those along with the 3 bad
ones. None of my five criteria measures whether the pick ever differs from
the old "take the first result" behavior, which is why the table is all MET
while the extension now changes nothing about which item the user gets. It
still adds a correct, non-contradicting reason. The cost was about 25 more
tokens a run, which is negligible.

---

### What's Still Broken

- **The pick always agrees with the keyword ranking now (0 of 30 differ).**
  The new tool still runs, still costs one call per run, and still gives a
  reason, but it hasn't changed the chosen item once since the fix. My guess
  is position bias: with the reason written first and "don't mention the other
  listings", the model settles on the first listing it reads, and that's always
  the top keyword match. I haven't tested this. What I'd do is in What I'd Do
  Next. I stopped because the milestone allows one improvement, and a second
  prompt change would make it impossible to say which change did what.
- **Targets set too low, even after 3a:**
  - Criterion 2 (9 of 10) never fell back in 60 tries, so I'd tighten it to
    **10 of 10**. The 503 allowance was never needed, and `generate.py`'s
    retries handled the one 503 I saw during the cost runs.
  - Criterion 3 (8 of 10) passed 60 of 60, because the model copies wardrobe
    names word for word at temperature 0.0. With 3a beside it, I'd raise it to
    **10 of 10** too.
  - I'd add a criterion that measures the extension's effect rather than its
    safety: *on `vintage graphic tee under $30`, the pick is the same item
    whichever order the 3 candidates are listed in, in 5 of 5 tries.*
- **Criterion 2's original failure mode is still untested on a real reply.**
  A reply formatted as `**ID:** lst_006` still wouldn't parse and would fall
  back. The model never produced one, so all I have is the offline stub test.
- **The `crash` path in `run_agent` is untested.** Every failure I triggered
  was caught as `error` or `no_results`.
- **Temperature 0.0 wasn't deterministic** before the fix: the sneakers and
  denim picks varied between identical prompts. After the fix every query got
  the same pick every time, which looks like the position bias, not stability.

---

### What I'd Do Next

First, I'd run the same 10 queries with the 3 candidates shuffled in the
prompt and check whether the pick follows the item or follows the position.
The extension's whole claim is that it picks by wardrobe, and right now 30 of
30 picks are the first item listed, so I can't tell whether the model is
choosing or just taking whatever comes first. Every other improvement to the
pick depends on that answer.

---

### How I Used AI

I used Claude (Claude Code, in VS Code) throughout the capstone, mainly for
three things: getting the commands right, making my explanations clearer, and
adding detail to the README and RUNNING.md.

**Moment 1: getting the commands right**

- *What I asked for:* the exact commands to set up and test the project from a
  fresh clone, and to run the agent with the cache off and a deliberately bad
  API key.
- *What came back:* the clone → venv → `pip install` → `.env` → `test.py`
  sequence for both PowerShell and Git Bash, plus
  `AI201_CACHE=0 GEMINI_API_KEY=bad python app.py ask '...' --trace`.
- *What I changed:* the first bad-key run "passed" because every answer came
  from the cache. I added `AI201_CACHE=0` to the command, to RUNNING.md's
  troubleshooting table, and to the criteria.

**Moment 2: improving explanations**

- *What I asked for:* help turning my verdicts and diagnosis into a place plus
  a mechanism instead of a description.
- *What came back:* the diagnosis for criterion 3a: the prompt asked for the
  ID before the reason, so the model committed to an item before reasoning.
- *What I changed:* I checked it against the saved run files first. All three
  contradictions were on the same sneakers query, so I wrote it up as one
  problem with three symptoms, not three problems.

**Moment 3: more detail in the README and RUNNING.md**

- *What I asked for:* more detail in RUNNING.md (what the environment needs,
  where the logs go, what breaks on a fresh clone) and in the README's run log
  and cost sections.
- *What came back:* the environment table, the troubleshooting table, the
  log-field list, and the per-run cost table with the arithmetic shown.
- *What I changed:* I corrected numbers I'd guessed against the measured ones:
  RUNNING.md said about 4 model calls a run, and the measurement said 3. An
  empty run took about 2 s, not 3.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [X] criteria.md has five numbered criteria, each with a target
       [X] Each criterion has a reason underneath it
       [X] All five unit 3 sections above have real content
       [X] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [X] Planning Loop names the branch rule and agent.py::run_agent
       [X] Sample Run: one full query plus the three per-tool tests, as text
       [X] At least four new commits
       [X] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [X] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [X] Run Log — Before, five criteria, five tries each
       [ X Real output pasted underneath, naming file and function
       [X] A verdict on every criterion
       [X] A diagnosis for every miss, naming a place AND a mechanism
       [X] Loop Trace, with the MCP call visible in it
       [X] All three failure modes triggered and handled
       [XX] One improvement, with Run Log — After in the same format
       [X] What's Still Broken
       [X] At least four new commits
       [X] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
