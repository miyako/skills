# Localising a page served by the project

Some demos open a companion HTML page in the browser (`OPEN URL` to the
project's web server, a component's `WebFolder/`). XLIFF does not reach
it. For a small static page, a JavaScript dictionary is enough and the
HTML stays untouched (verified on a 4D 21 R5 demo page with ~60 strings).

## Language from 4D

Pass the UI language in the URL so the page matches the 4D window, not
the browser:

```4d
$url+="&lang="+Get database localization(Current localization)
OPEN URL($url)
```

The page falls back to `navigator.language` when `?lang=` is absent.

## Dictionary file

Load `page.i18n.js` before the page's own script:

```html
<script src="./page.i18n.js"></script>
<script src="./page.js"></script>
```

```js
const LANG = (new URLSearchParams(location.search).get('lang') || navigator.language || 'en')
  .slice(0, 2).toLowerCase();

const I18N = {
  ja: {
    'Current Values': '現在の値',
    'Request {i} / {count}': 'リクエスト {i} / {count}',
  },
};

function t(text, vars = {}) {
  const dict = I18N[LANG] || {};
  const out = Object.prototype.hasOwnProperty.call(dict, text) ? dict[text] : text;
  return out.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? vars[k] : m));
}

function translatePage() {
  if (!I18N[LANG]) return;
  document.documentElement.lang = LANG;
  document.title = t(document.title);
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const key = node.nodeValue.replace(/\s+/g, ' ').trim();
    if (key && I18N[LANG][key] !== undefined) {
      const lead = /^\s/.test(node.nodeValue) ? ' ' : '';
      const trail = /\s$/.test(node.nodeValue) ? ' ' : '';
      node.nodeValue = lead + I18N[LANG][key] + trail;
    }
  }
  document.querySelectorAll('[title], [aria-label]').forEach((el) => {
    ['title', 'aria-label'].forEach((a) => {
      if (el.hasAttribute(a)) el.setAttribute(a, t(el.getAttribute(a)));
    });
  });
}

translatePage();
```

## Rules

* Keys are the **exact English text** of the node, whitespace collapsed.
  The English page needs no dictionary.
* Strings built in script go through `t('... {name} ...', {name})`, with
  named placeholders, never concatenation.
* **Inputs inside a sentence** ("Generate [1000] bytes of data") are
  separate text nodes around the input. Translate the fragments so the
  sentence reads in the target order: "Generate" → 「生成サイズ：」,
  "bytes of data" → 「バイト」.
* Dates and times use the page language
  (`toLocaleTimeString(LANG, ...)`), not a hard-coded locale.
* Translate code comments left in another language while you are there
  (attendees read the source).
* Check every page state (results, errors, bursts) in each language: the
  TreeWalker runs once, at load, and dynamic text relies on `t()`.

Pages with many strings or several pages: use a real i18n library and
keep one JSON per language next to the XLIFF table instead.
