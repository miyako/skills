//%attributes = {"invisible":true}
// Called via CALL FORM inside a DIALOG context.
// Takes a screenshot, saves to disk, then accepts and quits.

var $screenshotPath : Text
$screenshotPath:=Form.__screenshotPath

If ($screenshotPath#"")
	var $screenshot : Picture
	FORM SCREENSHOT($screenshot)
	
	var $file : 4D.File
	$file:=File($screenshotPath)
	$file.parent.create()
	WRITE PICTURE FILE($file.platformPath; $screenshot)
End if 

ACCEPT
QUIT 4D
