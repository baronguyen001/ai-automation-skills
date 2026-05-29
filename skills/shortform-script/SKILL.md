---
name: shortform-script
description: "Draft a short-form TikTok/Reels/Shorts or long-form video script from a topic and creator persona file - hook variants, beat-structured body, CTA, b-roll cues, caption overlays, and [STORY]/[NUMBER] slots so the model never fabricates personal facts. Use for write a video script, tiktok script, youtube script, or /shortform-script."
argument-hint: "<topic> [--format short|long] [--hook salary|mistake|contrarian|story|howto|curiosity|bts] [--variants N]"
---

# Shortform Script

Use this skill when a creator wants a short-form or long-form video script that matches a supplied persona instead of generic internet voice. It creates hook variants, a beat-structured body, CTA options, b-roll cues, caption overlays, and fact slots for any claim the persona file does not prove.

## When to invoke

- User says: "write a video script" / "tiktok script" / "youtube script" / "/shortform-script"
- Code or files in the conversation include: `persona.md`, a content calendar, or creator voice notes.

## When NOT to invoke

- The user wants a blog post, article, email, or landing page.
- The user wants paid ad copy with offer testing and conversion claims.

## Concrete example

User input:

```text
/shortform-script "Stop overengineering your first CLI" --format short --hook mistake --variants 3
```

Output:

```markdown
## Hook variants
1. The biggest CLI mistake is adding config before anyone uses the command.
2. Your first CLI does not need a plugin system. It needs one command that works.
3. If your setup guide is longer than the tool, cut the feature list in half.

## Script
Hook: Your first CLI does not need a plugin system. It needs one command that works.

Beat 1: Start with the user action. "I want to lint one folder and see the errors."
Beat 2: Ship the smallest command: `tool check ./project`.
Beat 3: Add flags only after the second real user asks for them.
Beat 4: Keep a slot for proof: [NUMBER: your measured setup time before/after simplification].

CTA: Comment "CLI" if you want the checklist I use before adding a new flag.

## B-roll cues
- Terminal running one command.
- Split screen: overloaded help text vs three clean options.
- Cursor deleting a premature plugin folder.

## Caption overlays
- "One command first."
- "Flags come later."
- "Measure setup time."
```

## Pattern to apply

1. Load the user's persona file, or ask them to adapt `prompts/persona.example.md`.
2. Choose short format (30-60 seconds) or long format (10-15 minutes).
3. Generate hook variants from the requested hook family.
4. Write beats that match the persona's audience, voice, phrasing, and CTA bank.
5. Use `[STORY:]`, `[NUMBER:]`, `[DATE:]`, and `[NAME:]` slots for facts not provided by the user.
6. Return script, CTA, b-roll cues, and caption overlays.

Reference: `prompts/persona.example.md` and `examples/sample_output.md`.

## Source

Distilled from production use across the author's automation projects. v0.1.0.
See also: [[gemini-structured-output]].
