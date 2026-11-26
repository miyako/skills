# Moving UI text out of the data file

Older demos keep their instructions, tab titles or help pages in a table
(an `INFO` table with a `PageNumber` and styled-text `Description`) inside
a committed `Data/data.4DD`. That text is not greppable, not diffable and
has one language. Move it to XLIFF so it is localised like every other
string. Different from `language-attributes.md`, which keeps per-language
**data** in the data file on purpose.

## Recipe (verified on a 4D 21 R5 demo, 13 styled-text rows)

1. **Find it.** Grep the code for queries that feed labels, tabs or
   descriptions (`ds.INFO.query(...)`, `QUERY([INFO]...)`, `.toCollection()`
   assigned to a form variable). The forms show only the variable.
2. **Extract it with tool4d** (`4dcli`): on a temporary copy of the
   project, a throw-away startup method writes the rows as JSON and quits:

   ```4d
   var $rows:=ds.INFO.all().orderBy("PageNumber").toCollection("PageNumber,TabTitle,Description")
   File("/PACKAGE/info.json").setText(JSON Stringify($rows; *))
   QUIT 4D
   ```

   Use a `File` object, not `TEXT TO DOCUMENT` with a POSIX path, which
   wrote nothing in a headless run (`4dcli`, "Writing Output Files").
   Keep the original bytes: styled text uses CR line breaks and
   `<span style=...>` markup.
3. **Generate XLIFF** from a script (`xliff_pair.py` and "Styled text" in
   `../SKILL.md`). Fix typos in the English source while moving it and
   list them for the owner.
4. **Read it from XLIFF** in the init code instead of the table:

   ```4d
   Infos:=[]
   For ($i; 1; 8)
   	Infos.push({PageNumber: $i; TabTitle: Localized string("Step_Tab"+String($i)); Description: Localized string("Step_Info"+String($i))})
   End for 
   ```

   Remove the `READ WRITE` / `QUERY` lines that only served the text.
5. **Verify**: `xliff_check.py` (the `"Step_Tab"+String($i)` pattern is
   detected as a dynamic prefix), then the tool4d runtime test and
   `fourdform --language ja` renders (`../SKILL.md`, "Verification").
6. **Leave the table** in the catalog and data unless the owner agrees to
   drop it: removing a table changes the structure and the shipped data.
   Say in the PR that it is now unused.
