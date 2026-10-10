//%attributes = {"invisible":true}
var $userParamValue : Text
var $paramValue : Integer
$paramValue:=Get database parameter(User param value; $userParamValue)

var $userParams : Collection
$userParams:=Split string($userParamValue; ":")

If ($userParams.length<3)
	return 
End if 

var $formName : Text
$formName:=$userParams[0]
var $formPage : Integer
$formPage:=Num($userParams[1])
var $formObjectPath : Text
$formObjectPath:=$userParams.slice(2).join(":")

If ($formObjectPath="")
	return 
End if 

If ($formPage<1)
	$formPage:=1
End if 

var $file : 4D.File
$file:=File($formObjectPath)
$file.parent.create()

var $width; $height; $pages : Integer
FORM GET PROPERTIES($formName; $width; $height; $pages)

If ($formPage>$pages)
	$formPage:=$pages
End if 

var $form : Object
$form:={}

var $window : Integer
$window:=Open form window($formName)
DIALOG($formName; $form; *)
CALL FORM($window; Formula(ACCEPT))

$file.setText(JSON Stringify($form; *))

If (Application info.headless)
	LOG EVENT(Into system standard outputs; $file.path; Information message)
End if 

QUIT 4D
