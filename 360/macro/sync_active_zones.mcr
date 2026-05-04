#!MC 1410
#
# This macro registers a new Quick Macro Panel function
# which will set the active zones (field maps) to be the
# same across all frames. This may have problems if there
# are non-2D/3D frames in the layout
#
$!MacroFunction
  Name = "Sync active zones"
  ShowInMacroPanel = True

  $!EXTENDEDCOMMAND
    COMMANDPROCESSORID = "extendmcr"
    Command = 'query.activezones ActiveZones'
  $!Loop |NumFrames|
    $!FrameControl ActivateNext
    $!ActiveFieldMaps = [|ActiveZones|]
  $!EndLoop

$!EndMacroFunction
