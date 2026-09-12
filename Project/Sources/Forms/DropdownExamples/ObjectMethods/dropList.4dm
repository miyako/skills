#declare()
// Object Method: dropList
// Events handled: onClick, onDataChange

Case of 
	: (Form event code=On Clicked) | (Form event code=On Data Change)
		// For a choice list dropdown with saveAs: "value":
		// - Form.dropList directly receives the string value chosen by the user
		If (Form.dropList#"Please select an option…")
			Form.listResult:=Form.dropList
		Else 
			Form.listResult:=""
		End if
End case
