// Reset button method

Case of
	: (OBJECT Get name(Object current)="resetButton")
		If (Form event=On Clicked)
			// Reset object-based dropdown
			Form.dropObject.index:=-1
			Form.dropObject.currentValue:="Please select an option…"
			OBJECT SET TEXT("objectResultLabel"; "")
			
			// Reset array-based dropdown
			asColor:=0
			OBJECT SET TEXT("arrayResultLabel"; "")
			
			// Reset choice list dropdown
			Form.dropChoice:="Please select a color…"
			OBJECT SET TEXT("choiceResultLabel"; "")
		End if
End case
