# pyforces

[![Github release](https://img.shields.io/github/release/LZDQ/pyforces)](https://github.com/LZDQ/pyforces/releases)
![platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
[![license](https://img.shields.io/badge/license-WTFPL-%23373737.svg)](https://raw.githubusercontent.com/LZDQ/pyforces/main/LICENSE)

[中文](README-zh.md)

Yet another command-line interface tool for [Codeforces](https://codeforces.com) designed for (neo)vim competitors. Rebirth of [xalanq/cf-tool](https://github.com/xalanq/cf-tool).

## Why another CLI tool?

Codeforces added bot detection recently, and AFAIK all the existing CLI tools are blocked. [ref1](https://codeforces.com/blog/entry/96091) [ref2](https://github.com/woshiluo/cf-tool/issues/5)

## Features

* Parse sample testcases.
* Test your solution with parsed testcases.
* Submit code.
* Generate code from templates.
* Start a contest (parse sample testcases for all problems and optionally gen template).
* Gym support.

Feature requests and PRs are welcomed.

Since this tool is designed for **speed** only, some features of [xalanq/cf-tool](https://github.com/xalanq/cf-tool) are removed. If you want some other features like contest standing, please use Codeforces webpage itself or other GUI tools like [CCH](https://github.com/CodeforcesContestHelper/CCHv2).

## Installation

`pip install pyforces-cli`

See [FAQ](#FAQ) if you encounter any problems.

## Usage

* `pyforces config` to login and configure your tool. Firefox is needed for login. See [How to login](#How-to-login) below.
* `pyforces race 2092` to start the contest `2092`. The contest id is in the URL, for example [2092](https://codeforces.com/contest/2092/). Same for gym (numbers >= 100000 are gyms).
* `pyforces test` in the problem directory, like `~/cf/contest/2092/a`, to test your solution against parsed sample testcases. Note that you need to first compile it yourself, and the executable filename is derived from the cpp filename. If the executable file's modified time is earlier than the source file's, you will see a warning.
* `pyforces submit` in the problem folder, to submit your solution.
* `pyforces parse` in the problem folder to parse sample testcases.
* `pyforces gen` in the problem folder to generate a file from template.

## How to login

First, you need to login to codeforces in Firefox. If you don't use Firefox, either use it once or find a way (like a plugin?) to configure your `~/.pyforces/headers.txt` (If you don't know what is `~`, try searching `home directory`).

Then, follow this video to configure your HTTP header:


https://github.com/user-attachments/assets/cac3b09a-1809-4de3-bc9a-53d8d9df8c05

(Note: in the video the root name has been configured to `cf` not default `pyforces`.)

If the method in the video fails, check [FAQ](#FAQ) first. If that doesn't help, you can manually paste your headers to `~/.pyforces/headers.txt`. If you use Firefox, directly pasting the "(Copy All)" to `~/.pyforces/headers.txt` is okay. If you use other browsers, check [this](example/headers.txt) example `headers.txt`.

**IMPORTANT**: It is recommended to paste your headers before each contest. I'm not sure how long they last but it works for a single contest's session.

## Vim config

The intended use of this tool is to bind some keys to speed up testing and submitting. Here is an example neovim keybinding configuration (vim users need to replace `term` by `!`):

```vim
" test, and submit if test passed
nnoremap <F5> :w<CR>:term pyforces test -f % && pyforces submit -f %<CR>
" test
nnoremap <F6> :term pyforces test -f %<CR>
" submit
nnoremap <F7> :w<CR>:term pyforces submit -f %<CR>
```

Change the keys to your choices as you wish.

Also, if you don't want to mess up keybindings of other buffers or projects, consider adding a filetype check and buffer prefix:

```vim
" test, and submit if test passed
au FileType cpp nnoremap <buffer><F5> :w<CR>:term pyforces test -f % && pyforces submit -f %<CR>
" test
au FileType cpp nnoremap <buffer><F6> :term pyforces test -f %<CR>
" submit
au FileType cpp nnoremap <buffer><F7> :w<CR>:term pyforces submit -f %<CR>

" python support, with program_type_id=70 (PyPy 3.10)
au FileType python nnoremap <buffer><F5> :w<CR>:term pyforces test -f % && pyforces submit --file=% --program-type-id=70<CR>
au FileType python nnoremap <buffer><F6> :w<CR>:term pyforces test -f %<CR>
au FileType python nnoremap <buffer><F7> :w<CR>:term pyforces submit -f % --program-type-id=70<CR>
```

## FAQ

#### pip install failed

```
error: externally-managed-environment

× This environment is externally managed
```

It is recommended to install this tool in a virtual environment. I'd suggest astral-uv in 2025.

If you don't want to use a virtual environment, adding `--break-system-packages` at the end of `pip install` should work.

#### Command 'pyforces' not found

If `pyforces` command isn't available, you can use `python -m pyforces` to invoke pyforces.

#### Terminal stuck when pasting headers

Change the buffer size of your terminal, and make sure you press enter after pasting it if it seems to stuck. You can modify the buffer size in your terminal's settings.

#### Is it violating bot detection?

Since login requries you to actually login in Firefox first, this doesn't violate bot detection. For more details, see [here](https://codeforces.com/blog/entry/134322).

#### Cannot track last submission

This is a known bug and cannot be reproduced stably. However the submission always works, so you can still manually track the status.

#### Other issues

If you encounter any issues, please read the error message and stacktrace first. If you believe this is a bug or unwanted feature, submit an issue with the stacktrace, or use `pyforces --log-level=debug <subcommand> [sub-arguments]` to get even more verbose output.

## TODO

- [x] Bug fix: some problems have multiple sub-problems like g1, g2
- [ ] Bug fix: cannot track last submission
- [ ] Floating-point errors in tests
- [x] (Neo)vim config example
- [ ] Fix "ensure logged in" (some old cookies still work on the host url)
- [x] Use websocket to receive status updates
- [ ] ~~Test on Windows & Mac~~ Write tests(?)
- [ ] Provide more test outputs
- [x] Better CLI ~~and color~~
- [x] Arguments for time and memory limit
- [x] Arguments for user customization (submit with custom URL and problem id)
- [x] Log to `~/.pyforces/logs/` to track bugs
- [ ] Log requests and responses
- [ ] Also store images if `parse_problem_md`

## Not Planned

* Login with username and password (too complicated firewall)
* SPJ, interactive problem and communication. Most users don't write SPJ or interactor during contest, and after contest it is better to write custom test scripts for these problems.
* Export as a python SDK for other libraries. CLI is the only way to use this tool.
