# Travel agent (Cursor)

This repo is a **Cursor chat agent**, not a web app and not a trip-planner UI.

Open the repo in Cursor (or start a Cloud Agent on it) and ask. Cursor’s model is the agent. There are no outside LLM APIs to pay for.

## How to use it

Ask in plain language, for example:

- We’re in Munich 6–8 Sep with Noga and Shir. Coffee and dinner tonight?
- Innsbruck for five nights. One easy nature day, not a hike-heavy trip.
- We went to Man Versus Machine. Liked it.

The agent reads your files, answers, then asks what you thought so it can update taste and history.

## How to set a rule

**On the Cursor iPhone/iPad app: you can't.** The app has no Rules screen. That is expected. It directs Cloud Agents; it is not an IDE. [Cursor's mobile docs](https://cursor.com/docs/cloud-agent/mobile) say rules are managed on the web, and agents pick up whatever is already in the repo.

You do not need to set anything on the phone. This repo already has the travel-agent rule at `.cursor/rules/travel-agent.mdc` (`alwaysApply: true`). Agents you start from the app load it automatically.

**From the phone, to change a rule:** tell this agent what the rule should say. It will edit the `.mdc` file and open a PR. Do not look for a Settings → Rules toggle in the app.

**Optional User Rules** (account-wide) are only in the **Cursor desktop app**: Customize → Rules. Not in the mobile app, and not on cursor.com/agents. You can skip this. The project rule is enough.

## Files

| File | Who writes it | Role |
| ---- | ------------- | ---- |
| `data/who-i-am.md` | You | Identity. The agent reads it and does not rewrite it. |
| `data/taste.json` | Agent, from your replies | Living likes, dislikes, feedback log. |
| `data/taste-vector.json` | Agent | Numeric taste vector. Options are scored and ranked by distance. |
| `data/history.json` | Agent, when you say you went | Places visited, liked or disliked. |
| `data/search-cache.json` | Agent | Last 30 days of scored options. Cleared on request. Not committed. |
| `.cursor/rules/travel-agent.mdc` | You (or ask the agent) | The always-on rule. This is how you set rules for this repo. |

Behavior lives in `.cursor/rules/travel-agent.mdc` and `.cursor/skills/travel-agent/SKILL.md`. Cloud Agents also read `.cursor/CLOUD.md`: if the checkout is behind `origin/main`, pull before answering.
