# Form Themes: Liquid Glass & Fluent UI

References:
- Liquid Glass announcement: https://blog.4d.com/the-new-macos-tahoe-design-comes-to-your-4d-applications/
- CSS media queries: https://developer.4d.com/docs/FormEditor/stylesheets#media-queries
- `FORM theme` command: https://developer.4d.com/docs/commands/form-theme
- Apple Liquid Glass: https://developer.apple.com/documentation/technologyoverviews/liquid-glass

Starting with macOS Tahoe (macOS 26) and 4D 21 R3, Apple's Liquid Glass
visual language is applied automatically to 4D desktop applications. No
code change is strictly required, but push buttons and dropdowns need
height adjustments to render correctly. Version gates: "4D Version
Detection" in `skills/4dproject/SKILL.md`. Stylesheet files, syntax and
specificity: `../SKILL.md`.

## Form Theme Media Queries

4D supports the `form-theme` media feature in CSS stylesheets. This allows you to write theme-specific rules that apply automatically based on the active platform rendering.

### Available `form-theme` Values

| Value | Platform | Description |
|-------|----------|-------------|
| `liquid-glass` | macOS Tahoe+ (4D 21 R3+) | Apple's translucent Liquid Glass rendering |
| `mac-classic` | macOS (pre-Tahoe or compatibility mode) | Traditional macOS control rendering |
| `fluent-ui` | Windows 11+ (4D 21 R2+) | Microsoft Fluent UI rendering |
| `win-classic` | Windows (classic) | Traditional Windows control rendering |

### Available `prefers-color-scheme` Values

| Value | Description |
|-------|-------------|
| `light` | Light colour scheme |
| `dark` | Dark colour scheme |

> **Note:** Colour schemes are not supported with the `win-classic` platform theme.

### Syntax

```css
@media (form-theme: liquid-glass) {
    /* macOS Tahoe Liquid Glass rules */
}

@media (form-theme: mac-classic) {
    /* classic macOS rules */
}

@media (form-theme: fluent-ui) {
    /* Windows Fluent UI rules */
}

@media (form-theme: win-classic) {
    /* classic Windows rules */
}
```

Media queries can be nested for theme + colour scheme combinations:

```css
@media (form-theme: fluent-ui) {
    .myClass {
        stroke: #2A2A2A;
    }

    @media (prefers-color-scheme: dark) {
        .myClass {
            stroke: #E0E0E0;
        }
    }
}
```


## Button Sizing for Liquid Glass

### The Problem

In Liquid Glass, push buttons have two visual variants based on height:

- **Regular variant** — square corners (shorter buttons)
- **Large variant** — rounded corners with Liquid Glass translucency (taller buttons)

The switch between these variants occurs at a **one-pixel threshold**. A button must be at least **27px high** to receive the rounded Liquid Glass appearance.

Many legacy forms use hardcoded button heights of 20px or 23px. These render as flat, square buttons under Liquid Glass, which looks inconsistent with the rest of the Tahoe UI.

### The Fix

Use CSS media queries in `styleSheets_mac.css` to set appropriate button heights per theme. Define height on **both** the class-only selector (`.default`) and the compound type+class selector (`button.default`):

```css
@media (form-theme: liquid-glass) {
    .default {
        height: 27px;
    }

    button.default {
        height: 27px;
    }
}

@media (form-theme: mac-classic) {
    .default {
        height: 23px;
    }

    button.default {
        height: 23px;
    }
}
```

**Why both selectors?** In practice, 4D's CSS engine may not always match a compound `button.default` selector at runtime, even when the form object is clearly a button. Using the class-only `.default` selector as a fallback ensures the height rule is applied reliably. The compound `button.default` selector is kept for specificity when other object types also use the `default` class but should not receive button sizing.

**This was discovered in practice**: a button with `"class": "default"` and no `height` in the form JSON rendered as a flat, square button because only `button.default` was defined in the CSS. Adding `.default` alongside it fixed it immediately.

### Mandatory Audit Scope: Every Button and Dropdown in Every Form

Control height is a project-wide concern, not a single-form concern. Before
declaring this migration done, enumerate every button **and** every
dropdown in **every** `form.4DForm` file in the project -- not just the
form you happen to be looking at, and not just the first control you
notice.

```
grep -rn '"type": "button"\|"type": "dropdown"' Project/Sources/Forms/ Project/Sources/TableForms/
```

For each button, check the enclosing object for a `height` (or `bottom`)
property and a `class` property. A button is only "done" once **both**:

1. `height`/`bottom` has been removed, and
2. `"class": "default"` (or the appropriate class) has been added.

**This was missed in practice**: a pass migrated the one button on the
first form, confirmed that no *other object* used the new class yet, and
stopped -- while five buttons on a second form kept a hardcoded
`height: 20`/`21` and rendered flat and square next to the one rounded
button.

**Rule:** "no other button uses this class yet" is not a stopping point --
it is a prompt to find every other button that should use it.

### Critical: CSS Specificity vs Form JSON

Properties defined directly in the `.4DForm` JSON have **the highest specificity** and override CSS rules — unless the CSS uses `!important` (which is discouraged).

Therefore, for CSS-driven sizing to work:

1. **Remove** the `height` property from the button definition in `form.4DForm`
2. **Remove** the `bottom` property if present (it implicitly constrains height)
3. **Keep only** positioning properties: `top`, `left`, `width` (or `right`)
4. **Add** a `"class"` property to the button (e.g., `"class": "default"`) so the CSS selector matches

**Before (CSS will NOT take effect):**
```json
"MyButton": {
    "type": "button",
    "top": 520,
    "left": 614,
    "width": 90,
    "height": 20,
    "text": "OK"
}
```

**After (CSS controls height):**
```json
"MyButton": {
    "type": "button",
    "top": 520,
    "left": 614,
    "width": 90,
    "text": "OK",
    "class": "default"
}
```

### Choosing a CSS Class Name

Use a class name that reflects the button's role or style tier. Common conventions:

| Class | Use case |
|-------|----------|
| `default` | Standard push buttons (OK, Cancel, etc.) |
| `toolbar` | Toolbar-style buttons with different sizing |
| `small` | Intentionally compact buttons |

You may combine type and class selectors in CSS: `button.default` targets only buttons with the `default` class — it will not affect other object types.


## Adapting Other Controls

### Radio Buttons and Checkboxes

Under Liquid Glass, radio buttons and checkboxes render slightly larger. Review spacing and alignment around these controls to ensure they do not overlap adjacent objects.

### Combo Boxes

Combo boxes use translucent rendering under Liquid Glass, meaning background objects may show through. If overlapping objects exist behind a combo box, adjust their visibility or z-order to prevent visual clutter.

### Dropdown / Popup Menus

Dropdown and popup menu controls (`"type": "dropdown"`) follow the **same 27px height threshold** as push buttons. A dropdown must be at least **27px high** to receive the rounded Liquid Glass appearance; at 26px or below it renders as a flat, square control.

Unlike buttons, dropdowns are usually **not** managed via CSS classes -- their height stays in the form JSON. Ensure every dropdown in the project has `"height": 27` (or greater), using the same project-wide grep as for buttons.

**This was missed in practice**: one dropdown was 26px while its sibling on the same form was 27px; one rendered with Liquid Glass styling and the other without.

### Sequences of Buttons

If a form contains multiple buttons in a row, ensure they all have **consistent heights**. A one-pixel difference can cause some buttons to render as square and others as rounded, creating a visually jarring mix.


## Runtime Theme Detection

The `FORM theme` command returns the current rendering mode as a string at runtime. Possible return values include:

| Value | Meaning |
|-------|---------|
| `"liquidGlass"` | Liquid Glass is active |
| `"classic"` | Classic rendering |

Use this when you need to adjust behaviour programmatically beyond what CSS can handle — for example, dynamically setting meta-source colours in listboxes.

```4d
If (FORM theme="liquidGlass")
    // adjust programmatic styling for Liquid Glass
End if
```

> **Prefer CSS over runtime detection** whenever possible. CSS media queries are declarative, automatic, and require no method code.


## Anti-Patterns to Avoid

### ❌ Leaving `height` in the form JSON when using CSS

```json
"height": 20,
"class": "default"
```

**Why:** The JSON property overrides CSS. The button will remain 20px regardless of your CSS rules.

### ❌ Using `!important` to override form JSON heights

```css
button.default {
    height: 27px !important;
}
```

**Why:** While this works, it makes the CSS harder to maintain and override later. Remove the property from the JSON instead.

### ❌ Using `bottom` to constrain height

```json
"top": 520,
"bottom": 540
```

**Why:** The `top` + `bottom` combination implicitly defines height. Remove `bottom` and let CSS control height.

### ❌ Hardcoding a single height without theme differentiation

```css
button.default {
    height: 27px;
}
```

**Why:** This gives 27px on classic macOS too, where 23px is the standard button height. Always use media queries to set theme-appropriate values.

### ❌ Putting macOS-specific rules in `styleSheets.css`

```css
/* In styleSheets.css — WRONG */
@media (form-theme: liquid-glass) {
    button.default { height: 27px; }
}
```

**Why:** `liquid-glass` and `mac-classic` are macOS-only themes. Place them in `styleSheets_mac.css`. Similarly, `fluent-ui` and `win-classic` rules belong in `styleSheets_windows.css`. Cross-platform rules (e.g., `prefers-color-scheme`) belong in `styleSheets.css`.

### ❌ Inconsistent button heights in a button group

```json
"BtnOK":     { "type": "button", "height": 27 },
"BtnCancel": { "type": "button", "height": 26 }
```

**Why:** A one-pixel difference causes one button to render rounded and the other square under Liquid Glass. Always use the same class and let CSS set a consistent height.

### ❌ Forgetting the `class` property on buttons

Creating a CSS rule for `button.default` but not adding `"class": "default"` to the button in the form JSON. The rule will not match.

### ❌ Using only the compound `button.default` selector

```css
/* WRONG — may not match at runtime */
@media (form-theme: liquid-glass) {
    button.default { height: 27px; }
}
```

**Why:** 4D's CSS engine may not reliably match the compound `button.default` selector for all button objects at runtime, even when the form object type is `"button"`. Always define height on **both** `.default` and `button.default` to ensure the rule applies.

### ❌ Migrating only the first form/button you find

**Why:** Fixing one button and checking that no other object uses the class
*yet* leaves every other button (and dropdown) on every other form
unmigrated. Always grep `Project/Sources/Forms/` and
`Project/Sources/TableForms/` project-wide -- see "Mandatory Audit Scope"
above.

## Disabling Liquid Glass (Merged Applications Only)

For merged (engine-based) applications that need a transition period, add the `UIDesignRequiresCompatibility` key to the application's `Info.plist`:

```xml
<key>UIDesignRequiresCompatibility</key>
<true/>
```

This retains the classic visual style while you adapt interfaces. This key has **no effect** on 4D and 4D Server applications — they always use Liquid Glass on macOS 26+.


## Checklist

When adapting a 4D project for Liquid Glass:

- [ ] Ran `grep -rn '"type": "button"\|"type": "dropdown"' Project/Sources/Forms/ Project/Sources/TableForms/` and accounted for **every** result across **every** form — not just the form initially in scope
- [ ] `styleSheets_mac.css` exists in `Project/Sources/`
- [ ] `@media (form-theme: liquid-glass)` rule sets `height: 27px` for **both** `.default` and `button.default`
- [ ] `@media (form-theme: mac-classic)` rule sets `height: 23px` for **both** `.default` and `button.default`
- [ ] All target buttons in `form.4DForm` have `"class"` assigned (e.g., `"default"`)
- [ ] `height` property removed from target buttons in `form.4DForm`
- [ ] `bottom` property removed from target buttons in `form.4DForm` (if present)
- [ ] Only `top`, `left`, `width` (or `right`) remain as positioning properties
- [ ] All buttons in a visual group use the same class for consistent rendering
- [ ] All dropdowns (`"type": "dropdown"`) have `"height": 27` or greater in the form JSON
- [ ] No `!important` used to override JSON-defined heights (remove from JSON instead)
- [ ] Radio buttons and checkboxes reviewed for spacing under Liquid Glass
- [ ] Combo boxes reviewed for background transparency under Liquid Glass
- [ ] macOS-specific rules are in `styleSheets_mac.css`, not `styleSheets.css`
- [ ] Windows-specific rules (if any) are in `styleSheets_windows.css`
