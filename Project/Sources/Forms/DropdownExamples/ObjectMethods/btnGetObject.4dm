#declare()
// Button: btnGetObject
// Programmatically inspects the object-based dropdown selection

Case of 
	: (Form event code=On Clicked)
		If (Form.dropObject.index#-1)
			ALERT("Object Dropdown Selection:\n"+\
				"Index (0-based): "+String(Form.dropObject.index)+"\n"+\
				"Value: "+String(Form.dropObject.currentValue))
		Else 
			ALERT("No option selected yet (index is -1, showing placeholder).")
		End if
End case
