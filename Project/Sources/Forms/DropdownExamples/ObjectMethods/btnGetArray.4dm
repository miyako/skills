#declare()
// Button: btnGetArray
// Programmatically inspects the array-based dropdown selection

Case of 
	: (Form event code=On Clicked)
		If (asArrayChoices>0)
			ALERT("Array Dropdown Selection:\n"+\
				"Element (1-based): "+String(asArrayChoices)+"\n"+\
				"Value: "+asArrayChoices{asArrayChoices})
		Else 
			ALERT("No option selected yet (element is 0, showing placeholder).")
		End if
End case
