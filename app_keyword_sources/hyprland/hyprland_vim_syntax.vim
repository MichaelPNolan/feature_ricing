" vim_data/syntax/hyprland.vim
" Vim syntax file for Hyprland configuration

if exists("b:current_syntax")
  finish
endif

" Comments
syntax region hyprlandComment start="#" skip="\\$" end="$" contains=@Spell transparent

" Keywords/Commands
syntax keyword hyprlandCommand set bindsym exec_always exec-once exec source bar gaps client. workspace movetoworkspace
syntax keyword hyprlandModifier Mod1 Mod4 Shift CTRL Alt SUPER
syntax keyword hyprlandKey Up Down Left Right Return Escape Tab Delete Insert Home End Page_Up Page_Down F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12

" Variables (e.g., $mod)
syntax match hyprlandVariable "\\$\h\\w*"

" Strings (double-quoted)
syntax region hyprlandString start=/'/ skip=/\\'/ end=/'/

" Numbers
syntax match hyprlandNumber "\\<\\d\\+\>"

" Highlight groups
hi def link hyprlandComment Comment
hi def link hyprlandCommand Statement
hi def link hyprlandModifier Type
hi def link hyprlandKey Identifier
hi def link hyprlandVariable Special
hi def link hyprlandString String
hi def link hyprlandNumber Number

let b:current_syntax = "hyprland"

