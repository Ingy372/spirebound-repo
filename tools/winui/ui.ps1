# Small helper for automated client testing on Windows: screenshot of the game window, click, type, key.
# Usage (dot-source):  . tools\winui\ui.ps1 ; Focus ; Click 100 200 ; Keys "text" ; Shot out.png
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W { 
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
 [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] public static extern void mouse_event(int f,int x,int y,int d,int e);
[DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x,int y,int cx,int cy,uint f);
 public struct RECT { public int L,T,R,B; } }
"@
[W]::SetProcessDPIAware() | Out-Null
function GameProc { Get-Process otclient -ErrorAction SilentlyContinue | ? { $_.MainWindowHandle -ne 0 } | select -First 1 }
function Rect { $r = New-Object W+RECT; [W]::GetWindowRect((GameProc).MainWindowHandle, [ref]$r) | Out-Null; $r }
function Focus { $h=(GameProc).MainWindowHandle; [W]::ShowWindow($h, 9) | Out-Null; [W]::SetWindowPos($h, [IntPtr](-1), 40, 40, 1400, 900, 0x40) | Out-Null; [W]::SetForegroundWindow($h) | Out-Null; Start-Sleep -Milliseconds 600 }
function Click($x, $y) { $r = Rect; [W]::SetCursorPos($r.L + $x, $r.T + $y) | Out-Null; Start-Sleep -Milliseconds 150; [W]::mouse_event(2,0,0,0,0); [W]::mouse_event(4,0,0,0,0); Start-Sleep -Milliseconds 300 }
function Keys($t) { [Windows.Forms.SendKeys]::SendWait($t); Start-Sleep -Milliseconds 300 }
function Shot($f) { $r = Rect; $w=$r.R-$r.L; $h=$r.B-$r.T; $bm = New-Object Drawing.Bitmap $w,$h; $g=[Drawing.Graphics]::FromImage($bm); $g.CopyFromScreen($r.L,$r.T,0,0,$bm.Size); $bm.Save($f); "$w x $h" }
