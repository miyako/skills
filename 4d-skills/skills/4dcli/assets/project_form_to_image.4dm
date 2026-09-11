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
var $screenshotPath : Text
$screenshotPath:=$userParams.slice(2).join(":")

If ($screenshotPath="")
	return 
End if 

If ($formPage<1)
	$formPage:=1
End if 

var $file : 4D.File
$file:=File($screenshotPath)
$file.parent.create()

var $width; $height; $pages : Integer
FORM GET PROPERTIES($formName; $width; $height; $pages)

If ($formPage>$pages)
	$formPage:=$pages
End if 

var $screenshot : Picture
Case of 
	: (False)
		FORM LOAD($formName)
		FORM GOTO PAGE($formPage)
		FORM SCREENSHOT($screenshot)
		FORM UNLOAD
	: (True)
		FORM SCREENSHOT($formName; $screenshot; $formPage)
End case 

WRITE PICTURE FILE($file.platformPath; $screenshot)

If (Application info.headless)
	LOG EVENT(Into system standard outputs; $file.path; Information message)
	QUIT 4D
End if 
