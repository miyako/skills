# 4D Project Layout

Reference: https://developer.4d.com/docs/Project/architecture

Given a project named `{ProjectName}`, the standard structure is:

```
{ProjectName}/
├── .gitignore
├── Project/
│   ├── {ProjectName}.4DProject
│   └── Sources/
│       ├── catalog.4DCatalog          # Database schema (XML)
│       ├── catalog_editor.json        # Visual layout for IDE (JSON)
│       ├── folders.json               # Explorer folder definitions
│       ├── menus.json                 # Menu bar definitions
│       └── roles.json                 # Security/permissions
└── Resources/
```

## .gitignore

```
# Data folder
[dD][aA][tT][aA]/

# Derived data
DerivedData/

# Libraries
Libraries/

# User preferences
userPreferences.*/

# Uncomment (remove the following # ) to ignore Trash
# Project/Trash

# System files
.DS_Store
ehthumbs.db
Thumbs.db
```

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

Default menu bar with File (Quit), Edit (standard items), and Mode (Design):

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

Methods are plain text files in `Project/Sources/Methods/`. When
`tokenizedText` is `false` in the `.4DProject` file, write **plain 4D code
without token suffixes** (no `:C###` or `:K##:##`).

**File**: `Project/Sources/Methods/{MethodName}.4dm`

- Method names follow the same identifier rules (max 31 chars, no reserved
  names -- see the `4dcatalog` skill for the full list).
- Methods are auto-discovered by 4D -- no registration needed.
