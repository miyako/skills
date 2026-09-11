---
object: "any"
json_type: null
keywords: ["property", "JSON", "CSS", "getter", "setter", "schema", "reference"]
summary: "Cross-reference of form object properties from three angles: JSON key, CSS name, and getter/setter command, with the object types each applies to."
---

# Form Object Property Reference

Every form object property can be viewed from three angles:

1. **JSON schema** — the key name in the form's `.4DForm` file
2. **CSS stylesheet** — some properties have CSS equivalents usable in `.css` stylesheets applied via the `class` property
3. **Runtime commands** — `OBJECT SET …` / `OBJECT Get …` commands that read or modify properties at runtime

The tables below cross-reference all three. Not every property has a CSS name or a runtime command.

## Abbreviation Key

| Abbr | Object Type | Abbr | Object Type |
|------|-------------|------|-------------|
| txt | text (static) | ln | line |
| rect | rectangle | ovl | oval |
| grp | groupBox | tab | tab control |
| pic | picture (static) | inp | input |
| btn | button | chk | checkbox |
| rad | radio button | dd | dropdown |
| cmb | combo box | web | webArea |
| vp | view (4D View Pro) | wp | write (4D Write Pro) |
| sub | subform | plug | plugin area |
| spl | splitter | bg | buttonGrid |
| prog | progress indicator | rul | ruler |
| spin | spinner | step | stepper |
| lst | list (hierarchical) | pbtn | pictureButton |
| ppop | picturePopup | lb | listbox |
| lbc | listbox column | lbh | listbox header |
| lbf | listbox footer | | |

"**all**" = every object type via `objectCommon`.
"**all\***" = nearly all; exceptions noted.

---

## Geometry

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `top` | Top | — | all | `OBJECT GET COORDINATES` | `OBJECT SET COORDINATES` |
| `left` | Left | — | all | `OBJECT GET COORDINATES` | `OBJECT SET COORDINATES` |
| `right` | Right | — | all | `OBJECT GET COORDINATES` | `OBJECT SET COORDINATES` |
| `bottom` | Bottom | — | all | `OBJECT GET COORDINATES` | `OBJECT SET COORDINATES` |
| `width` | Width | — | all | `OBJECT GET COORDINATES` | `OBJECT SET COORDINATES` |
| `height` | Height | — | all | `OBJECT GET COORDINATES` | `OBJECT SET COORDINATES` |

## Sizing

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `sizingX` | Horizontal Sizing | — | all | `OBJECT GET RESIZING OPTIONS` | `OBJECT SET RESIZING OPTIONS` |
| `sizingY` | Vertical Sizing | — | all | `OBJECT GET RESIZING OPTIONS` | `OBJECT SET RESIZING OPTIONS` |

## Appearance

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `borderStyle` | Border Style | `border-style` | txt, inp, btn, web, vp, wp, sub, plug, spl, bg, prog, rul, spin, step, lst, pbtn, ppop, lb | `OBJECT Get border style` | `OBJECT SET BORDER STYLE` |
| `borderRadius` | Corner Radius | — | txt, inp | — | `OBJECT SET CORNER RADIUS` |
| `fill` | Background Color | `background-color` | txt, rect, ovl, inp, lst, lb, lbc, lbf | — | `OBJECT SET RGB COLORS` |
| `stroke` | Font/Line Color | `color` | txt, ln, rect, ovl, grp, inp, btn, chk, rad, dd, cmb, spl, prog, rul, lst, lb, lbc, lbh, lbf | — | `OBJECT SET COLOR` / `OBJECT SET RGB COLORS` |
| `visibility` | Visibility | — | all | `OBJECT Get visible` | `OBJECT SET VISIBLE` |
| `alternateFill` | Alternate Background | — | lb, lbc | — | — |
| `strokeWidth` | Stroke Width | — | ln, rect, ovl | — | — |
| `strokeDashArray` | Stroke Dash Array | — | ln, rect, ovl | — | — |

## Font

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `fontFamily` | Font | `font-family` | txt, grp, tab, inp, btn, chk, rad, dd, cmb, prog, rul, lst, lb, lbc, lbh, lbf | `OBJECT Get font` | `OBJECT SET FONT` |
| `fontSize` | Font Size | `font-size` | txt, grp, tab, inp, btn, chk, rad, dd, cmb, prog, rul, lst, lb, lbc, lbh, lbf | `OBJECT Get font size` | `OBJECT SET FONT SIZE` |
| `fontStyle` | Italic | `font-style` | txt, grp, tab, inp, btn, chk, rad, dd, cmb, prog, rul, lst, lb, lbc, lbh, lbf | `OBJECT Get font style` | `OBJECT SET FONT STYLE` |
| `fontWeight` | Bold | `font-weight` | txt, grp, tab, inp, btn, chk, rad, dd, cmb, prog, rul, lst, lb, lbc, lbh, lbf | `OBJECT Get font style` | `OBJECT SET FONT STYLE` |
| `textDecoration` | Underline / Strikethrough | `text-decoration` | txt, grp, tab, inp, btn, chk, rad, dd, cmb, prog, rul, lst, lb, lbc, lbh, lbf | `OBJECT Get font style` | `OBJECT SET FONT STYLE` |

## Text

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `text` | Title | — | txt, grp, btn, chk, rad, lbh | `OBJECT Get title` | `OBJECT SET TITLE` |
| `textAlign` | Horizontal Alignment | `text-align` | txt, grp, inp, btn, chk, rad, dd, cmb, lb, lbc, lbh, lbf | `OBJECT Get horizontal alignment` | `OBJECT SET HORIZONTAL ALIGNMENT` |
| `verticalAlign` | Vertical Alignment | `vertical-align` | lb, lbc, lbh, lbf | `OBJECT Get vertical alignment` | `OBJECT SET VERTICAL ALIGNMENT` |
| `textAngle` | Text Orientation | — | txt, inp | `OBJECT Get text orientation` | `OBJECT SET TEXT ORIENTATION` |
| `placeholder` | Placeholder | — | inp, cmb | `OBJECT Get placeholder` | `OBJECT SET PLACEHOLDER` |
| `fontTheme` | Font Theme | — | txt, inp | — | — |

## Data

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `dataSource` | Data Source | — | tab, inp, btn, chk, rad, dd, cmb, web, vp, wp, sub, plug, spl, bg, prog, rul, spin, step, lst, pbtn, ppop, lb, lbc, lbh, lbf | `OBJECT Get data source` | `OBJECT SET DATA SOURCE` |
| `dataSourceTypeHint` | Data Source Type | — | tab, inp, chk, rad, dd, cmb, sub, plug, spl, bg, prog, rul, spin, step, lst, lbc, lbf | — | — |
| `memorizeValue` | Save Value | — | tab, inp, chk, rad, dd, cmb, spl, lb | — | — |
| `defaultValue` | Default Value | — | inp | — | — |

## Entry

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `enterable` | Enterable | — | inp, chk, wp, step, prog, rul, lst, lb (via lbc) | `OBJECT Get enterable` | `OBJECT SET ENTERABLE` |
| `focusable` | Focusable | — | inp, btn, chk, rad, dd, wp, sub, plug, step, lst, lb | — | — |
| `hideFocusRing` | Hide Focus Ring | — | inp, wp, sub, lst, lb | `OBJECT Get focus rectangle invisible` | `OBJECT SET FOCUS RECTANGLE INVISIBLE` |
| `spellcheck` | Spellcheck | — | inp, wp | `OBJECT Get spellcheck` | `OBJECT SET SPELLCHECK` |
| `contextMenu` | Context Menu | — | inp, web, wp, lst (via lbc) | `OBJECT Get context menu` | `OBJECT SET CONTEXT MENU` |
| `showSelection` | Show Selection | — | inp, wp | — | — |

## Format

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `textFormat` | Text Format | — | inp, dd, cmb, lbc, lbf | `OBJECT Get format` | `OBJECT SET FORMAT` |
| `numberFormat` | Number Format | — | inp, dd, cmb, prog, rul, lbc, lbf | `OBJECT Get format` | `OBJECT SET FORMAT` |
| `dateFormat` | Date Format | — | inp, dd, cmb, lbc, lbf | `OBJECT Get format` | `OBJECT SET FORMAT` |
| `timeFormat` | Time Format | — | inp, dd, cmb, lbc, lbf | `OBJECT Get format` | `OBJECT SET FORMAT` |
| `booleanFormat` | Boolean Format | — | inp, lbc | `OBJECT Get format` | `OBJECT SET FORMAT` |
| `pictureFormat` | Picture Format | — | inp, pic, lbc, lbf | `OBJECT Get format` | `OBJECT SET FORMAT` |

## Lists

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `choiceList` | Choice List | — | inp, dd, cmb, lbc | `OBJECT Get list name` | `OBJECT SET LIST BY NAME` / `OBJECT SET LIST BY REFERENCE` |
| `requiredList` | Required List | — | inp, lbc | `OBJECT Get list name` | `OBJECT SET LIST BY NAME` |
| `excludedList` | Excluded List | — | inp, cmb, lbc | `OBJECT Get list name` | `OBJECT SET LIST BY NAME` |
| `saveAs` | Save As | — | dd, lbc | — | — |
| `automaticInsertion` | Automatic Insertion | — | cmb, lbc | — | — |
| `list` | Hierarchical List | — | lst | — | — |
| `labels` | Labels | — | tab | — | — |

## Range

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `min` | Minimum Value | — | inp, prog, rul, step | `OBJECT GET MINIMUM VALUE` | `OBJECT SET MINIMUM VALUE` |
| `max` | Maximum Value | — | inp, prog, rul, step | `OBJECT GET MAXIMUM VALUE` | `OBJECT SET MAXIMUM VALUE` |
| `step` | Step | — | prog, rul, step | — | — |
| `graduationStep` | Graduation Step | — | prog, rul | — | — |

## Scrollbar

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `scrollbarHorizontal` | Horizontal Scroll Bar | — | inp, wp, sub, lst, lb | `OBJECT GET SCROLLBAR` | `OBJECT SET SCROLLBAR` |
| `scrollbarVertical` | Vertical Scroll Bar | — | inp, wp, sub, lst, lb | `OBJECT GET SCROLLBAR` | `OBJECT SET SCROLLBAR` |

## Action

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `method` | Object Method | — | tab, inp, btn, chk, rad, dd, cmb, web, vp, wp, sub, plug, spl, bg, prog, rul, spin, step, lst, pbtn, ppop, lb, lbc | — | — |
| `action` | Standard Action | — | tab, btn, chk, dd, bg, pbtn, ppop, lb | `OBJECT Get action` | `OBJECT SET ACTION` |
| `events` | Events | — | all* (not txt, ln, rect, ovl, pic) | — | — |
| `tooltip` | Help Tip | — | tab, inp, btn, chk, rad, dd, cmb, spl, bg, prog, rul, spin, step, lst, pbtn, ppop, lbh, lbf | `OBJECT Get help tip` | `OBJECT SET HELP TIP` |

## Drag & Drop

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `dragging` | Dragging | — | inp, cmb, wp, plug, lst, lb | `OBJECT GET DRAG AND DROP OPTIONS` | `OBJECT SET DRAG AND DROP OPTIONS` |
| `dropping` | Dropping | — | inp, btn, cmb, wp, plug, lst, pbtn, lb | `OBJECT GET DRAG AND DROP OPTIONS` | `OBJECT SET DRAG AND DROP OPTIONS` |

## Shortcut

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `shortcutKey` | Shortcut Key | — | btn, chk, rad, pbtn | — | `OBJECT SET SHORTCUT` |
| `shortcutAccel` | Shortcut with Accel | — | btn, chk, rad, pbtn | — | `OBJECT SET SHORTCUT` |
| `shortcutControl` | Shortcut + Control | — | btn, chk, rad, pbtn | — | `OBJECT SET SHORTCUT` |
| `shortcutCommand` | Shortcut + Command | — | btn, chk, rad, pbtn | — | `OBJECT SET SHORTCUT` |
| `shortcutShift` | Shortcut + Shift | — | btn, chk, rad, pbtn | — | `OBJECT SET SHORTCUT` |
| `shortcutAlt` | Shortcut + Alt | — | btn, chk, rad, pbtn | — | `OBJECT SET SHORTCUT` |

## Button-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `style` | Button Style | — | btn, chk, rad | — | — |
| `defaultButton` | Default Button | — | btn | — | — |
| `display` | Display | — | btn, dd | — | — |
| `textPlacement` | Title/Picture Position | — | btn, chk, rad | — | — |
| `icon` | Icon | — | btn, chk, rad, lbh | — | — |
| `iconFrames` | Icon Frames | — | btn, chk, rad | — | — |
| `popupPlacement` | With Pop-up Menu | — | btn | — | — |
| `customBackgroundPicture` | Custom Background | — | btn, chk, rad | — | — |
| `customBorderX` | Custom Horizontal Margin | — | btn, chk, rad | — | — |
| `customBorderY` | Custom Vertical Margin | — | btn, chk, rad | — | — |
| `customOffset` | Custom Offset | — | btn, chk, rad | — | — |
| `imageHugsTitle` | Image Hugs Title | — | btn, chk, rad | — | — |

## Checkbox/Radio-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `threeState` | Three-States | — | chk | — | — |
| `radioGroup` | Radio Group | — | rad | — | — |

## Input-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `styledText` | Styled Text / Multi-style | — | inp | — | `OBJECT SET STYLED TEXT` |
| `storeDefaultStyle` | Store Default Style | — | inp | — | — |
| `multiline` | Multiline | — | inp | — | — |
| `wordwrap` | Wordwrap | — | inp, lbc | — | — |
| `allowFontColorPicker` | Allow Font/Color Picker | — | inp | — | — |
| `printFrame` | Print Frame | — | inp, wp | `OBJECT Get print variable frame` | `OBJECT SET PRINT VARIABLE FRAME` |
| `keyboardDialect` | Keyboard Dialect | — | inp, wp | — | — |
| `entryFilter` | Entry Filter | — | inp, cmb, lst, lbc | — | — |

## Indicator-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `continuousExecution` | Continuous Execution | — | prog, rul, step | — | — |
| `showGraduations` | Show Graduations | — | prog, rul | — | — |
| `labelsPlacement` | Label Location | — | tab, prog, rul | — | — |

## List Box-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `listboxType` | List Box Type | — | lb | — | — |
| `columns` | Columns | — | lb | — | — |
| `showHeaders` | Show Headers | — | lb, wp | — | — |
| `showFooters` | Show Footers | — | lb, wp | — | — |
| `headerHeight` | Header Height | — | lb | — | — |
| `footerHeight` | Footer Height | — | lb | — | — |
| `horizontalLineStroke` | Horizontal Line Color | — | lb | — | — |
| `verticalLineStroke` | Vertical Line Color | — | lb | — | — |
| `staticColumnCount` | Number of Static Columns | — | lb | — | — |
| `lockedColumnCount` | Number of Locked Columns | — | lb | — | — |
| `sortable` | Sortable | — | lb | — | — |
| `movableRows` | Movable Rows | — | lb | — | — |
| `selectionMode` | Selection Mode | — | sub, lst, lb | — | — |
| `singleClickEdit` | Single-Click Edit | — | lb | — | — |
| `highlightSet` | Highlight Set | — | lb | — | — |
| `hideSystemHighlight` | Hide System Highlight | — | lb | — | — |
| `hideExtraBlankRows` | Hide Extra Blank Rows | — | lb | — | — |
| `rowHeight` | Row Height | — | lb | — | — |
| `rowHeightSource` | Row Height Array | — | lb | — | — |
| `rowHeightAutoMin` | Row Height Auto Min | — | lb | — | — |
| `rowHeightAutoMax` | Row Height Auto Max | — | lb | — | — |
| `rowHeightAuto` | Row Height Automatic | — | lbc | — | — |
| `resizingMode` | Column Auto-Resizing | — | lb | — | — |
| `horizontalPadding` | Horizontal Padding | — | lb, lbc, lbh, lbf | — | — |
| `verticalPadding` | Vertical Padding | — | lb, lbc, lbh, lbf | — | — |
| `selectionName` | Selection Name | — | lb | — | — |
| `currentItemSource` | Current Item | — | lb | — | — |
| `currentItemPositionSource` | Current Item Position | — | lb | — | — |
| `selectedItemsSource` | Selected Items | — | lb | — | — |
| `metaSource` | Meta Info Expression | — | lb | — | — |
| `rowStrokeSource` | Row Font Color Array | — | lb, lbc | — | — |
| `rowFillSource` | Row Background Color Array | — | lb, lbc | — | — |
| `rowStyleSource` | Row Style Array | — | lb, lbc | — | — |
| `rowControlSource` | Row Control Array | — | lb | — | — |
| `doubleClickInRowAction` | Double-click on Row | — | sub, lb | — | — |
| `truncateMode` | Truncate with Ellipsis | — | lbc, lbf | — | — |
| `resizable` | Resizable | — | lbc | — | — |
| `minWidth` | Minimum Width | — | lbc | — | — |
| `maxWidth` | Maximum Width | — | lbc | — | — |
| `controlType` | Display Type | — | lbc | — | — |
| `controlTitle` | Display Title | — | lbc | — | — |
| `values` | Values | — | lbc | — | — |
| `header` | Header Object | — | lbc | — | — |
| `footer` | Footer Object | — | lbc | — | — |
| `name` | Object Name | — | lbc, lbh, lbf | — | — |
| `iconPlacement` | Icon Placement | — | lbh | — | — |
| `variableCalculation` | Variable Calculation | — | lbf | — | — |

## Subform-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `detailForm` | Detail Form | — | sub, lb | — | `OBJECT SET SUBFORM` |
| `listForm` | List Form | — | sub | — | `OBJECT SET SUBFORM` |
| `table` | Table | — | sub, lb | — | — |
| `enterableInList` | Enterable in List | — | sub | — | — |
| `deletableInList` | Deletable in List | — | sub | — | — |
| `doubleClickInEmptyAreaAction` | Double-click on Empty Row | — | sub | — | — |

## Web Area-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `webEngine` | Web Engine | — | web | — | — |
| `progressSource` | Progress Variable | — | web | — | — |
| `urlSource` | URL Variable | — | web | — | — |
| `methodsAccessibility` | Access 4D Methods | — | web | — | — |

## Write Pro-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `dpi` | Resolution (DPI) | — | wp | — | — |
| `zoom` | Zoom | — | wp | — | — |
| `layoutMode` | View Mode | — | wp | — | — |
| `showHTMLWysiwyg` | Show HTML WYSIWYG | — | wp | — | — |
| `showHiddenChars` | Show Hidden Characters | — | wp | — | — |
| `showPageFrames` | Show Page Frame | — | wp | — | — |
| `showHeaders` | Show Header | — | wp, lb | — | — |
| `showFooters` | Show Footer | — | wp, lb | — | — |
| `showBackground` | Show Background | — | wp | — | — |
| `showReferences` | Show References | — | wp | — | — |
| `showHorizontalRuler` | Show Horizontal Ruler | — | wp | — | — |
| `showVerticalRuler` | Show Vertical Ruler | — | wp | — | — |
| `showEmptyImages` | Show Empty Images | — | wp | — | — |
| `showTableBorders` | Show Table Borders | — | wp | — | — |
| `displayFormulaAsSymbol` | Display Formula as Symbol | — | wp | — | — |

## View Pro-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `userInterface` | User Interface | — | vp | — | — |
| `withFormulaBar` | Formula Bar | — | vp | — | — |

## Plugin-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `pluginAreaKind` | Plugin Area Kind | — | plug | — | — |
| `customProperties` | Custom Properties | — | plug | — | — |

## Picture-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `picture` | Picture Path | — | pic, pbtn, ppop | — | — |
| `rowCount` | Rows (frames) | — | bg, pbtn, ppop | — | — |
| `columnCount` | Columns (frames) | — | bg, pbtn, ppop | — | — |

## Picture Button-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `switchContinuously` | Switch Continuously | — | pbtn | — | — |
| `loopBackToFirstFrame` | Loop Back to First Frame | — | pbtn | — | — |
| `switchWhenRollover` | Switch on Rollover | — | pbtn | — | — |
| `switchBackWhenReleased` | Switch Back When Released | — | pbtn | — | — |
| `useLastFrameAsDisabled` | Use Last Frame as Disabled | — | pbtn | — | — |
| `frameDelay` | Frame Delay | — | pbtn | — | — |

## Line/Shape-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `startPoint` | Start Point | — | ln | — | — |

## Splitter-Specific

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `splitterMode` | Splitter Mode | — | spl | — | — |

## Miscellaneous

| JSON Key | Doc Name | CSS Name | Applicable Types | Getter | Setter |
|---|---|---|---|---|---|
| `class` | CSS Class / Style Sheet | — | all, lbc, lbh, lbf | — | `OBJECT SET STYLE SHEET` |
| `type` | Object Type | — | all (required) | — | — |

---

## Properties NOT Settable via CSS

The following properties have **no CSS equivalent** and must be set in the JSON form definition or via runtime commands:

- **`method`** — object method (project method name)
- **`type`** — object type discriminator
- **`class`** — applies a CSS stylesheet but is not itself a CSS property
- **`events`** — event array
- **List-type properties** — `choiceList`, `requiredList`, `excludedList`, `labels`, `list`
