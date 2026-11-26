# Japanese UI text

Conventions for `<target>` strings in `ja` XLIFF, served pages and
Japanese README sections, collected from en/ja 4D demos. Ask the owner
when a project already follows a different house style.

## Typography

| Rule | Example |
|---|---|
| Half-width space between Latin words or numbers and Japanese | 「4D Web サーバー」, 「次の 1 分間」 |
| Full-width colon after a label | 「バージョン：」, 「セッション数：」 |
| Full-width brackets and parentheses around Japanese text | 「データ送信（単発リクエスト）」 |
| Quote UI names with 「」, matching the button label exactly | 「適用」 ボタン, not 「適用する」 ボタン when the button says 適用 |
| No full-width Latin letters or digits | `429`, not `４２９` |

## Wording

* Labels and buttons: short noun phrases or verb stems (検索, 適用,
  今すぐテスト, リセット); messages that are sentences use です/ます.
* Keep API identifiers, commands and class names in Latin script and
  untranslated (`inBytesPerMin`, `WEB Server().quotas`, `4D.Vector`); keep
  4D terms Japanese users know in katakana (ベクトルインデックス,
  セッション, エンティティセット).
* In fixed-width chrome (brand, buttons, tabs, single-line headers) prefer
  a short native word over a katakana transliteration: "トラベル
  エージェンシー" wrapped or clipped where "旅行会社" fitted. Katakana
  loanwords are often *longer* than the English.
* Do not translate a product or series brand the owner keeps in English
  (e.g. "How do I..." for HDI demos); ask.
* Translate meaning, not word order: word order changes around
  placeholders (`{1} of {2}` → `{2} 件中 {1} 件`, `../SKILL.md`).

## Fonts and layout

* Japanese glyphs are taller: leave room above and below text boxes
  (`4dform`, `references/layout.md`), and check every label in a `ja`
  runtime capture (`../SKILL.md`, "Verification").
* Fonts without CJK glyphs (Lucida Grande, many Latin-only brand fonts)
  fall back unpredictably. Prefer the system font (`4dcss`, "Fonts").
