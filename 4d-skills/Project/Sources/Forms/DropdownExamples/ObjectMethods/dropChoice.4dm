// Object method for choice list dropdown

Case of
	: (OBJECT Get name(Object current)="dropChoice")
		If (Form event=On Data Change)
			// Get the selected value directly
			If (Form.dropChoice="Please select a color…")
				// Still showing placeholder
				OBJECT SET TEXT("choiceResultLabel"; "No selection")
			Else
				// Display the selected color
				OBJECT SET TEXT("choiceResultLabel"; "Selected: "+Form.dropChoice)
			End if
		End if
End case
