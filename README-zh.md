# pyforces

[![Github release](https://img.shields.io/github/release/LZDQ/pyforces)](https://github.com/LZDQ/pyforces/releases)
![platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
[![license](https://img.shields.io/badge/license-WTFPL-%23373737.svg)](https://raw.githubusercontent.com/LZDQ/pyforces/main/LICENSE)

[English](README.md)

为 (neo)vim 用户设计的 [Codeforces](https://codeforces.com) 命令行工具，新的 [xalanq/cf-tool](https://github.com/xalanq/cf-tool)。

注意：该文档可能不包含最新变化，请尽量阅读英文版。

## 为什么需要另一个命令行工具？

Codeforces 最近增加了机器人检测，所有现有的纯命令行工具都被屏蔽。[参考1](https://codeforces.com/blog/entry/96091) [参考2](https://github.com/woshiluo/cf-tool/issues/5)

## 功能

* 解析样本测试用例。
* 使用解析的测试用例测试你的解决方案。
* 提交代码。
* 根据模板生成代码。
* 开始一场比赛（解析所有问题的样本测试用例，并可选生成模板）。

欢迎提出功能请求和提交 PR。

由于此工具专为速度设计，[xalanq/cf-tool](https://github.com/xalanq/cf-tool) 的一些功能已被移除。请勿请求非速度敏感的功能或 Codeforces 网页本身或其他 GUI 工具（如 [CCH](https://github.com/CodeforcesContestHelper/CCHv2)）已支持的功能。

## 平台

在 Linux 上开发，经过 Linux、Mac 和 Windows 测试。

如果在 Windows 或 Mac 上遇到问题，请先阅读错误信息和堆栈跟踪。如果认为这是 bug 或不需要的功能，请提交带有堆栈跟踪的问题，或使用 `pyforces --log-level=debug <子命令> [子参数]` 获取更详细的输出。

## 安装

`pip install git+https://github.com/LZDQ/pyforces.git`

如果遇到问题，请参阅 [FAQ](#FAQ)。

## 使用方法

* `pyforces config` 用于登录和配置工具。登录需要 Firefox 浏览器。
* `pyforces race 2092` 开始比赛 `2092`。
* 在题目文件夹（如 `~/pyforces/contest/2092/a`）中运行 `pyforces test`，使用样例测试你的程序。注意你需要先自行编译，并确保可执行文件名与你的源文件名（去掉 cpp 后缀）一致。
* 在题目文件夹中运行 `pyforces submit`，提交代码。
* 在题目文件夹中运行 `pyforces parse`，爬取样例。
* 在题目文件夹中运行 `pyforces gen`，根据模板生成文件。

## Vim 配置

此工具的用途是绑定一些快捷键以加速测试和提交。以下是 neovim 样例配置（vim 用户需要将 `term` 替换成 `!`）：

```vim
" 测试，如果成功则提交
nnoremap <F5> :w<CR>:term pyforces test -f % && pyforces submit -f %<CR>
" 测试
nnoremap <F6> :term pyforces test -f %<CR>
" 提交
nnoremap <F7> :w<CR>:term pyforces submit -f %<CR>
```

可根据需要更改键绑定。

如果不想干扰其他缓冲区或项目的键绑定，可考虑添加文件类型检查和缓冲区前缀：

```vim
" 测试，成功后提交
au FileType cpp nnoremap <buffer><F5> :w<CR>:term pyforces test -f % && pyforces submit -f %<CR>
" 测试
au FileType cpp nnoremap <buffer><F6> :term pyforces test<CR>
" 提交
au FileType cpp nnoremap <buffer><F7> :w<CR>:term pyforces submit -f %<CR>

" 支持 Python，program_type_id=70 (PyPy 3.10)
au FileType python nnoremap <buffer><F5> :w<CR>:term pyforces test -f % && pyforces submit --file=% --program-type-id=70<CR>
au FileType python nnoremap <buffer><F6> :w<CR>:term pyforces test -f %<CR>
au FileType python nnoremap <buffer><F7> :w<CR>:term pyforces submit -f % --program-type-id=70<CR>
```

## 如何登录

首先，你需要在 Firefox 中登录 Codeforces。如果不使用 Firefox，可临时使用一次或手动配置 `~/.pyforces/headers.txt`（如果你不知道 `~` 是什么，请搜索“家目录”）。

然后，参考以下视频配置 HTTP 请求头：

https://github.com/user-attachments/assets/cac3b09a-1809-4de3-bc9a-53d8d9df8c05

注：视频中根目录名已配置为 `cf`，而非默认的 `pyforces`。

如果视频中的方法失败，请先查看 [FAQ](#FAQ)。如果仍无法解决，可手动将你的头信息粘贴到 `~/.pyforces/headers.txt`。如果使用 Firefox，直接将 “(Copy All)” 粘贴到 `~/.pyforces/headers.txt` 即可。如果使用其他浏览器，请参考 [此示例](example/headers.txt) 的 `headers.txt`。

注：配置中的 “ensure logged in” 选项实际上并不能保证你已登录。

**强烈建议**在每次比赛前都重新复制一次 HTTP 请求头至 pyforces。

## FAQ

### pip 安装失败

```
error: externally-managed-environment

× This environment is externally managed
```

建议在 miniconda 管理的虚拟环境中安装此工具。

如果不想使用虚拟环境，可在 `pip install` 后添加 `--break-system-packages`。

### 找不到 'pyforces' 命令

如果 `pyforces` 命令不可用，可使用 `python -m pyforces` 调用 pyforces。

### 粘贴头信息时终端卡住

更改终端的缓冲区大小，并确保粘贴后按回车键。如果仍卡住，可在终端设置中修改缓冲区大小。

### 是否违反机器人检测？

由于登录需要先在 Firefox 中实际登录，此工具不违反机器人检测。更多详情请见 [此处](https://codeforces.com/blog/entry/134322)。
