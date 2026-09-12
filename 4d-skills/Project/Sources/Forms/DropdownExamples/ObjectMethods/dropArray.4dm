// Object method for array-based dropdown

Case of
	: (OBJECT Get name(Object current)="dropArray")
		If (Form event=On Data Change)
			// Get the selected value using array idiom
			If (asColor=0)
				// No selection was made
				OBJECT SET TEXT("arrayResultLabel"; "No selection")
			Else
				// asColor{asColor} gives us the currently selected value
				var $selectedValue : Text
				$selectedValue:=asColor{asColor}
				OBJECT SET TEXT("arrayResultLabel"; "Selected: "+$selectedValue)
			End if
		End if
End case
