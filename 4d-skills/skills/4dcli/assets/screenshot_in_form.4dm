//%attributes = {"invisible":true}
// Screenshot of a window that belongs to ANOTHER process (MODIFY SELECTION, MODIFY RECORD, a
// DIALOG opened by the app itself). Run it inside that window's process with CALL FORM:
//   CALL FORM($window; "screenshot_in_form"; "/PACKAGE/shots/out.png")
// FORM SCREENSHOT($window; $picture) called from a different process on such a window was
// observed to hang. Calling FORM SCREENSHOT($picture) inside the form's own process works.
// Find $window by title or process name, not with Frontmost window: with --skip-onstartup
// the Design Explorer is the frontmost window.
#DECLARE($path : Text)

var $screenshot : Picture
FORM SCREENSHOT($screenshot)

var $file : 4D.File
$file:=File($path)
$file.parent.create()
WRITE PICTURE FILE($file.platformPath; $screenshot)
