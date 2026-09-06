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

`data/who-i-am.md` is filled in with Ran's travel taste profile. `data/taste.json` starts as a structured extract of that file (likes, dislikes, family rules). The `log` in taste and `places` in history grow from feedback.

## How a suggestion works

Every pick is a question, not a statement.

1. Read `who-i-am.md`, `taste.json`, and `history.json`.
2. Filter out places you already disliked. Prefer patterns from places you liked.
3. Show **2–4 strong choices**, plus one clear pick: "I would choose X because…"
4. Each card includes **why Ran specifically might like it** (cite who-i-am or taste). Say so if it is unverified.
5. **Ask for feedback before moving on.** Required, not optional.

Feedback options on each suggestion:

- **Like this** — keep on the trip shortlist; add a like-pattern to `taste.json`
- **Not for me** — drop it; add a dislike-pattern to `taste.json`
- **I went, liked** — write to `history.json` as liked; reinforce taste
- **I went, disliked** — write to `history.json` as disliked; never suggest this (or this kind) again
- Optional one-line **why**

Taste is only adjusted from feedback. Suggestions never silently rewrite the files.

## History

`history.json` is the log of places you actually experienced.

Each entry: place, city, kind (stay / eat / coffee / do / neighborhood), when, liked or disliked, notes.

Uses:

- Do not re-suggest disliked places
- Treat liked places as examples ("more like this")
- Show a simple history view so you can correct a mark later

Suggested-but-not-visited stays in `taste.json` only, not in history.

## User flow

1. **You** — `who-i-am.md` is the anchor. `taste.json` starts as a structured extract of it.
2. **Trip** — city, dates, days, companions, budget.
3. **Picks** — 2–4 items per bucket: Stay, Eat, Coffee, Do, Neighborhood. One recommended pick.
4. **Why** — each card cites who-i-am or taste. Flag tourist-trap risk and uncertainty.
5. **Feedback** — like / not for me / I went (liked or disliked). Files update immediately.
6. **Shortlist** — liked suggestions become the trip list.

Family trips plan for Ran, Noga, and Shir (18): cities and comfortable food over hike-heavy or museum-heavy days; at least one straightforward restaurant option.

Example: "Tokyo, 4 days, slow" → Yanaka over Shibuya. After a skip of a packed food tour, taste records that, and later trips respect it.

## MVP (build this first)

One small web app. One user (you). No accounts required.

- Load `who-i-am.md` as the identity panel (read-only in the UI except a link to edit the file)
- New trip: destination + dates + notes
- Generate 2–4 ranked picks (Stay / Eat / Coffee / Do / Neighborhood) plus one chosen pick
- Feedback prompt on every card; write `taste.json` and `history.json`
- Trip shortlist and a history page
- Family-aware picks when Noga and Shir are on the trip

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
- Live editorial sources, opening hours, weather, reservations
- Running routes near the hotel
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
data/who-i-am.md        Ran's profile (filled)
data/taste.json         extract + feedback log
data/history.json       places you went
data/catalog/           seed places for a few cities
```

## Default assumptions

- Personal tool, not a product launch
- English UI
- `who-i-am.md` is yours; the app does not edit it
- Taste and history are append-friendly JSON the app does edit
- 2–4 choices, one recommendation, then ask for feedback
- Do not invent confidence; say when a pick is unverified
- First seed cities: pick 2–3 when we start building
