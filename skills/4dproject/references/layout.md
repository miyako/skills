# 4D Project Layout and Boilerplate Files

Reference: https://developer.4d.com/docs/Project/architecture

Given a project named `{ProjectName}`, the standard structure is:

```
{ProjectName}/
├── .gitignore                         # see "## .gitignore" in ../SKILL.md
├── Project/
│   ├── {ProjectName}.4DProject        # see ../SKILL.md
│   └── Sources/
│       ├── catalog.4DCatalog          # database schema (XML) -- 4dcatalog skill
│       ├── catalog_editor.json        # visual layout for the Structure editor (JSON)
│       ├── folders.json               # Explorer folder definitions
│       ├── menus.json                 # menu bar definitions -- see menus.md
│       ├── roles.json                 # security/permissions
│       ├── settings.4DSettings        # structure settings -- 4dsettings skill
│       ├── styleSheets*.css           # form stylesheets -- 4dcss skill
│       ├── Methods/                   # project methods ({MethodName}.4dm)
│       ├── Classes/                   # class definitions ({ClassName}.4dm)
│       ├── DatabaseMethods/           # onStartup.4dm, onExit.4dm, ...
│       ├── Triggers/                  # table triggers
│       ├── Forms/{FormName}/          # project forms -- 4dform skill
│       └── TableForms/{tableNum}/{FormName}/
├── Resources/                         # images, XLIFF ({lang}.lproj/) -- 4dlocalise skill
├── Documentation/                     # developer-written .md docs for methods/classes/forms
└── Settings/                          # user settings (see "## .gitignore" in ../SKILL.md)
```

Each `.4dm` file maps to one method or class; the file name is the method
or class name. Methods and classes are auto-discovered by 4D -- no
registration is needed.

## catalog_editor.json

Stores visual/graphical data for the IDE structure editor (table positions,
colors, field colors). For agent-generated projects, use a minimal version:

```json
{
  "tables": {}
}
```

## folders.json

```json
{
  "Default Classes": {},
  "Default Folder": {
    "groups": [
      "Default Classes",
      "Default Forms",
      "Default Project Methods",
      "Default Tables"
    ]
  },
  "Default Forms": {},
  "Default Project Methods": {},
  "Default Tables": {},
  "trash": {}
}
```

## menus.json

Default menu bar with File (Quit), Edit (standard items), and Mode (Design).
Items use standard `"action"` values and 4D's built-in `Common*` XLIFF IDs;
see `menus.md` before adding or changing menu items.

```json
{
  "bars": [
    {
      "id": 1,
      "name": "Barre #1",
      "items": [
        { "link": 32001 },
        { "link": 32002 },
        { "link": 32003 }
      ]
    }
  ],
  "menus": [
    {
      "link": 32001,
      "title": ":xliff:CommonMenuFile",
      "items": [
        { "title": ":xliff:CommonMenuItemQuit", "shortcutAccel": true, "shortcutKey": "Q", "action": "quit" }
      ]
    },
    {
      "link": 32002,
      "title": ":xliff:CommonMenuEdit",
      "items": [
        { "title": ":xliff:CommonMenuItemUndo", "shortcutAccel": true, "shortcutKey": "Z", "action": "undo" },
        { "title": "(-", "isSeparator": true },
        { "title": ":xliff:CommonMenuItemCut", "shortcutAccel": true, "shortcutKey": "X", "action": "cut" },
        { "title": ":xliff:CommonMenuItemCopy", "shortcutAccel": true, "shortcutKey": "C", "action": "copy" },
        { "title": ":xliff:CommonMenuItemPaste", "shortcutAccel": true, "shortcutKey": "V", "action": "paste" },
        { "title": ":xliff:CommonMenuItemClear", "action": "clear" },
        { "title": ":xliff:CommonMenuItemSelectAll", "shortcutAccel": true, "shortcutKey": "A", "action": "selectAll" },
        { "title": "(-", "isSeparator": true },
        { "title": ":xliff:CommonMenuItemShowClipboard", "action": "showClipboard" }
      ]
    },
    {
      "link": 32003,
      "title": ":xliff:CommonMenuMode",
      "items": [
        { "title": ":xliff:CommonMenuItemDesign", "action": "design" }
      ]
    }
  ]
}
```

## roles.json

```json
{
  "forceLogin": false,
  "restrictedByDefault": false,
  "privileges": [],
  "roles": [],
  "permissions": {
    "allowed": [
      {
        "applyTo": "ds",
        "type": "datastore",
        "read": [],
        "create": [],
        "update": [],
        "drop": [],
        "execute": [],
        "promote": []
      }
    ]
  }
}
```

## Methods (.4dm files)

**File**: `Project/Sources/Methods/{MethodName}.4dm`

- Method names follow the same identifier rules (max 31 chars, no reserved
  names -- see the `4dcatalog` skill for the full list).
- The first line may carry method attributes (`//%attributes = {...}`) --
  see the `4dmethods` skill.
- Whether to write token suffixes (`:C###`) is governed by `tokenizedText`
  and the token rules in `../SKILL.md`.
- Validate every `.4dm` you write with the `4dlsp` skill.
