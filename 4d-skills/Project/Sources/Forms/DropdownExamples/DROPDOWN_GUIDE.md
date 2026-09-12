# Dropdown Examples Form

This form demonstrates all three common ways to use dropdown lists in 4D forms.

## Overview

The form showcases:
1. **Object-based dropdown** (recommended modern approach)
2. **Array-based dropdown** (traditional 4D array approach)
3. **Choice list dropdown** (simple static list approach)

Each dropdown is populated with five items and displays the user's selection below it.

## How It Works

### 1. Object-based Dropdown
**Reference:** https://developer.4d.com/docs/FormObjects/dropdownListOverview

The **recommended** modern approach using 4D objects with these properties:
- `values`: Collection of items (0-based indexing)
- `index`: Selected index (-1 = no selection)
- `currentValue`: The actual value of the selected item (or placeholder when no selection)

**Form Data Source:**
```
dataSource: "Form.dropObject"
dataSourceTypeHint: "object"
```

**Initialization (method.4dm):**
```4d
Form.dropObject:=New object
Form.dropObject.values:=New collection("Apple"; "Banana"; "Cherry"; "Orange"; "Strawberry")
Form.dropObject.index:=-1
Form.dropObject.currentValue:="Please select an option…"
```

**Getting the Selected Value:**
```4d
If (Form.dropObject.index=-1)
    // No selection
Else
    $value:=Form.dropObject.currentValue
End if
```

---

### 2. Array-based Dropdown
**Reference:** https://developer.4d.com/docs/FormObjects/dropdownListOverview

Traditional approach using 4D arrays (still supported but superseded by object-based).
- 1-based indexing (elements start at index 1)
- Element 0 is reserved for the "no selection" placeholder
- The array variable itself holds the current selection index

**Form Data Source:**
```
dataSource: "asColor"
dataSourceTypeHint: "arrayText"
```

**Initialization (method.4dm):**
```4d
ARRAY TEXT(asColor; 5)
asColor{1}:="Red"
asColor{2}:="Green"
asColor{3}:="Blue"
asColor{4}:="Yellow"
asColor{5}:="Purple"
asColor{0}:="Please select a color…"
asColor:=0  // No selection initially
```

**Getting the Selected Value:**
```4d
If (asColor=0)
    // No selection
Else
    $value:=asColor{asColor}  // Idiom: asColor{asColor} = current value
End if
```

---

### 3. Choice List Dropdown
**Reference:** https://developer.4d.com/docs/FormObjects/propertiesDataSource#data-type-list

Simplest approach for static lists with inline values.
- Data source is a plain variable/field holding the selected value
- `saveAs: "value"` stores the literal text of the selected item
- `choiceList` can be inline or a reference to a toolbox list

**Form Definition:**
```json
{
  "type": "dropdown",
  "dataSource": "Form.dropChoice",
  "choiceList": ["Red", "Green", "Blue", "Yellow", "Purple"],
  "saveAs": "value"
}
```

**Initialization (method.4dm):**
```4d
Form.dropChoice:="Please select a color…"
```

**Getting the Selected Value:**
```4d
If (Form.dropChoice="Please select a color…")
    // No selection
Else
    $value:=Form.dropChoice
End if
```

---

## Form Events

All three dropdowns listen to:
- `onClick`: Fires when the dropdown is clicked
- `onDataChange`: Fires when the user selects an item

The form's object methods update the result labels when `onDataChange` fires, providing instant feedback.

## Resetting the Form

The **Reset** button demonstrates how to reset each dropdown type back to its initial "no selection" state:

**Object-based:** Set `index` to -1
**Array-based:** Set the array variable to 0
**Choice list:** Set the variable to the placeholder text

## File Structure

```
Forms/DropdownExamples/
├── form.4DForm                 # Form definition (pages, objects)
├── method.4dm                  # Form method (On Load, On Unload)
└── ObjectMethods/
    ├── dropObject.4dm          # Object-based dropdown handler
    ├── dropArray.4dm           # Array-based dropdown handler
    ├── dropChoice.4dm          # Choice list dropdown handler
    └── resetButton.4dm         # Reset button handler
```

## Documentation References

- **Official Dropdown Documentation:** https://developer.4d.com/docs/FormObjects/dropdownListOverview
- **Data Source Properties:** https://developer.4d.com/docs/FormObjects/propertiesDataSource
- **Blog Post - Modern Approach:** https://blog.4d.com/use-collections-and-lists-within-forms-objects/

## Best Practices

1. **Use object-based dropdowns** for new forms (modern, recommended)
2. **Always set a default/placeholder value** (`Please select an option…`)
3. **Check for "no selection"** before accessing the value:
   - Object: Check if `index = -1`
   - Array: Check if array variable `= 0`
   - Choice list: Check if variable matches placeholder
4. **Use `onDataChange`** event to react to user selections
5. **Avoid array-based** in new code (deprecated but still functional)

