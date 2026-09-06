# Taste-based travel assistant

A personal picker, not a travel search engine.

The job is to take a destination and constraints, then return a **short list** of places and activities that match **you**, with a reason for each pick — then **ask for feedback** so taste and history stay current.

## What it is (and is not)

**Is**

- Anchored on a `who-i-am` file you write
- A taste file that gets adjusted from your feedback
- A history of places you actually went to, marked liked or disliked
- Ranked suggestions for neighborhoods, food, stays, and things to do

**Is not**

- Booking, flights, or a map of every restaurant in a city
- Generic "top 10 in Paris" lists
- A chatbot that forgets what you like

## Three files (source of truth)

| File | Who writes it | Role |
| ---- | ------------- | ---- |
| `data/who-i-am.md` | You | Identity anchor. How you travel, what you care about. The system reads it; it does not rewrite it. |
| `data/taste.json` | System, from your feedback | Working taste. Likes, dislikes, patterns. Updated after every reaction. |
| `data/history.json` | System, when you say you went | Places you visited, with liked / disliked and a short note. |

Ranking always loads all three. `who-i-am` is the north star. History is hard evidence. Taste is the living summary of reactions.

Drop your real `who-i-am` content into `data/who-i-am.md` when you have it. The template is a placeholder until then.

## How a suggestion works

Every pick is a question, not a statement.

1. Read `who-i-am.md`, `taste.json`, and `history.json`.
2. Filter out places you already disliked. Prefer patterns from places you liked.
3. Show a short list. Each card includes **why this fits you** (cite the who-i-am or taste line).
4. **Ask for feedback before moving on.** Required, not optional.

Feedback options on each suggestion:

- **Like this** — keep on the trip shortlist; add a like-pattern to `taste.json`
- **Not for me** — drop it; add a dislike-pattern to `taste.json`
- **I went, liked** — write to `history.json` as liked; reinforce taste
- **I went, disliked** — write to `history.json` as disliked; never suggest this (or this kind) again
- Optional one-line **why**

Taste is only adjusted from feedback. Suggestions never silently rewrite the files.

## History

`history.json` is the log of places you actually experienced.

Each entry: place, city, kind (stay / eat / do / neighborhood), when, liked or disliked, notes.

Uses:

- Do not re-suggest disliked places
- Treat liked places as examples ("more like this")
- Show a simple history view so you can correct a mark later

Suggested-but-not-visited stays in `taste.json` only, not in history.

## User flow

1. **You** — `who-i-am.md` is the anchor. Taste starts empty or copied from it.
2. **Trip** — city, dates, days, companions, budget.
3. **Picks** — 5–8 items per bucket: Stay, Eat, Do, Neighborhood.
4. **Why** — each card cites who-i-am or taste.
5. **Feedback** — like / not for me / I went (liked or disliked). Files update immediately.
6. **Shortlist** — liked suggestions become the trip list.

Example: "Tokyo, 4 days, mid budget" + who-i-am says slow and local → Yanaka over Shibuya. After you skip a packed food-tour, taste records "no packed food tours" and later trips respect that.

## MVP (build this first)

One small web app. One user (you). No accounts required.

- Load `who-i-am.md` as the identity panel (read-only in the UI except a link to edit the file)
- New trip: destination + dates + notes
- Generate ranked picks (Stay / Eat / Do / Neighborhood)
- Feedback prompt on every card; write `taste.json` and `history.json`
- Trip shortlist and a history page

**Data for v1:** LLM + a tiny seed catalog for 2–3 cities. No booking APIs.

**Stack (simple):** Next.js, the three JSON/Markdown files above, one LLM call with structured output.

## Ranking (keep it dumb)

Do not train a model.

1. Filter hard constraints and history dislikes.
2. Score overlap with who-i-am + taste + liked history.
3. LLM reranks a small set and writes a one-line why.
4. If it cannot cite who-i-am or taste, drop the item.
5. After the list is shown, collect feedback and write files.

## Later (not now)

- More cities / live Places data
- Import likes from Google Maps
- Auto-summarize taste from a long history
- Calendar / packing / logistics
- Multi-user accounts
- Flights and hotels booking

## Files we would add next

```
app/                    UI: trip, picks, feedback, history
lib/taste.ts            read/write taste.json from feedback
lib/history.ts          read/write visited liked/disliked
lib/rank.ts             who-i-am + taste + history → picks
data/who-i-am.md        you write this
data/taste.json         adjusted from feedback
data/history.json       places you went
data/catalog/           seed places for a few cities
```

## Default assumptions

- Personal tool, not a product launch
- English UI
- `who-i-am.md` is yours; the app does not edit it
- Taste and history are append-friendly JSON the app does edit
- First seed cities: pick 2–3 when we start building
