//%attributes = {"invisible":true}
// CLI endpoint: like dialog_screenshot, but with a UI language and a form-data factory.
// Usage: --startup-method dialog_screenshot_with_data
//        --user-param "FormName:Page:lang:factory:/path/to/output.png"
// lang    : "" keeps the default language, otherwise SET DATABASE LOCALIZATION(lang) before DIALOG.
// factory : "" for {} as form data, otherwise a project method #DECLARE($formName : Text) : Object
//           that returns the form data, e.g. cs.MyFormClass.new(...) for forms with a formClass.
// Chains goto_page_then_screenshot -> screenshot_and_accept (install all three).
// Requires 4D WITHOUT --headless.

var $userParamValue : Text
var $unused : Real
$unused:=Get database parameter(User param value; $userParamValue)

var $params : Collection
$params:=Split string($userParamValue; ":")

If ($params.length<5)
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

If ($params[2]#"")
	SET DATABASE LOCALIZATION($params[2])
End if 

var $form : Object
If ($params[3]#"")
	EXECUTE METHOD($params[3]; $form; $formName)
End if 
If ($form=Null)
	$form:={}
End if 

$form.__page:=$formPage
$form.__screenshotPath:=$params.slice(4).join(":")

var $window : Integer
$window:=Open form window($formName)
DIALOG($formName; $form; *)

CALL FORM($window; Formula(goto_page_then_screenshot))
