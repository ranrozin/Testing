# Taste-based travel assistant

A personal picker, not a travel search engine.

The job is to take a destination and constraints, then return a **short list** of places and activities that match **your taste**, with a reason for each pick.

## What it is (and is not)

**Is**

- A taste profile that gets better as you react to picks
- Ranked suggestions for neighborhoods, food, stays, and things to do
- A saved shortlist for a trip

**Is not**

- Booking, flights, or a map of every restaurant in a city
- Generic "top 10 in Paris" lists
- A chatbot that forgets what you like

## How taste works

Taste is a small, explicit profile plus feedback. No hidden black box.

### Profile (you fill once, edit anytime)

| Dimension        | Examples                                      |
| ---------------- | --------------------------------------------- |
| Pace             | slow / mixed / packed                         |
| Vibe             | local, design-forward, classic, nature, quiet |
| Food             | cuisines, street vs sit-down, coffee, bars    |
| Stay             | boutique, apartment, luxury, budget, location |
| Avoid            | tourist traps, chains, late nights, hiking    |
| Budget           | low / mid / high                              |
| Hard constraints | diet, walking limit, kids, accessibility      |

Free-text notes are first-class: "I like neighborhood bakeries, not destination restaurants."

### Feedback (how it learns)

Every suggestion can be **keep**, **skip**, or **never this kind of thing**.

That writes a short memory, for example:

- Kept: "quiet wine bar, locals, no reservations theater"
- Skipped: "rooftop club, bottle service"

Later picks must respect those notes.

## User flow

1. **Taste** — answer a short form (or paste notes). Saved locally.
2. **Trip** — city, dates, days, companions, budget.
3. **Picks** — 5–8 items per bucket: Stay, Eat, Do, Neighborhood.
4. **Why** — each card says which taste rule it matched.
5. **Shortlist** — keep items into a trip list you can export.

Example: "Tokyo, 4 days, mid budget, slow pace" → Yanaka over Shibuya if the profile says quiet and local.

## MVP (build this first)

One small web app. One user (you). No accounts required.

- Taste profile page (form + free text)
- New trip: destination + dates + notes
- Generate ranked picks (Stay / Eat / Do / Neighborhood)
- Keep / skip on each card, which updates taste memory
- Trip shortlist you can reopen

**Data for v1:** LLM + a tiny seed catalog for 2–3 cities you care about. No booking APIs.

**Stack (simple):** Next.js, local JSON/SQLite for profile and trips, one LLM call with structured output.

## Ranking (keep it dumb)

Do not train a model.

1. Filter hard constraints (diet, budget, walking).
2. Score tag overlap with the profile.
3. Ask the LLM to rerank a small candidate set and write a one-line "why this fits you."
4. Show the why. If it cannot cite the profile, drop the item.

## Later (not now)

- More cities / live Places data
- Import likes from Google Maps or saved lists
- Calendar / packing / logistics
- Multi-user accounts
- Flights and hotels booking

## Files we would add next

```
app/                 UI: taste, trip, picks
lib/taste.ts         profile + feedback memory
lib/rank.ts          filter → score → LLM rerank
data/profile.json    your taste
data/catalog/        seed places for a few cities
```

## Default assumptions

- Personal tool, not a product launch
- English UI
- You will type taste in your own words; the form just gives structure
- First seed cities: pick 2–3 when we start building
