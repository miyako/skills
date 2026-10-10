//%attributes = {"invisible":true}
// Called via CALL FORM. Navigates to the requested page,
// then chains another CALL FORM for the screenshot.
// The page rendering completes at the end of THIS execution cycle,
// so the screenshot in the NEXT cycle captures the correct page.

var $page : Integer
$page:=Form.__page
If ($page>1)
	FORM GOTO PAGE($page)
End if 

// Chain: screenshot will run in the next execution cycle,
// after this cycle's page change has been rendered.
var $window : Integer
$window:=Current form window
CALL FORM($window; Formula(screenshot_and_accept))
