---
object: "subform"
json_type: "subform"
keywords: ["subform", "page subform", "detailForm", "Form", "bound object", "CALL SUBFORM CONTAINER", "EXECUTE METHOD IN SUBFORM", "FORM GOTO PAGE", "OBJECT SET SUBFORM", "widget"]
summary: "Page subform container: what Form returns inside a subform, form classes in subforms, value synchronisation, child-to-parent and parent-to-child calls, page changes inside a subform."
---

# 4D Subform Object (Page Subform)

Reference: https://developer.4d.com/docs/FormObjects/subformOverview
Properties: `references/property-reference.md` ("Subform-Specific")

Some rules adapted from the 4d-depot agent instructions by Mathieu Ferry
(MIT License).

## Basic Definition

```json
{
  "addressArea": {
    "type": "subform",
    "left": 20,
    "top": 60,
    "width": 400,
    "height": 160,
    "detailForm": "AddressEditor",
    "dataSource": "Form.address",
    "focusable": false
  }
}
```

`detailForm` names the form shown inside the container (a project form, or
a table form of any table). Its coordinates are local to the container.

## What `Form` Is Inside the Subform

* `Form` in the subform returns the object bound to the container
  (`dataSource`). Objects are passed by reference, so the parent and the
  subform share one object: a change on either side is visible on the
  other.
* Without a `dataSource`, 4D binds an empty object to the container.
* The subform's own `formClass` is **not** what `Form` returns there
  (observed: the container's bound object wins, as formData does for
  `DIALOG`). To use class functions in the subform, the parent creates the
  instance and binds it:

  ```4d
  // parent form, On Load
  Form.address:=cs.AddressEditor.new()
  ```

* To swap the form shown in a container at runtime:
  `OBJECT SET SUBFORM(*; "addressArea"; "OtherForm")`.

## Synchronising a Single Value

For a scalar binding (e.g. `Form.parisTime`), exchange the value explicitly:

| Direction | Code |
|---|---|
| Parent → subform | Subform form method, `On Bound Variable Change`: `Form.clock:=OBJECT Get subform container value` |
| Subform → parent | `OBJECT SET SUBFORM CONTAINER VALUE(Form.clock)` |

`On Bound Variable Change` fires only when the subform is on the current
page or page 0.

## Calls Between Parent and Subform

| Direction | Command | Notes |
|---|---|---|
| Subform → parent | `CALL SUBFORM CONTAINER(-101)` | The event is received in the **container's object method** (`Form event code` = -101). Use negative custom codes; an existing event code is delivered only if that event is checked on the container. |
| Parent → subform | `EXECUTE METHOD IN SUBFORM("addressArea"; Formula(Form.refresh()); *)` | Runs in the subform context. `*` when nothing is returned; parameters follow `*`. |

Events a subform container itself supports: On Load, On Validate, On
Getting Focus, On Losing Focus, On Data Change, On Unload.

A formula created in the subform and passed to the parent (or the reverse)
runs with `This` resolved at call time -- capture objects in a local
variable first (`skills/4dlang/references/pitfalls.md`).

## Pages Inside a Subform

* `FORM GOTO PAGE(2; *)` changes the page of the subform that calls it.
  Without `*` it changes the **parent** form's page.
* The `gotoPage` standard action on a button inside a subform was observed
  to act on the parent form: drive subform pages from code with
  `FORM GOTO PAGE(...; *)`.
* Subform containers on page 2+ miss resize events
  (`references/form-concepts.md`, "Sizing on Non-Visible Pages").
