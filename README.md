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

**On Android: there is no Rules screen.** There is also no native Cursor Android app yet (it is [planned](https://cursor.com/docs/cloud-agent/mobile)). What you have is [cursor.com/agents](https://cursor.com/agents) in Chrome, often installed as a home-screen app. That page starts and reviews Cloud Agents. It is not an IDE, and it has no Customize → Rules.

You do not need to set anything on the phone. This repo already has the travel-agent rule at `.cursor/rules/travel-agent.mdc` (`alwaysApply: true`). Agents you start from Android load it automatically.

**From the phone, to change a rule:** tell this agent what the rule should say. It will edit the `.mdc` file and open a PR. Do not look for a Settings → Rules toggle in the Android app / PWA.

**Optional User Rules** (account-wide) are only in the **Cursor desktop app**: Customize → Rules. Not on Android, and not on cursor.com/agents. You can skip this. The project rule is enough.

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
