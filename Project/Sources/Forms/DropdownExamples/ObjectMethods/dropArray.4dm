#declare()
// Object Method: dropArray
// Events handled: onClick, onDataChange

Case of 
	: (Form event code=On Clicked) | (Form event code=On Data Change)
		// For an array-based dropdown:
		// - asArrayChoices variable holds the selected element index (1-based, 0 if placeholder)
		// - asArrayChoices{asArrayChoices} yields the selected value
		If (asArrayChoices>0)
			Form.arrayResult:=asArrayChoices{asArrayChoices}
		Else 
			Form.arrayResult:=""
		End if
End case
