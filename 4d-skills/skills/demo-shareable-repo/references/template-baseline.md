# Template Baseline vs Current Choices

An older personal template (miyako/HDI_Template, for the "How Do I"
collection) carries demo preferences. Treat it as a **baseline**: confirm
each row with the owner before applying it, and record in the PR which
ones were not adopted and why. The "Seen later" column is what owners chose
in later demo work. It is an example, not a rule.

| Template preference | Seen later | Owning skill |
|---|---|---|
| `.agents` git submodule (skills `dist` branch) + weekly update workflow | Dropped for a webinar shared with attendees: they only run the demo, and "Download ZIP" omits submodules. Ask. | `demo-shareable-repo` (step 9) |
| `.gitignore`: canonical 4D list, `Settings/` ignored, `userPreferences.*` | Kept. Use the directory pattern `userPreferences.*/`. | `4dproject` |
| Splash form `HDI` (title, blog link, version check, "run the demo" button) opening `HDI2` | Replaced by a launcher with a language toggle and one button per demo form | `demo-launcher`, `4dstartup` |
| Start method `00_Start` passing an options object to the splash | Any name; the `4dstartup` worker pattern, with the singleton check in the worker | `4dstartup` |
| README: badges, Key commands, How it works, Points of interest, Modernisation notes | Bilingual README (日本語 / English) with runtime screenshots per language; badges and Modernisation notes optional | `references/readme.md` |
| One branch per modernisation effort | Still valid | `demo-shareable-repo` (Workflow) |
| "The demo is the point": never change what the demo shows | Still valid; polish must not hide the subject | `polish-ui-pass` |
| English source + Japanese XLIFF | Still valid; add an in-app switch when both languages are shown | `4dlocalise` |
| Validate `.4dm` (4dlsp), `.4DForm` (4dform), XLIFF (xmllint) | Still valid; pin the tool4d build for 4dlsp | `4dlsp`, `4dform`, `4dtools` |
