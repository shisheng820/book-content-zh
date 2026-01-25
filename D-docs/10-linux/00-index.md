# Linux 用户指南
欢迎阅读 Keybase Linux 用户指南！

本指南适用于从 Linux 初学者到专家再到发行版软件包维护者的所有人。它涵盖了 Linux 上 Keybase 独有的一些主题。如果你有任何 [反馈或问题](#feedback-and-questions)，请告诉我们！

 1. [快速入门](#quickstart)
 1. [示例命令](#example-commands)
 1. [每夜构建版 (Nightly Builds)](#nightly-builds)
 1. [自动启动](#autostart)
 1. [`run_keybase`](#runkeybase)
 1. [systemd 和运行无界面 Keybase](#systemd-and-running-headless-keybase)
 1. [示例：systemd 定时器上的每日 KBFS 备份](#example-daily-kbfs-backup-on-a-systemd-timer)
 1. [配置 KBFS](#configuring-kbfs)
 1. [无 Root 权限安装 Keybase](#installing-keybase-without-root-privileges)
 1. [致软件包维护者](#for-package-maintainers)
 1. [反馈和问题](#feedback-and-questions)

## 快速入门
Keybase 官方仅支持 Ubuntu、Debian、Fedora、CentOS 和 Arch，但也有适用于其他系统的其他软件包。

请注意，我们维护的软件包是获取最新功能和安全更新的最快方式，社区软件包可能存在我们要控制之外的打包问题，并且以下说明可能无法开箱即用。

无论你如何安装，你都应该通过运行软件包管理器的更新命令来自动获取更新。

<table class="padded-table">
    <tr>
        <th>发行版</th>
        <th>URL</th>
        <th>维护者</th>
    </tr>
    <tr>
        <td>源代码</td>
        <td><a href="https://github.com/keybase/client">github.com/keybase/client</a></td>
        <td>Keybase</td>
    </tr>
    <tr>
        <td>Ubuntu, Debian, 等</td>
        <td><a href="https://keybase.io/docs/the_app/install_linux#ubuntu-debian-and-friends">Keybase 安装页面</a></td>
        <td>Keybase</td>
    </tr>
    <tr>
        <td>Fedora, CentOS, 等</td>
        <td><a href="https://keybase.io/docs/the_app/install_linux#fedora-red-hat">Keybase 安装页面</a></td>
        <td>Keybase</td>
    </tr>
    <tr>
        <td>Arch AUR</td>
        <td>`keybase-bin` [<a href="https://aur.archlinux.org/packages/keybase-bin/">链接</a>], [<a href="https://keybase.io/docs/the_app/install_linux#arch-linux">Keybase 安装页面</a>]</td>
        <td>Keybase</td>
    </tr>
    <tr>
        <td>Arch Community</td>
        <td>
            `keybase` [<a href="https://www.archlinux.org/packages/community/x86_64/keybase/">链接</a>],
            `kbfs` [<a href="https://www.archlinux.org/packages/community/x86_64/kbfs/">链接</a>],
            `keybase-gui` [<a href="https://www.archlinux.org/packages/community/x86_64/keybase-gui/">链接</a>]
        </td>
        <td>社区</td>
    </tr>
    <tr>
        <td>Slackware</td>
        <td>
            `kbfs` [<a href="https://www.slackbuilds.org/repository/14.2/system/kbfs/">链接</a>]
            (同时也提供 keybase 和 gui)
        </td>
        <td>社区</td>
    </tr>
    <tr>
        <td>FreeBSD</td>
        <td>
            `keybase` [<a href="https://www.freshports.org/security/keybase/">链接</a>],
            `kbfs` [<a href="https://www.freshports.org/security/kbfs">链接</a>],
            `kbfsd` [<a href="https://www.freshports.org/security/kbfsd">链接</a>],
        </td>
        <td>社区</td>
    </tr>
    <tr>
        <td>Nix</td>
        <td>
            `keybase` [<a href="https://github.com/NixOS/nixpkgs/blob/release-19.03/pkgs/tools/security/keybase/default.nix) [(选项)](https://nixos.org/nixos/options.html#services.keybase">链接</a>],
            `kbfs` [<a href="https://github.com/NixOS/nixpkgs/blob/release-19.03/pkgs/tools/security/kbfs/default.nix) [(选项)](https://nixos.org/nixos/options.html#services.kbfs">链接</a>],
            `keybase-gui` [<a href="https://github.com/NixOS/nixpkgs/blob/release-19.03/pkgs/tools/security/keybase/gui.nix">链接</a>],
        </td>
        <td>社区</td>
    </tr>
    <tr>
        <td>Gentoo</td>
        <td>
            `keybase` [<a href="https://packages.gentoo.org/packages/app-crypt/keybase">链接</a>],
            `kbfs` [<a href="https://packages.gentoo.org/packages/app-crypt/kbfs">链接</a>]
        </td>
        <td>社区</td>
    </tr>
</table>

如果你通过官方软件包安装了 Keybase，你应该有可用的 `run_keybase` 脚本，它会启动 Keybase、KBFS 和 GUI。

```bash
run_keybase
...
success!
```

既然 Keybase 正在运行，你将能够创建一个帐户或登录 GUI。登录后，你可以在 GUI 中制作证明、与朋友聊天、浏览你的 KBFS 文件。

## 示例命令
以下内容并非 Linux 特有，但展示了许多 Keybase 的功能。

```bash
keybase signup # 创建一个账户
keybase id # 打印你的用户名和证明
keybase prove twitter # 证明你的 twitter 身份
keybase prove -l # 列出可用的证明类型
keybase id {some-keybase-username} # 检查另一个用户的证明
keybase chat send {some-keybase-username} -m "Hey! I'm on Keybase now!" # 发送加密消息

# 查看此 github 用户是否在 Keybase 上
keybase id {some-github-username}@github

# 发送（加密）消息给 twitter 用户，*即使他们尚未加入 Keybase*
# （当他们加入时，他们会收到消息）
keybase chat send {some-reddit-username}@reddit -m "Hey! I'm on Keybase now!"

# 为另一个 keybase 用户加密文件或消息，以便通过不安全的聊天渠道发送
keybase encrypt {some-keybase-username} -m "hello, world"
BEGIN KEYBASE SALTPACK ENCRYPTED MESSAGE. kigG6zVjgVFCFLm GxarUYJUY9RGEoH ... e6lZF0EDl3VFSI4 jE0rHiCLJGYpSwk l1ohzskP1Myn9lz . END KEYBASE SALTPACK ENCRYPTED MESSAGE.

# 启动带有纸质密钥的“一次性”临时设备，例如，
# 用于在 Docker 容器中登录 Keybase
keybase oneshot --help

keybase help # 查看所有可用命令
```

随着 KBFS 的运行，你将能够向神奇的 `/keybase` 目录添加文件。此目录中的所有内容都在 *你的机器上* 加密，并与你的所有 [设备](https://keybase.io/download) 同步。没有其他人，包括 Keybase，可以访问你的文件，除非你选择公开它们或与其他用户共享它们。更多信息可在 [理解 KBFS](https://keybase.io/docs/kbfs/understanding_kbfs) 中找到。

```bash
# 添加一个公共文件供 Keybase 上的任何人查看
echo "hello, world" > /keybase/public/{your-username}/hello.txt

# 添加一个仅为你自己加密的私有文件
cp ~/documents/taxes.pdf /keybase/private/{your-username}/taxes.pdf

# 添加一个仅为你自己和某个网站的所有者加密的私有文件，
# *即使他们尚未加入 keybase*（当他们加入并证明他们拥有该网站时，他们将获得它）
cp ~/documents/proposal.pdf /keybase/private/{your-username},example.com@https/proposal.pdf

# 添加一个在一组人之间私密共享的文件
cp ~/documents/resume.pdf /keybase/private/{your-username},{some-keybase-username}/resume.pdf

# 添加一个私密共享给 Keybase 团队的文件
mkdir /keybase/team/{your-team-name}/devops/backups/
mv ~/backups/database.tar.gz /keybase/team/{your-team-name}/devops/backups/database.tar.gz

# 创建一个在你的设备之间同步的私有加密 git 存储库
# 另请参阅：https://keybase.io/blog/encrypted-git-for-everyone
keybase git create my-project

# 在没有挂载的情况下与 KBFS 交互
# 例如，在可能不提供 FUSE 的系统（如 ChromiumOS）中很有用
keybase fs ls /keybase/team/
```

如果你使用的软件包不提供 keybase 重定向器，`/keybase` 可能不存在。在这种情况下，你的文件夹位于 `keybase config get -b mountdir` 给出的位置（[稍后会详细介绍](#configuring-kbfs)）。

如果你正在寻找可以交谈的人，请前往我们的 [热门团队页面](https://keybase.io/popular-teams) 并请求从 GUI 内加入公共团队（或使用 `keybase team request-access`）。特别是 `keybasefriends`，是开始讨论 Keybase 一般性问题的好地方。有关团队的更多信息，请参阅 [这里](https://keybase.io/blog/introducing-keybase-teams) 和 [这里](https://keybase.io/blog/new-team-features)。

就是这样！在应用程序和命令行中还有更多功能可以尝试。

如果你只想使用 Keybase，则无需深入了解，但以下部分详细介绍了高级主题，供希望更多地了解和控制 Keybase 在其系统上运行方式的用户使用。

## 每夜构建版 (Nightly Builds)
我们现在提供 `.deb`、`.rpm` 和 Arch 每夜构建版！

标准免责声明：这些不是正式发布版本，可能会导致意外崩溃和不稳定。请谨慎使用。

<table class="padded-table">
    <tr>
        <th>格式</th>
        <th>64位</th>
        <th>32位</th>
    </tr>
    <tr>
        <td>元数据</td>
        <td colspan=2><a href="https://prerelease.keybase.io/nightly/update-linux-prod.json">update-linux-prod.json</a></td>
    </tr>
    <tr>
        <td>`.deb`</td>
        <td><a href="https://prerelease.keybase.io/nightly/keybase_amd64.deb">keybase_amd64.deb</a> (<a href="https://prerelease.keybase.io/nightly/keybase_amd64.deb.sig">签名</a>)</td>
        <td><a href="https://prerelease.keybase.io/nightly/keybase_i386.deb">keybase_i386.deb</a> (<a href="https://prerelease.keybase.io/nightly/keybase_i386.deb.sig">签名</a>)</td>
    </tr>
    <tr>
        <td>`.rpm`</td>
        <td><a href="https://prerelease.keybase.io/nightly/keybase_amd64.rpm">keybase_amd64.rpm</a> (<a href="https://prerelease.keybase.io/nightly/keybase_amd64.rpm.sig">签名</a>)</td>
        <td><a href="https://prerelease.keybase.io/nightly/keybase_i386.rpm">keybase_i386.rpm</a> (<a href="https://prerelease.keybase.io/nightly/keybase_i386.rpm.sig">签名</a>)</td>
    <tr>
        <td>Arch Linux AUR</td>
        <td colspan=2><a href="https://aur.archlinux.org/packages/keybase-git/">keybase-git</a>; 支持 64 位、32 位和 ARM</td>
    </tr>
</table>

请注意，我们（尚未）提供 `.deb` 和 `.rpm` 每夜构建版的软件包存储库：你需要手动运行 `dpkg -i` 或 `rpm -i` 来安装和更新到下一个每夜构建版，而不是使用 `apt-get` 或 `yum`。但是，如果你在 Arch 上，你可以通过重新安装 `keybase-git` 来更新。

要启用实验性 GUI 功能，请创建一个调试文件：
```bash
$ cat ~/.cache/keybase/keybase.app.debug # 或者在你的 $XDG_CACHE_HOME/keybase 中
{ "featureFlagsOverride": "admin" }
```
当然，这不会给你任何额外的访问权限，并且其中一些功能可能也是服务器控制的，因此它们可能无法正常工作或根本无法工作。

如果你发现这些每夜构建版的任何错误或问题，请 [报告它们](#feedback-and-questions)，我们将尽最大努力尽快修复！同时在问题标题中指定 `[NIGHTLY]`。

## 自动启动
如果你使用的是像 KDE 或 Gnome 这样的图形桌面环境，Keybase 会安装一个自动启动桌面文件到 `~/.config/autostart/keybase_autostart.desktop`。如果你不想要这种行为，可以在桌面环境设置中禁用它，或者运行

```bash
keybase ctl autostart --disable
```

如果你在无界面系统上，你可能想使用 systemd 单元。如果你使用像 i3wm 这样的窗口管理器，你可以让它在启动时执行 `run_keybase`。如果你希望 Keybase 启动但不希望 GUI 最大化，请将命令更改为 `run_keybase -a`。你将能够从系统托盘中的图标打开 GUI。

当使用 `systemctl` 启动 GUI 时，你必须将 `KEYBASE_AUTOSTART=1` 导入环境，以便 GUI 启动但保持在后台。单元文件会在之后立即取消设置此变量，因此随后的调用将启动它并最大化，除非该变量已再次设置：

```bash
systemctl --user set-environment KEYBASE_AUTOSTART=1
```

## `run_keybase`
`run_keybase` 接受更多用于控制 Keybase 的选项。
```bash
$ run_keybase -h
启动 Keybase 服务、KBFS 和 GUI。
如果服务已经在运行，它们将被重启。

选项也可以通过将相关环境变量设置为 1 来控制
  -a  启动后保持 GUI 最小化在系统托盘 (env KEYBASE_AUTOSTART=1)
  -f  不启动 KBFS (env KEYBASE_NO_KBFS=1)
  -g  不启动 gui (env KEYBASE_NO_GUI=1)
  -h  打印此帮助文本
  -k  关闭所有 Keybase 服务 (env KEYBASE_KILL=1)
```

当执行 `run_keybase` 时，最多启动四个后台进程：
`keybase`、`kbfsfuse`、`Keybase` 和 `keybase-redirector`。

- `keybase` 是支持所有其他 Keybase 操作的主要服务，同时也提供命令行工具。如果你愿意，你可以单独使用 `keybase`。

- `kbfsfuse` 允许你使用 KBFS 和 KBFS git，并依赖于 `keybase`。

- `Keybase` 是 GUI 应用程序，依赖于 `keybase` 和 `kbfsfuse`。

- `keybase-redirector` 提供神奇的 `/keybase` KBFS 目录，但使用 KBFS 不需要它。

`run_keybase` 尝试将其进程作为 systemd 用户管理器服务运行（如果你的系统支持，如 Arch、Ubuntu、Debian），但如果不能，它会回退到启动常规后台进程。

你可以通过以下命令查看你是否通过 systemd 运行
```bash
systemctl --user status keybase keybase.gui kbfs keybase-redirector
# （如果你没有那个命令，你没有使用 systemd）
```

如果你不想启动后台进程，你可以尝试
```bash
keybase --standalone {rest-of-command}
```
但此模式不支持所有 Keybase 功能（例如，聊天），并且可能会更慢。

## systemd 和运行无界面 Keybase
如果你在服务器上运行 Keybase，你可能希望比 `run_keybase` 提供的更精细地控制 Keybase。在这种情况下，你可以直接配置 systemd 单元，而无需使用 `run_keybase`。

请注意，`keybase` *不能* 以 root 身份运行，必须以用户身份运行。
因此，它在特定用户的系统用户管理器下运行，而不是全局系统管理器。

首先，执行 systemd 单元所需的一些基本环境设置。
```bash
keybase ctl init
```
除其他外，这将转发一些环境变量到 systemd 单元。如果它们发生变化，你需要再次运行此命令（或 `run_keybase`）以刷新它们。因为 systemd 单元不会自动转发用户环境，所以这 *不能* 在 `ExecStartPre` 指令中自动运行。但是，你可以选择在 shell 配置文件或 rc 文件中登录时运行它。具体来说，这会在 `~/.config/keybase/keybase.autogen.env`（或在你的 `$XDG_CONFIG_HOME` 中）创建一个文件。可以通过写入同一目录中的 `keybase.env` 或使用 `Environment` 指令创建 systemctl drop-in 配置来覆盖环境变量。

（可选）启用单元在系统引导时自动启动。你可以选择其中的一部分，但请记住 KBFS 依赖于 Keybase（如果尚未启动，它将启动它）。
```bash
systemctl --user enable keybase.service
systemctl --user enable kbfs.service
systemctl --user enable keybase-redirector.service
```

（可选）允许 Keybase 即使在你注销后也能继续运行。如果你通过 SSH 连接到服务器，你可以这样做，以便 Keybase 和 KBFS 在你的会话结束后继续工作。
```bash
loginctl enable-linger
```

接下来，启动 Keybase 服务。
```bash
systemctl --user start keybase.service
systemctl --user start kbfs.service
systemctl --user start keybase-redirector.service
```

现在，你应该能够使用 KBFS 并从命令行使用 Keybase。
```bash
keybase id
```

如果你遇到问题，可以重启服务
```bash
systemctl --user restart keybase kbfs keybase-redirector
```

请注意，GUI 也作为 systemd 单元运行。
```bash
systemctl --user start keybase.gui
```
要使其工作，你必须在环境文件中配置你的 `$DISPLAY`，如果你按照上面的指示配置了环境文件或在会话中执行了 `run_keybase`，这应该是已经做好的。
当然，除非你配置了 X 转发，否则它在 ssh 会话中不起作用。

如果你需要编辑 systemd 单元，请运行
```
systemctl --user edit {unit-name}
```
你将能够在 [drop-in 目录](https://www.freedesktop.org/software/systemd/man/systemd.unit.html) 中单独覆盖指令。
如果你在升级后遇到问题，可能需要合并上游单元文件的更改，所以仅作为最后手段这样做。

最后，如果你不希望 `run_keybase` 使用 systemd，你可以导出 `KEYBASE_SYSTEMD=0`，它将回退到启动后台进程。
如果它检测到你的系统不支持 systemd 用户管理器，它会自动执行此操作。

## 示例：systemd 定时器上的每日 KBFS 备份
既然你了解了基础知识，让我们看看如何在服务器上运行 Keybase 进行每日 KBFS 备份（再次强调，加密并自动同步到你的所有其他 Keybase 设备，甚至是一组用户或团队！）。

除了 systemd 定时器，你还可以选择编写 cron 任务。只需确保它作为你的用户 cron 任务运行，如果不使用 systemd，请先执行 `run_keybase` 以便 Keybase 服务在你启动脚本之前启动。

请记住，你的 KBFS 配额（由 `keybase fs quota` 给出）目前是 250GB。

按照上一节中的说明进行操作。现在，创建一个执行一次备份的 systemd 单元。它可能看起来像这样：
```bash
$ cat ~/.config/systemd/user/kbfs-backup.service
[Unit]
Requires=keybase.service kbfs.service keybase-redirector.service
Description=make a backup of my photos

[Service]
ExecStart=%h/scripts/run-kbfs-backup

$ cat ~/scripts/run-kbfs-backup
#!/bin/bash
set -euo pipefail

function date {
    date --utc +%Y%m%d_%H%M%SZ
}

keybase_username={your-keybase-username}
archive="backup-$(date).tar.gz"
tar -czvf "$HOME/$archive" "$HOME/photos"
mkdir -p "/keybase/private/$keybase_username/backups/"
mv "$HOME/$archive" "/keybase/private/$keybase_username/backups/$archive"

$ chmod +x ~/scripts/run-kbfs-backup
```

当然，你可以使用像 `rsync` 这样的工具来改进这个简单的例子。

最后，创建一个定时器文件。它可能看起来像这样：

```bash
$ cat ~/.config/systemd/user/kbfs-backup.timer
[Unit]
Description=run kbfs-backup.service every weekday at noon

[Timer]
OnCalendar=Mon-Fri 12:00
Persistent=true

[Install]
WantedBy=timers.target

$ systemctl --user enable --now kbfs-backup.timer
```

完成了！你可以检查定时器的日志，并使用 `journalctl --user` 检查故障。

要手动运行一次备份，只需执行

```bash
systemctl --user start kbfs-backup.timer
```

## 配置 KBFS
有关 KBFS 如何工作的更多信息，你可以阅读 [理解 KBFS](https://keybase.io/docs/kbfs/understanding_kbfs)。

在 Linux 上，`kbfsfuse` 将 FUSE 文件系统挂载到运行 Keybase 的用户拥有的目录。然后，`keybase-redirector` 挂载在 `/keybase`，并根据请求 KBFS 数据的用户显示 `/keybase` 的不同版本。

如果配置了 `$XDG_RUNTIME_USER`（通常由 systemd 配置），此挂载目录位于 `$XDG_RUNTIME_USER/keybase/kbfs/`，否则位于 `~/.config/keybase/kbfs`。此外，你的软件包维护者可能已将其预配置为其他位置。

要查看当前的挂载目录，请运行
```bash
keybase config get -b mountdir
```

你可以通过运行以下命令更改它
```bash
keybase config set mountdir ~/another-mount-dir
run_keybase # 或重启 systemd 服务
```
确保在重启服务之前没有使用 KBFS。
另外，请注意不要将挂载目录设置在主目录中的某个位置，以防像 `find` 或 `grep` 这样的工具意外爬取 KBFS。

最后，你可能想禁用重定向器。这是一个管理员命令：它需要 root 权限。

你可以这样做
```bash
sudo keybase --use-root-config-file ctl redirector --disable
```
或者重新打开它
```bash
sudo keybase --use-root-config-file ctl redirector --enable
```

再次强调，在运行这些命令之前，请确保未使用 KBFS。
启用的重定向器归 root 所有，并设置了 setuid 位。当你禁用它时，该位被取消设置，用户将无法访问 `/keybase` 或运行重定向器。为了方便，用户可以包含类似以下内容
```bash
export keybase="$(keybase config get --direct --bare mountdir)"
```
在他们的 shell 配置文件或 rc 文件中，以便他们可以访问他们的文件 `$keybase/private/<their-username>` 等。

## 无 Root 权限安装 Keybase
Keybase 仅使用 root 权限使神奇的 `/keybase` 目录可用。

如果你想在没有 root 权限的情况下安装 Keybase，例如，你可以解压 `.deb` 文件并在那里运行二进制文件。如果你将二进制文件放在 `$PATH` 中，你甚至可以将提供的 systemd 单元文件符号链接到你的 `~/.config/systemd/user` 目录，并使用 systemd 用户管理器来管理你的自定义 Keybase 安装。请注意，KBFS 挂载将无法在 `/keybase` 访问，而是在用户可写的挂载目录中访问（参见 <a href="#configuring-kbfs">配置 KBFS</a>）。

或者，你可以选择从源代码构建 Keybase 以完全自定义你的安装，如 <a href="#for-package-maintainers">致软件包维护者</a> 中所述。

## 致软件包维护者
我们要很高兴你有兴趣打包 Keybase！这涉及许多活动部件，因此打包可能会很棘手。

我们的脚本可在 https://github.com/keybase/client/tree/master/packaging/linux 获得。

特别值得注意的是 `post_install.sh` 和 `run_keybase`。你不必打包这些，但你应该包含必要的配置和文档，以便用户能够使用 Keybase。

我们的代码签名指纹在同一目录下的 `code_signing_fingerprint` 中，也可在 [我们的网站](https://keybase.io/docs/server_security/our_code_signing_key) 上找到。

你也可以从 [我们的发布目录](https://prerelease.keybase.io/linux_binaries/deb/index.html) 中的 `.deb` 文件中提取我们自己构建的二进制文件，而不是从源代码构建。你可以选择将 Keybase、KBFS 和 GUI 全部打包在一起或分包打包，但请确保指定了依赖关系。

如果你创建了一个软件包并希望被添加到此页面顶部的列表中，请告诉我们。特别是 SysVinit 和 OpenRC 的 init 脚本可能是其他软件包维护者感兴趣的。

## 反馈和问题
我们的目标是使 Keybase 对从桌面用户到服务器管理员的所有人都灵活易用。

如果你认为你发现了安全问题或错误，请参阅我们的 [错误报告页面](https://keybase.io/docs/bug_reporting)。在提交错误报告时，请从命令行执行 `keybase log send`，以便开发人员可以更快地为你提供帮助。

如果你有功能请求，你可以创建一个 [GitHub issue](https://github.com/keybase/client/issues/new) 或加入 Keybase 上的 keybasefriends 团队并在 `#feature-requests` 频道发帖。或者如果你只需要一般帮助，请在 `#general` 频道发帖。
