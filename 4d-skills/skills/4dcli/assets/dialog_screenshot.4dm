//%attributes = {"invisible":true}
// CLI endpoint: opens a form with DIALOG, takes a runtime screenshot, saves to disk, quits.
// Usage: --startup-method dialog_screenshot --user-param "FormName:Page:/path/to/output.png"
// Requires 4D WITHOUT --headless (headless auto-dismisses DIALOG before screenshot can run).
// Do NOT use tool4d either (no DIALOG support).

var $userParamValue : Text
var $unused : Real
$unused:=Get database parameter(User param value; $userParamValue)

var $params : Collection
$params:=Split string($userParamValue; ":")

If ($params.length<3)
	QUIT 4D
	return 
End if 

var $formName : Text
$formName:=$params[0]

var $formPage : Integer
$formPage:=Num($params[1])
If ($formPage<1)
	$formPage:=1
End if 

var $screenshotPath : Text
$screenshotPath:=$params[2]

var $form : Object
$form:={}
$form.__page:=$formPage
$form.__screenshotPath:=$screenshotPath

var $window : Integer
$window:=Open form window($formName)
DIALOG($formName; $form; *)

CALL FORM($window; Formula(goto_page_then_screenshot))
