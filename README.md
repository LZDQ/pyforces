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

Since this tool is designed for speed only, some features of [xalanq/cf-tool](https://github.com/xalanq/cf-tool) are removed. Please don't request for any features that are not speed-sensitive and already supported by Codeforces webpage itself or other GUI tools like [CCH](https://github.com/CodeforcesContestHelper/CCHv2).

## Platforms

Developed on Linux, but tests are still in progress. Will test on Windows and Mac later.

If you encounter any issues on Windows or Mac, please read the error message and stacktrace first. If you believe this is a bug or unwanted feature, submit an issue with the stacktrace, or use `pyforces --log-level=debug` to get even more verbose output.

## Installation

`pip install git+https://github.com/LZDQ/pyforces.git`

See [FAQ](#FAQ) if you encounter any problems.

## Usage

* `pyforces config` to login and configure your tool. Firefox is needed for login.
* `pyforces race 2092` to start the contest `2092`.
* `pyforces test` in the problem folder, like `~/pyforces/contest/2092/a`, to test your solution against parsed sample testcases.
* `pyforces submit` in the problem folder, to submit your solution. Currently the CLI doesn't output anything on success, you need to refresh the submission page.
* `pyforces parse` in the problem folder to parse sample testcases.
* `pyforces gen` in the problem folder to generate a file from template.

## How to login

First, you need to login to codeforces in Firefox. Support for other browsers are not added yet, or you can manually put all your headers in `~/.pyforces/headers.txt`.

Then, follow this video to configure your HTTP header:


https://github.com/user-attachments/assets/cac3b09a-1809-4de3-bc9a-53d8d9df8c05

Note: in the video the root name has been configured to `cf` not default `pyforces`.

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

### Is it violating bot detection?

Since login requries you to actually login in Firefox first, this doesn't violate bot detection. For more details, see [here](https://codeforces.com/blog/entry/134322).

## TODO

- [ ] Colorful CLI and tab completion for path
- [ ] Template substitution
- [ ] Submission status tracking
- [ ] Floating-point errors in tests
- [ ] Special Judge and Interactive problems
- [ ] (Neo)vim config example
- [ ] Sphinx documentation
- [ ] Support for AI automatic problem solving as a library

