#declare()
// Object Method: dropObject
// Events handled: onClick, onDataChange

Case of 
	: (Form event code=On Clicked) | (Form event code=On Data Change)
		// For an object-based dropdown:
		// - Form.dropObject.index is the 0-based index of the chosen item (-1 if placeholder)
		// - Form.dropObject.currentValue is the chosen item's value
		If (Form.dropObject.index#-1)
			Form.objectResult:=String(Form.dropObject.currentValue)
		Else 
			Form.objectResult:=""
		End if
End case
