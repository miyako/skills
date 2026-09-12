#declare()
// Button: btnGetList
// Programmatically inspects the choice list dropdown selection

Case of 
	: (Form event code=On Clicked)
		If (Form.dropList#"Please select an option…")
			ALERT("Choice List Dropdown Selection:\n"+\
				"Value: "+Form.dropList)
		Else 
			ALERT("No option selected yet (showing placeholder).")
		End if
End case
