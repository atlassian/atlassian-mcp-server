# author checklist

Follow the tool-access and coverage rules in the shared skill entrypoint. Examples name operations; use direct calls when available, otherwise the discovered runner and schema.

## Checklist for skill authors

A skill that loads this file should state:

- **Anchor:** what the user provides, which `objectType` it resolves to, and how to resolve it.
- **Connectors:** needed and helpful, naming each Atlassian app separately, what the skill does when a needed one isn't on the site, and the vendor connector to use for each gap in Teamwork Graph the skill hits.
- **Context:** which relationships to follow from the anchor, which product records confirm them, which searches and JQL to run, and the date window.
- **Statuses:** the full vocabulary the source records use (including Pending, Paused, Done and Cancelled), and how each one displays.
- **Stop condition:** what the artifact needs before it can be written, and a call budget if it differs from the default.
- **Writes:** any actions it takes, and what it confirms first.
- **Artifact:** its sections, and the design rules beyond `atlassian-design`.
- **Delivery:** state whether the skill uses answer-first delivery or its existing artifact flow. For answer-first delivery, give the answer, offer optional HTML export, and offer publication only when Atlassian Artifacts availability is confirmed. For either mode, state who to offer sharing with after an approved publication.
- **When live:** what the live version refreshes, which tools it asks for, any writes it offers, and whether it can be shared. Or "Static only".
