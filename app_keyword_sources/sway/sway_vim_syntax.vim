" vim_data/syntax/sway.vim
" Vim syntax file for Sway configuration

if exists("b:current_syntax")
  finish
endif

" Comments
syntax region swayComment start="#" skip="\\$" end="$" contains=@Spell transparent

" Keywords/Commands
syntax keyword swayCommand set bindsym bindcode exec workspace output mode for_window floating_modifier default_border gaps bar font include input client.focused client.focused_inactive client.unfocused client.urgent client.placeholder client.background
syntax keyword swayModifier Mod1 Mod4 Shift Control Alt Super
syntax keyword swayKey Return Tab Escape BackSpace Delete Insert Home End PageUp PageDown Up Down Left Right F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12
syntax keyword swayBoolean on off yes no enabled disabled

" Variables (e.g., $mod)
syntax match swayVariable "$\\h\\w*"

" Strings (double-quoted)
syntax region swayString start="/"" skip="\\\"" end="/""

" Numbers
syntax match swayNumber "\\<\\d\\+\>"

" Highlight groups
hi def link swayComment Comment
hi def link swayCommand Statement
hi def link swayModifier Type
hi def link swayKey Identifier
hi def link swayBoolean Boolean
hi def link swayVariable Special
hi def link swayString String
hi def link swayNumber Number

let b:current_syntax = "sway"

