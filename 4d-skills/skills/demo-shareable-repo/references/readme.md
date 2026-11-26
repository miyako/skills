# Demo README Conventions

The README is for the **developer or attendee** who opens the repository
after the talk. It is not a maintainer log.

## Structure

Bilingual when the audience is Japanese: one file with a language switch
near the top, the Japanese section first, then English with the same
headings.

```markdown
![version](https://img.shields.io/badge/version-21%20R5-E23089)
![platform](https://img.shields.io/static/v1?label=platform&message=mac-arm%20|%20mac-intel%20|%20win-64&color=blue)

# <RepoName>

[日本語](#日本語) | [English](#english)

---

## 日本語
### このデモでわかること / はじめかた / デモの進めかた / しくみ / データを作り直すには

---

## English
### What it demonstrates
### Requirements
### Getting started
### Running the demo
### How it works
### Rebuilding the data

## References
## Screenshots            (optional)
## Modernisation notes    (converted legacy demos only)
```

| Section | Content |
|---|---|
| Badges | version = the 4D release that `compatibilityVersion` targets; platforms actually supported |
| Intro | one paragraph: the feature, the data, what runs locally |
| What it demonstrates | 4-8 bullets, each backed by code in the repo, naming the 4D API |
| Requirements | 4D version, first-launch network, **disk space** (data + models) |
| Getting started | clone, download `Data.zip` from Releases and where to put it, open, what happens on first launch |
| Running the demo | the live script: which sample to pick, what to toggle, what to compare; quote real numbers (hit counts, ms) |
| How it works | real method/form names and the flow; the one piece of code worth reading |
| Rebuilding the data | generator script + headless command line |
| References | 4D docs, components, model card **and** the exact GGUF repository used |
| Modernisation notes | only for converted legacy demos: one row per branch **that exists on the remote**, linking the guiding skill |

## Rules

* Every claim comes from the code. Read the methods and forms before
  writing. Never invent command names.
* No Copilot, model-selection, token or session content.
* English: terse, British spelling, ASCII punctuation (`--`, straight
  quotes). Japanese: natural です/ます prose, full-width punctuation;
  keep 4D API names in backticks untranslated (`4dlocalise`).
* Numbers (sizes, timings, hit counts) are measured on the shipped data.
  Re-measure them when the data or the model changes.
* State that demo data is fictitious when it is generated.
* Say which language the shipped data is in when it differs by UI
  language, and how to regenerate it in the other.
