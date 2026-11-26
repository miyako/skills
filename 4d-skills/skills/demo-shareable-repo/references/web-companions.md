# Companion Web Pages in a 4D Demo

Use this when an attendee-shared 4D project also serves a browser page, such
as a dashboard or a live-results view. This supplements
`4dlocalise`'s rules for translating served HTML; it covers discovery,
integration and evidence that the page works with the actual project.

## Find the page and server

Inventory each candidate page before editing URLs:

| What to identify | Check |
|---|---|
| Served files | Project-root `WebFolder/` and each relevant component's `WebFolder/` are separate roots; find the page and its assets in the correct one |
| Server and port | Inspect the relevant project/component configuration and confirm the running server's actual port; do not assume port 80 or that every page uses the project-root server |
| Route and origin | Record the URL path, which server serves it, and whether its API requests go to that same server |

When the page and endpoint share a server, build requests relative to the
page's origin rather than hard-coding a host or default port. If they use
different servers, make that choice explicit and verify the configured
origins.

## Keep language ownership clear

Use [`4dlocalise`'s web-page guidance](../../4dlocalise/references/web-pages.md)
for page dictionaries, placeholder handling and dynamic browser text. Keep
native form, method, menu and XLIFF work with `4dlocalise`; do not assume
XLIFF translates HTML.
Static dictionary checks do not cover text assembled dynamically: route
those strings through the page's translation helper and exercise each
relevant page state in every supported language.

Text visible in the browser may come from the 4D data file rather than
editable project source. Source searches cannot establish that such text
has been localised; inspect the data-backed page or query path and follow
[`4dlocalise`'s data-text migration guidance](../../4dlocalise/references/data-text-migration.md)
where appropriate.

## Verify the real integration

Static HTML/JavaScript checks can catch syntax and content issues, but do
not prove that 4D serves the page, that a route resolves, or that browser
requests reach the intended server. Open the page through the configured
4D server and test its real routes and dynamic states in a browser. Record
the verified 4D build, server origin/port and any unavailable runtime
checks. A static render or screenshot is not evidence of live 4D behavior.

Before changing a native launch path or menu entry, trace the actual
startup method and verify the referenced method exists. A stale-looking
menu reference alone does not establish which startup behavior is intended;
leave it unchanged and report the evidence if the entry point is unresolved.

## Make attendee requirements visible

In the README, identify the component or external service the page relies
on, its version provenance (including floating versions), and any required
network or security configuration. State observed TLS and CORS defaults
plainly. Do not silently pin dependencies, change origins, or weaken/alter
security settings: confirm the supported target and intended access policy
first ([`4dproject`'s dependency guidance](../../4dproject/references/dependencies.md)).

## Checklist

- [ ] Each page is mapped to its WebFolder root, server, configured port and route
- [ ] Requests use the intended origin; no assumed port or machine-specific URL remains
- [ ] Static and dynamic browser strings are covered in each supported language
- [ ] The actual 4D-served page and its interactive states were tested, or runtime gaps are stated
- [ ] Data-backed text, native startup/menu references and dependency provenance were checked
- [ ] README explains required network/security settings and observed TLS/CORS defaults
