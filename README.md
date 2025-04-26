# pyforces

[![Github release](https://img.shields.io/github/release/LZDQ/pyforces)](https://github.com/LZDQ/pyforces/releases)
![platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
[![license](https://img.shields.io/badge/license-WTFPL-%23373737.svg)](https://raw.githubusercontent.com/LZDQ/pyforces/main/LICENSE)

Yet another command-line interface tool for [Codeforces](https://codeforces.com). Rebirth of [xalanq/cf-tool](https://github.com/xalanq/cf-tool).

## Why another CLI tool?

Codeforces added bot detection recently, and AFAIK all the existing CLI tools are blocked. [ref1](https://codeforces.com/blog/entry/96091) [ref2](https://github.com/woshiluo/cf-tool/issues/5)

## Features

* Parse sample testcases.
* Generate code from templates.
* Test your solution with parsed testcases.
* Submit code.
* Start a contest (parse sample testcases for all problems and optionally gen template).

Feature requests and PRs are welcomed.

Since this tool is designed for speed only, some features of [xalanq/cf-tool](https://github.com/xalanq/cf-tool) are removed. Please don't request for any features that are not speed-sensitive or already supported by Codeforces webpage itself or other GUI tools like [CCH](https://github.com/CodeforcesContestHelper/CCHv2).

## Platforms

Developed on Linux, but tests are still in progress. Will test on Windows and Mac later.

If you encounter any issues on Windows or Mac, please read the error message and stacktrace first. If you believe this is a bug or unwanted feature, submit an issue with the stacktrace, or use `pyforces --log-level=debug <subcommand>` to get even more verbose output.

## Installation

`pip install git+https://github.com/LZDQ/pyforces.git`

See [FAQ](#FAQ) if you encounter any problems.

## Usage

* `pyforces config` to login and configure your tool. Firefox is needed for login.
* `pyforces race 2092` to start the contest `2092`.
* `pyforces test` in the problem folder, like `~/pyforces/contest/2092/a`, to test your solution against parsed sample testcases. Exit 0 on success, 1 in most cases and the actual non-zero exit code if Runtime Error.
* `pyforces submit` in the problem folder, to submit your solution. The status will refresh on the terminal with a default polling rate of 10s.
* `pyforces parse` in the problem folder to parse sample testcases.
* `pyforces gen` in the problem folder to generate a file from template.

## Vim config

The intended use of this tool is to bind some keys to speed up testing and submitting. Here is an example (neo)vim keybinding configuration:

```vim
" test, and submit on success
nnoremap <F5> :term pyforces test -f % && pyforces submit -f %<CR>
" test
nnoremap <F6> :term pyforces test -f %<CR>
" submit
nnoremap <F7> :w<CR>:term pyforces submit -f %<CR>
```

Change the keys to your choices as you wish.

Also, if you don't want to mess up keybindings of other buffers or projects, consider adding a filetype check and buffer prefix:

```vim
" test, and submit on success
au FileType cpp nnoremap <buffer><F5> :term pyforces test -f % && pyforces submit -f %<CR>
" test
au FileType cpp nnoremap <buffer><F6> :term pyforces test<CR>
" submit
au FileType cpp nnoremap <buffer><F7> :w<CR>:term pyforces submit -f %<CR>

" python support, with program_type_id=70 (PyPy 3.10)
au FileType python nnoremap <buffer><F5> :term pyforces test -f % && pyforces submit --file=% --program-type-id=70<CR>
au FileType python nnoremap <buffer><F6> :term pyforces test -f %<CR>
au FileType python nnoremap <buffer><F7> :w<CR>:term pyforces submit -f % --program-type-id=70<CR>
```

## How to login

First, you need to login to codeforces in Firefox. If you don't use Firefox, either use it once or manually config your `~/.pyforces/headers.txt`. If you don't know what is `~`, try searching `home directory`.

Then, follow this video to configure your HTTP header:


https://github.com/user-attachments/assets/cac3b09a-1809-4de3-bc9a-53d8d9df8c05

Note: in the video the root name has been configured to `cf` not default `pyforces`.

If the method in the video fails, check [FAQ](#FAQ) first. If that doesn't help, you can manually paste your headers to `~/.pyforces/headers.txt`. If you use Firefox, directly pasting the "(Copy All)" to `~/.pyforces/headers.txt` is okay. If you use other browsers, check [this](example/headers.txt) example `headers.txt`.

You can also re-ensure you are logged in with `pyforces config`.

## FAQ

### pip install failed

```
error: externally-managed-environment

× This environment is externally managed
```

It is recommended to install this tool in a virtual environment managed by miniconda.

If you don't want to use a virtual environment, adding `--break-system-packages` at the end of `pip install` should work.

### Command 'pyforces' not found

If `pyforces` command isn't available, you can use `python -m pyforces` to invoke pyforces.

### Terminal stuck when pasting headers

Change the buffer size of your terminal, and make sure you press enter after pasting it if it seems to stuck. You can modify the buffer size in your terminal's settings.

### Is it violating bot detection?

Since login requries you to actually login in Firefox first, this doesn't violate bot detection. For more details, see [here](https://codeforces.com/blog/entry/134322).

## TODO

- [ ] Floating-point errors in tests
- [ ] Special Judge and Interactive problems
- [x] (Neo)vim config example
- [ ] Sphinx documentation
- [ ] Support for AI automatic problem solving as a library
- [ ] Fix "ensure logged in" (some old cookies still work on the host url)
- [x] Use websocket to receive status updates
- [x] Test on Windows & Mac

