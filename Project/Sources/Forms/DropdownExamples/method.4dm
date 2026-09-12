#declare()
// Form method for DropdownExamples

Case of 
	: (Form event code=On Load)
		// --------------------------------------------------------------------
		// 1. OBJECT-BASED DROPDOWN (Collection in Object)
		// --------------------------------------------------------------------
		// The object requires:
		// - values: a Collection of scalar values (0-based)
		// - index: -1 means no selection (currentValue is displayed as placeholder)
		// - currentValue: initial placeholder string
		Form.dropObject:=New object
		Form.dropObject.values:=New collection(\
			"Option 1: Project Plan"; \
			"Option 2: Architecture Review"; \
			"Option 3: UI Implementation"; \
			"Option 4: Quality Assurance"; \
			"Option 5: Production Deployment")
		Form.dropObject.index:=-1
		Form.dropObject.currentValue:="Please select an option…"
		Form.objectResult:=""
		
		// --------------------------------------------------------------------
		// 2. ARRAY-BASED DROPDOWN
		// --------------------------------------------------------------------
		// The 4D array is 1-based:
		// - asArrayChoices{1} .. {5} are the choices
		// - asArrayChoices{0} holds the "no selection" placeholder text
		// - Assigning 0 to the array variable selects element 0 (placeholder)
		ARRAY TEXT(asArrayChoices; 5)
		asArrayChoices{1}:="Option 1: Project Plan"
		asArrayChoices{2}:="Option 2: Architecture Review"
		asArrayChoices{3}:="Option 3: UI Implementation"
		asArrayChoices{4}:="Option 4: Quality Assurance"
		asArrayChoices{5}:="Option 5: Production Deployment"
		asArrayChoices{0}:="Please select an option…"
		asArrayChoices:=0
		Form.arrayResult:=""
		
		// --------------------------------------------------------------------
		// 3. CHOICE LIST DROPDOWN (saveAs: value)
		// --------------------------------------------------------------------
		// With saveAs set to "value", the dataSource holds the selected item value directly.
		// Setting the variable at On Load initializes the placeholder / prompt.
		Form.dropList:="Please select an option…"
		Form.listResult:=""
End case
