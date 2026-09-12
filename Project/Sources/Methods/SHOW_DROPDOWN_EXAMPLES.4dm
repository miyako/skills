#declare()
// Project Method: SHOW_DROPDOWN_EXAMPLES
// Opens the DropdownExamples form dialog

var $win : Integer
$win:=Open form window("DropdownExamples"; Plain form window)
DIALOG("DropdownExamples")
CLOSE WINDOW($win)
