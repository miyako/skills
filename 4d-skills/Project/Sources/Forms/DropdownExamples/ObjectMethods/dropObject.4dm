// Object method for object-based dropdown

Case of
	: (OBJECT Get name(Object current)="dropObject")
		If (Form event=On Data Change)
			// Get the selected value
			If (Form.dropObject.index=-1)
				// No selection was made
				OBJECT SET TEXT("objectResultLabel"; "No selection")
			Else
				// Display the selected fruit
				var $selectedValue : Text
				$selectedValue:=Form.dropObject.currentValue
				OBJECT SET TEXT("objectResultLabel"; "Selected: "+$selectedValue)
			End if
		End if
End case
