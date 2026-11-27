# Sora 2 Character Consistency Prompting Guide

> A practical guide for getting consistent characters across hundreds of Sora 2 generations. Built from real production experience running multi-month AI video YouTube channels.

---

## The Core Problem

You generate a great-looking AI video of a character. The next day you generate another video with the same character — and Sora gives you a totally different-looking version. Different fur, different eyes, different proportions. Your "channel" looks like 50 different characters wearing the same name tag.

This guide covers the techniques that solve that problem.

---

## Why Character Consistency Matters

For a YouTube channel built on a recurring character, consistency is everything. Subscribers come back because they recognize the character. The algorithm learns to associate your channel with a specific look. Brand identity compounds.

Inconsistency does the opposite — it tells viewers (and the algorithm) that this is "AI slop content" rather than a coherent show.

---

## The Reference Subject Pattern

**The single most effective technique:** anchor every prompt to a named reference subject.

Sora 2 (and similar models) tend to lock in on a specific named entity better than they lock in on described characteristics. This means:

- **Weak:** "a fluffy white puppy with floppy ears"
- **Strong:** "Bandit, a fluffy white puppy with floppy ears" (and you use "Bandit" in every prompt going forward)

The named reference acts as an attention anchor. Even if Sora's interpretation drifts slightly, the name keeps it pulled toward a consistent latent representation.

**Rule:** give your character a unique name. Use it in every prompt. Reuse the same descriptive sentence verbatim across prompts as the character's "biography line."

---

## The Biography Line

For every character, write ONE biography line and paste it at the top of every prompt unchanged.

Example:

```
Bandit, a fluffy white Maltese puppy with cream-colored ears, large dark eyes,
and a small black nose. Always shown in soft natural lighting.
```

This single line goes at the start of every prompt. Then add the scene-specific content after it.

**Why this works:** Sora has a token-attention pattern that weights the opening of a prompt more heavily. By keeping the character description in the same opening position with identical wording, you pin the character interpretation across generations.

**Don't:**
- Vary the biography line "for variety"
- Move it to the middle or end of the prompt
- Paraphrase it in different words

**Do:**
- Copy-paste the exact same line
- Update it ONLY when you're intentionally evolving the character (rare)

---

## Scene Construction Pattern

After the biography line, structure each prompt in this order:

1. **Biography line** (fixed)
2. **Scene setting** (where is this happening)
3. **Action / situation** (what's the character doing)
4. **Style / mood** (lighting, camera, vibe)
5. **Technical constraints** (resolution, duration, format)

Example full prompt:

```
Bandit, a fluffy white Maltese puppy with cream-colored ears, large dark eyes,
and a small black nose. Always shown in soft natural lighting.

Setting: a sunny kitchen with white tile floors and morning light from a window.

Action: Bandit is trying to drag a slipper across the floor that's clearly too big.
The slipper keeps slipping out of his mouth. Bandit looks frustrated but determined.

Style: warm domestic lifestyle aesthetic, slight handheld camera, gentle slice-of-life mood.

Technical: vertical 1080x1920, 10 seconds, smooth motion.
```

Each generation: same biography line, same technical line, different setting/action/style.

---

## What to Vary, What to Lock

**Lock these across every prompt:**
- Character name
- Character physical description (the biography line)
- Character "world rules" (e.g. "Bandit always wears a small red collar")
- Technical specs (resolution, length)

**Vary these freely:**
- Setting / location
- Action / situation
- Mood / style descriptors
- Time of day
- Other characters or objects in scene

**Vary cautiously:**
- Camera angle (Sora handles this well, but extreme angles can break character recognition)
- Distance (extreme close-ups or extreme wides can make Sora "lose" the character)
- Lighting style (radical changes from "warm natural" to "neon nightclub" can drift)

---

## The "Same Universe" Rule

Even with a great biography line, you'll get drift if you put the character in radically different visual universes prompt-to-prompt.

**Drift-prone:**
- Day 1: photorealistic puppy in real kitchen
- Day 2: anime-style puppy in fantasy castle
- Day 3: claymation puppy on a spaceship

The model loses the thread.

**Drift-resistant:**
- Pick ONE visual universe (e.g. "warm domestic lifestyle, photorealistic")
- Stay within it for the whole channel
- Only break the universe rule for clearly-marked "special episodes"

**Rule of thumb:** if a viewer can immediately tell two videos came from the same channel without seeing the channel name, your universe is locked in correctly.

---

## Common Failure Modes

### Failure 1: The character is described, not named

**Symptom:** Every video looks like a different character that fits the description.
**Fix:** Add a name. Use the named reference subject pattern.

### Failure 2: Biography line is too long or vague

**Symptom:** Sora interprets the description differently each time.
**Fix:** Tighten the biography line. Pick 3-5 specific physical traits. Avoid abstract words like "cute," "majestic," "elegant" — use concrete physical descriptors.

### Failure 3: Biography line is in different positions across prompts

**Symptom:** Character drift across generations.
**Fix:** Always put the biography at the very start of the prompt.

### Failure 4: Mixing photorealistic and stylized prompts

**Symptom:** Some videos look like real puppies, others look like cartoon puppies.
**Fix:** Pick one style. Add a style descriptor to the biography line so it's locked in: *"...always rendered in photorealistic style with natural lighting."*

### Failure 5: Background characters / objects vary too much

**Symptom:** The character's environment changes wildly, making the channel feel fragmented.
**Fix:** Establish 3-5 "home environments" and rotate among them. e.g. "Bandit's kitchen," "Bandit's backyard," "Bandit's living room."

---

## The Stockpile Approach

For high-volume channels (100+ videos), don't generate prompts ad-hoc. Build a **prompt vault**.

A prompt vault is a single document with:
- The character biography line at the top
- A list of 50-200 pre-written scene/action descriptions
- Optionally: variations grouped by theme ("food scenes," "outdoor scenes," etc.)

You generate from the vault, marking each prompt as used. New prompts get added as you think of them. This:

- Keeps quality high (you write prompts when you're inspired, not when you're scrambling)
- Makes batch generation efficient (line up 20 prompts, generate them all)
- Prevents accidental repeats
- Builds an asset that compounds over months

---

## Iteration Loop

When a particular generation works, save the EXACT prompt text. When one fails, save that too with a note about what failed.

After 50-100 generations, patterns emerge:
- "Action verbs that include 'trying to' produce more emotionally engaging shots"
- "When I include 'soft lighting,' fur consistency improves"
- "When the action is too complex, the character drifts"

Use those patterns to update your prompt template.

---

## Working with Claude on Prompts

This kit is designed to work with Claude. For prompt generation, you can:

1. **Have Claude generate scene descriptions** based on a theme. Example:
   > "Generate 20 scene descriptions for a cute puppy character named Bandit. Each scene should be a 10-second action with clear visual moments."

2. **Have Claude wrap your scenes in the full prompt template.** Example:
   > "Take these 20 scenes and wrap each one in my standard Sora prompt template, including the biography line and technical specs."

3. **Have Claude review failed generations** to find patterns:
   > "Here are 10 prompts that produced inconsistent characters. What do they have in common that the successful prompts don't?"

This saves you hours of prompt engineering. Claude learns your style after a few examples and can generate dozens of on-brand prompts at a time.

---

## Quick Reference Card

```
PROMPT STRUCTURE:
  [Biography line — fixed, character description]
  [Setting — varies]
  [Action — varies]
  [Style — fixed for the channel universe]
  [Technical — fixed]

LOCK IN:
  - Character name
  - Character physical description (3-5 concrete traits)
  - World rules
  - Style universe
  - Technical specs

VARY:
  - Setting
  - Action
  - Mood within the universe

TEST:
  - If two videos from your channel look like different characters,
    tighten the biography line.
  - If the universe feels fragmented, lock the style descriptor harder.
```

---

## What This Doesn't Cover

- **Multi-character scenes.** Maintaining consistency for 2+ characters in the same generation is harder. Worth a separate guide.
- **Voice consistency.** This guide is visual-only. For talking characters, voice (ElevenLabs or similar) is its own discipline.
- **Realistic human characters.** Sora 2 is best at stylized or non-human subjects. Realistic humans drift more aggressively. Approach with caution.
- **Brand asset consistency.** If your character has signature props or settings, those need their own consistency strategies.

---

*Built with Claude. Refined through 800+ Sora generations.*
