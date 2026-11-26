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

Identify the `WebFolder` root, server, port and route of each page and
endpoint as in
[`demo-shareable-repo`'s companion-page guidance](../../demo-shareable-repo/references/web-companions.md).
A relative, same-origin request (e.g. `fetch('/<endpoint>')`) avoids a
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
