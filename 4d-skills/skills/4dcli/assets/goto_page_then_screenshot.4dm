//%attributes = {"invisible":true}
// Called via CALL FORM. Navigates to the requested page,
// then chains another CALL FORM for the screenshot.
// The page rendering completes at the end of THIS execution cycle,
// so the screenshot in the NEXT cycle captures the correct page.

// With DIALOG(...; *) the first CALL FORM can execute before the form's
// first display cycle, and a FORM GOTO PAGE issued that early is silently
// ignored (the form then displays page 1). Requeue once so the navigation
// lands on a displayed form.
If (Form.__hop=Null)
	Form.__hop:=1
	CALL FORM(Current form window; Formula(goto_page_then_screenshot))
	return 
End if 

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
