# Localising a demo's companion browser page

This reference covers the integration decisions for a browser page that
accompanies a 4D demo. It does not replace the implementation rules for
page dictionaries, XLIFF, placeholders or served HTML in
`4dlocalise/references/web-pages.md`.

## Keep language choices distinct

The native 4D UI and the browser page are separate surfaces. The native
UI may follow the operating-system language and use paired XLIFF files;
the browser page may detect the browser's preferred language and offer a
selector. Agree which behavior the demo needs rather than assuming that a
4D localization change will update an already-open browser page.

For a browser-language default, choose a supported language from
`navigator.languages` (fall back to `navigator.language`, then the
project's default). Persist an explicit selector choice, and apply it on
subsequent visits. Keep the selection logic in one place so initial page
rendering, selector changes and dynamic content use the same language.
If the page is intentionally required to mirror the native UI, pass the
language explicitly as described in `4dlocalise/references/web-pages.md`;
document which source wins when a saved browser choice and an explicit
language parameter disagree.

Translation must cover more than the initial static DOM. Route later
status, result, error and progress text through the same translation
function, and re-render or update those elements when the selected
language changes. Set the document's `lang` attribute and format dates
with the active page language. Do not silently leave newly generated
content in the source language.

## Map the served page and its requests

Before editing paths, identify which server owns each page and asset.
Project-root and component `WebFolder` directories are distinct roots;
do not assume that a page under one is available from the other. Verify
the actual URL, port and base path for every page and endpoint. Prefer a
relative, same-origin request such as `fetch('/runDemo')` when the page
and endpoint are served by the same origin. This avoids introducing a
second origin and unnecessary CORS configuration; it is not proof that
the endpoint is authorized or safe to expose.

If SSL is disabled or CORS is permissive, treat the demo as trusted-local-
network software only, document that limitation in its README, and do not
present it as safe for untrusted or public networks. Prefer enabling
transport security and narrowing allowed origins before broadening
distribution.

## Verification and evidence limits

Check the browser in each supported language, including after changing
the selector and after dynamic results arrive. Exercise the same-origin
endpoint from the actual served page. A timed-out browser smoke test is
inconclusive: report the timeout and leave the behavior unverified rather
than treating it as a pass.

Keep project-specific unresolved items separate from general guidance.
In the source demo handoff for this guidance, the following remained
unverified or unresolved: native form titles stored in `Data/Data.4DD`,
floating 4D dependency references, and a missing `00_Start` menu method.
No 4D runtime/LSP validation or Japanese native-UI review was available,
and the browser JavaScript smoke test timed out. These are not established
defects in other 4D projects; inspect and verify them in the project being
worked on.

The same handoff reported ten static labels in paired English/Japanese
XLIFF, OS-language selection for the native UI, browser-language detection
with a persistent selector and dynamic page translation, separate
component and project-root `WebFolder` pages, and a same-origin
`/runDemo` endpoint on port 8044 for the component page. These are
observations about that demo, not required paths, counts or port numbers
for other projects. Its cleanup also removed an undefined
`loadSessionCounts()` call, an unreferenced `ticketingSession.js`, and
explicit Latin-only fonts; the latter follows the existing font guidance
in `4dcss`.
