<!-- Source: Q, pasted by Mark into the Stella/MailBridge thread on 2026-10-03. Body preserved as supplied. Status: contributor proposal, not an approved specification or verified implementation. See mailbridge-source-index.md for integration notes. Private project material; established ownership/confidentiality instructions apply. -->

# MailBridge – Project Architecture & Design
**Role:** Lead Designer (Q) | **Advisor:** Mark | **Founder:** Stella
**Status:** Pre-launch MVP | **Date:** Current

---

## 1. PROJECT OVERVIEW

**Mission:** Give agency to ESL (English as a Second Language) and limited-English speakers by helping them understand physical mail.

**Core Problem:** Government letters, medical bills, and financial notices are confusing even for native speakers. For ESL users, they cause anxiety and inaction.

**Core Solution:** User photographs mail → App identifies it → Explains it in plain language → Gives clear action steps.

**Key Differentiator:** A toggle between "Official Business Language" and "Explain it like a friend." This is the buy-in feature.

---

## 2. THE SPINE (Core 4-Step Process)

This is the primary architecture. All decisions flow from this.

### Step 1: Intake
- User snaps photo of mail on kitchen table
- Minimal UI: camera viewfinder + single shutter button
- Ghost dot (top-left) for menu access

### Step 2: The Airlock (Privacy & Sanitization)
- Raw image processed **in memory only** (never written to disk)
- Local OCR extracts text (Tesseract or equivalent)
- Regex strips PII: SSNs, account numbers, names, addresses
- Raw image + raw OCR discarded immediately after sanitization
- **Nothing raw ever reaches classification or AI layers**

### Step 3: System 1 Triage (Sorting)
- Sanitized text sent to lightweight sorting engine
- Returns structured decision:
  - Category (medical, utility, government, bank, junk)
  - Urgency (high, medium, low)
  - Confidence score (0–1)
  - Action required (true/false)
- **Confidence Harness:** If confidence < 0.85, system does NOT guess
  - Flags as "needs_human_review"
  - Routes user to video/in-person support

### Step 4: System 2 Explanation (AI)
- Invoked only when user asks for explanation
- Receives sanitized text + triage tags
- Translates legalese into plain language
- Generates action plan
- Supports toggle: "Official" vs "Friend" mode

---

## 3. UX DESIGN CONCEPTS

### Stop Light System (Triage Display)
- 🔴 Red: "Act Now" (shut-off notice, tax deadline)
- 🟡 Yellow: "Read & Decide" (standard bill, policy update)
- 🟢 Green: "Safe to Toss" (junk mail, marketing)
- Document type shown as universal icon (medical cross, building, card, lightning bolt)

### Explanation Mode
- Agent avatar with animated noise waves (indicates AI is "talking")
- Verbosity slider: "Just the Facts" ←→ "Explain Everything"
- Mode toggle:
  - 🏛️ Building icon = Official Business Language
  - 💬 Speech bubble = Explain Like a Friend
- Content appears in progressive cards (one paragraph at a time, swipe up for more)

### Action Plan Screen
- Simple checklist with icons
- Tap to dial phone numbers
- Tap to add calendar events
- "Talk to Stella" escalation button for edge cases

### Platform Strategy
- Stella's iOS app continues in App Store review
- **Android APK built for sideloading** to enable faster testing
- Android serves as the test bed; iOS is the polished launch target

---

## 4. PRIVACY & SECURITY (The Fortress)

### Principles
- Raw PII never leaves the device
- No cloud OCR on raw images
- Only sanitized text reaches any AI model
- Ephemeral processing: raw data destroyed after sanitization
- HIPAA-compliant mindset from day one

### Implementation
- OCR runs locally (Tesseract, PaddleOCR, or on-device ML)
- PII stripping via deterministic regex (no AI involved)
- If cloud API is used for sorting, it receives ONLY sanitized text
- Future: fully local Small Language Models (Llama-3.2, Phi-3.5-mini) to eliminate cloud dependency entirely

---

## 5. TESTING STRATEGY

### The Genesis Set
- 3–5 curated real letters from friends/family
- PII manually redacted (black marker or tape)
- Used as seed templates for synthetic data generation
- Math: 5 real templates × 30 variations = 150 synthetic test cases

### Demo Structure
- **Document 1 (Success):** Standard medical bill → classified, explained in Friend Mode, action plan generated
- **Document 2 (Correct Refusal):** EBT/PIN split letter → low confidence → app says "I'm not sure, let me connect you with Stella"
- Showing a correct refusal proves the system is safe and won't hallucinate

### Edge Case: EBT/Medical Card
- Card arrives in one envelope, PIN in another
- Confusing even for native speakers
- Identified as edge case for MVP
- Handled via video/in-person support initially
- Later: build specific logic for multi-envelope documents

---

## 6. ALTERNATIVES & OPTIONS (Below the Spine)

These are modular swaps. The Spine above is the default. These exist for flexibility.

### Sorting Engine Options

| Option | Type | Cost | When to Use |
|--------|------|------|-------------|
| **Jev (TypeSafe)** | System 1 AI model | ~$0.01/doc | Default for V1. "New sexy" for talent attraction |
| **Reducto Classify** | SaaS API | $7.50/1,000 pages | MVP quick-start. $150 free credit |
| **Veryfi** | SaaS API | Free for 100 docs | Secondary test option |
| **Local SLM (Llama/Phi)** | On-device model | Free (compute only) | Future privacy-first option |

### OCR Options

| Option | Type | Cost | When to Use |
|--------|------|------|-------------|
| **Tesseract** | Local, open-source | Free | Default. No data leaves device |
| **PaddleOCR** | Local, open-source | Free | Better for handwritten/complex layouts |
| **On-device ML Kit** | Mobile-native | Free | Best for Android APK |

### Explanation AI Options

| Option | Type | Cost | When to Use |
|--------|------|------|-------------|
| **Qwen (Cloud)** | Large language model | Per-token | Default for MVP |
| **Qwen (Local)** | Quantized model | Free (compute) | Future privacy option |
| **Mistral (Z)** | Audit/validation | Per-token | Ensemble verification |
| **GPT (Meraki)** | Audit/validation | Per-token | Ensemble verification |

---

## 7. NEXT STEPS

1. **This week:** Stella selects 3–5 test letters. Mark prepares Genesis Set.
2. **This week:** Android APK skeleton built for sideloading.
3. **Next week:** Demo with 1 successful classification + 1 correct refusal.
4. **Next event:** Stella announces Jev integration as open challenge to attract engineering talent.
5. **Post-demo:** Evaluate SaaS sorting results. Decide if Jev replaces it for V1.

---

## 8. GITHUB REPOSITORY (Planned)

- `/docs` – This file, flowcharts, design specs
- `/src/ocr` – Local OCR pipeline
- `/src/sanitize` – PII regex patterns
- `/src/classify` – Jev/SaaS sorting logic
- `/src/explain` – Qwen explanation prompts
- `/test` – Synthetic test documents (no real PII)
- `/demo` – Demo scripts and expected outputs

---

*End of document. This is one of potentially 5+ markdowns. Meraki (GPT) will handle cross-document ordering and integration.*
