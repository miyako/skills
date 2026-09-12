// Form method for Dropdown Examples form

Case of
	: (Form event=On Load)
		// Initialize object-based dropdown
		Form.dropObject:=New object
		Form.dropObject.values:=New collection("Apple"; "Banana"; "Cherry"; "Orange"; "Strawberry")
		Form.dropObject.index:=-1  // -1 means "no selection"
		Form.dropObject.currentValue:="Please select an option…"
		
		// Initialize array-based dropdown
		ARRAY TEXT(asColor; 5)
		asColor{1}:="Red"
		asColor{2}:="Green"
		asColor{3}:="Blue"
		asColor{4}:="Yellow"
		asColor{5}:="Purple"
		asColor{0}:="Please select a color…"
		asColor:=0  // Set to 0 (no selection)
		
		// Initialize choice list dropdown
		Form.dropChoice:="Please select a color…"
		
		// Initialize result labels
		OBJECT SET TEXT("objectResultLabel"; "")
		OBJECT SET TEXT("arrayResultLabel"; "")
		OBJECT SET TEXT("choiceResultLabel"; "")

	: (Form event=On Unload)
		// Clean up array when form closes
		CLEAR ARRAY(asColor)
End case
