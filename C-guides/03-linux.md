{% set section_title = "Linux 用户指南" %}

# Linux

本指南适用于从 Linux 初学者到专家乃至发行版软件包维护者的所有人。它涵盖了 Linux 上 Keybase 独有的一些主题。如果您有任何[反馈或问题](#feedback-and-questions)，请告诉我们！

## 快速开始 (Quickstart)

Keybase 官方仅支持 Ubuntu, Debian, Fedora, CentOS, 和 Arch，但也存在适用于其他系统的软件包。

请注意，我们维护的软件包是获取最新功能和安全更新的最快方式，社区软件包可能会有我们无法控制的打包问题，并且下面的说明可能无法开箱即用。

无论您如何安装，都应该通过运行包管理器的更新命令来自动获取更新。

{# TODO: table
<table class="padded-table">
    <tr>
        <th>发行版 (Distribution)</th>
        <th>URL</th>
        <th>维护者 (Maintainer)</th>
    </tr>
    <tr>
        <td>源代码 (Source code)</td>
        <td>[github.com/keybase/client](https://github.com/keybase/client)</td>
        <td>Keybase</td>
    </tr>
    <tr>
        <td>Ubuntu, Debian, 等</td>
        <td>[Keybase 安装页面](/docs/the_app/install_linux#ubuntu-debian-and-friends)</td>
        <td>Keybase</td>
    </tr>
    <tr>
        <td>Fedora, CentOS, 等</td>
        <td>[Keybase 安装页面](/docs/the_app/install_linux#fedora-red-hat)</td>
        <td>Keybase</td>
    </tr>
    <tr>
        <td>Arch AUR</td>
        <td>`keybase-bin` [(链接)](https://aur.archlinux.org/packages/keybase-bin/), [Keybase 安装页面](/docs/the_app/install_linux#arch-linux)</td>
        <td>Keybase</td>
    </tr>
    <tr>
        <td>Arch Community</td>
        <td>
            `keybase` [(链接)](https://www.archlinux.org/packages/community/x86_64/keybase/),
            `kbfs` [(链接)](https://www.archlinux.org/packages/community/x86_64/kbfs/),
            `keybase-gui` [(链接)](https://www.archlinux.org/packages/community/x86_64/keybase-gui/)
        </td>
        <td>Community</td>
    </tr>
    <tr>
        <td>Slackware</td>
        <td>
            `kbfs` [(链接)](https://www.slackbuilds.org/repository/14.2/system/kbfs/)
            (同时提供 keybase 和 gui)
        </td>
        <td>Community</td>
    </tr>
    <tr>
        <td>FreeBSD</td>
        <td>
            `keybase` [(链接)](https://www.freshports.org/security/keybase/),
            `kbfs` [(链接)](https://www.freshports.org/security/kbfs/),
            `kbfsd` [(链接)](https://www.freshports.org/security/kbfsd/),
        </td>
        <td>Community</td>
    </tr>
    <tr>
        <td>Nix</td>
        <td>
            `keybase` [(链接)](https://github.com/NixOS/nixpkgs/blob/release-19.03/pkgs/tools/security/keybase/default.nix) [(选项)](https://nixos.org/nixos/options.html#services.keybase),
            `kbfs` [(链接)](https://github.com/NixOS/nixpkgs/blob/release-19.03/pkgs/tools/security/kbfs/default.nix) [(选项)](https://nixos.org/nixos/options.html#services.kbfs),
            `keybase-gui` [(链接)](https://github.com/NixOS/nixpkgs/blob/release-19.03/pkgs/tools/security/keybase/gui.nix),
        </td>
        <td>Community</td>
    </tr>
    <tr>
        <td>Gentoo</td>
        <td>
            `keybase` [(链接)](https://packages.gentoo.org/packages/app-crypt/keybase),
            `kbfs` [(链接)](https://packages.gentoo.org/packages/app-crypt/kbfs)
        </td>
        <td>Community</td>
    </tr>
</table>
#}

如果您是通过官方软件包安装的 Keybase，您应该可以使用 `run_keybase` 脚本，它会启动 Keybase、KBFS 和 GUI。

```bash
run_keybase
...
success!
```

现在 Keybase 正在运行，您可以创建一个账户或登录 GUI。登录后，您可以在 GUI 中进行证明、与朋友聊天、浏览您的 KBFS 文件。

## 示例命令 (Example Commands)

以下命令并非 Linux 特有，但展示了许多 Keybase 的功能。

```bash
keybase signup # 创建一个账户
keybase id # 打印您的用户名和证明
keybase prove twitter # 证明您的 twitter 身份
keybase prove -l # 列出可用的证明类型
keybase id {some-keybase-username} # 检查另一位用户的证明
keybase chat send {some-keybase-username} -m "Hey! I'm on Keybase now!" # 发送一条加密消息

# 查看此 github 用户是否在 Keybase 上
keybase id {some-github-username}@github

# 发送一条 (加密) 消息给一位 twitter 用户，*即使他们尚未加入 Keybase*
# (当他们加入时会收到消息)
keybase chat send {some-reddit-username}@reddit -m "Hey! I'm on Keybase now!"

# 为另一位 keybase 用户加密文件或消息，以便通过不安全的聊天频道发送
keybase encrypt {some-keybase-username} -m "hello, world"
BEGIN KEYBASE SALTPACK ENCRYPTED MESSAGE. kigG6zVjgVFCFLm GxarUYJUY9RGEoH ... e6lZF0EDl3VFSI4 jE0rHiCLJGYpSwk l1ohzskP1Myn9lz . END KEYBASE SALTPACK ENCRYPTED MESSAGE.

# 使用 paperkey 启动一个“一次性”临时设备，例如
# 用于在 Docker 容器中登录 Keybase
keybase oneshot --help

keybase help # 查看所有可用命令
```

随着 KBFS 的运行，您将能够向神奇的 `/keybase` 目录添加文件。此目录中的所有内容都在*您的机器上*加密，并与您的所有[设备](https://keybase.io/download)同步。除非您选择将其公开或与其他用户共享，否则其他人（包括 Keybase）都无法访问您的文件。更多信息请访问 [理解 KBFS](https://keybase.io/docs/kbfs/understanding_kbfs)。

```bash
# 添加一个公开文件，供 Keybase 上的任何人查看
echo "hello, world" > /keybase/public/{your-username}/hello.txt

# 添加一个仅为您自己加密的私有文件
cp ~/documents/taxes.pdf /keybase/private/{your-username}/taxes.pdf

# 添加一个仅为您自己和某个网站所有者加密的私有文件，
# *即使他们尚未加入 keybase* (当他们加入并证明他们拥有该网站时，他们将获得该文件)
cp ~/documents/proposal.pdf /keybase/private/{your-username},example.com@https/proposal.pdf

# 添加一个在一群人之间私密共享的文件
cp ~/documents/resume.pdf /keybase/private/{your-username},{some-keybase-username}/resume.pdf

# 添加一个私密共享给 Keybase 团队的文件
mkdir /keybase/team/{your-team-name}/devops/backups/
mv ~/backups/database.tar.gz /keybase/team/{your-team-name}/devops/backups/database.tar.gz

# 创建一个在您的设备之间同步的私有加密 git 仓库
# 另见: https://keybase.io/blog/encrypted-git-for-everyone
keybase git create my-project

# 在没有挂载的情况下与 KBFS 交互
# 例如，在像 ChromiumOS 这样可能不提供 FUSE 的系统中很有用
keybase fs ls /keybase/team/
```

如果您使用的软件包不提供 keybase 重定向器，`/keybase` 可能不存在。在这种情况下，您的文件夹位于 `keybase config get -b mountdir` 给出的位置（[稍后详细介绍](#configuring-kbfs)）。

如果您正在寻找可以交谈的人，请前往我们的 [热门团队页面](https://keybase.io/popular-teams) 并在 GUI 中请求加入公共团队（或使用 `keybase team request-access`）。特别是 `keybasefriends`，它是开始一般性讨论和询问有关 Keybase 问题的好地方。有关团队的更多信息，请参阅 [这里](https://keybase.io/blog/introducing-keybase-teams) 和 [这里](https://keybase.io/blog/new-team-features)。

就是这样！在应用程序和命令行中还有更多功能可以尝试。

如果您只想使用 Keybase，则无需继续往下看，但以下部分详细介绍了高级主题，供希望更多地了解和控制 Keybase 在其系统上运行方式的用户参考。

## Nightly 构建版本 (Nightly Builds)

我们现在提供 `.deb`, `.rpm`, 和 Arch nightly 构建版本！

标准免责声明：这些不是正式版本，可能会导致意外崩溃和不稳定。使用时请小心。

{# TODO: table
<table class="padded-table">
    <tr>
        <th>格式 (Format)</th>
        <th>64位 (64-bit)</th>
        <th>32位 (32-bit)</th>
    </tr>
    <tr>
        <td>元数据 (Metadata)</td>
        <td colspan=2>[update-linux-prod.json](https://prerelease.keybase.io/nightly/update-linux-prod.json)</td>
    </tr>
    <tr>
        <td>`.deb`</td>
        <td>[keybase_amd64.deb](https://prerelease.keybase.io/nightly/keybase_amd64.deb) ([签名](https://prerelease.keybase.io/nightly/keybase_amd64.deb.sig))</td>
        <td>[keybase_i386.deb](https://prerelease.keybase.io/nightly/keybase_i386.deb) ([签名](https://prerelease.keybase.io/nightly/keybase_i386.deb.sig))</td>
    </tr>
    <tr>
        <td>`.rpm`</td>
        <td>[keybase_amd64.rpm](https://prerelease.keybase.io/nightly/keybase_amd64.rpm) ([签名](https://prerelease.keybase.io/nightly/keybase_amd64.rpm.sig))</td>
        <td>[keybase_i386.rpm](https://prerelease.keybase.io/nightly/keybase_i386.rpm) ([签名](https://prerelease.keybase.io/nightly/keybase_i386.rpm.sig))</td>
    <tr>
        <td>Arch Linux AUR</td>
        <td colspan=2>[keybase-git](https://aur.archlinux.org/packages/keybase-git/); 支持 64位, 32位, 和 ARM</td>
    </tr>
</table>
#}

请注意，我们（尚）未提供 `.deb` 和 `.rpm` nightly 版本的软件包仓库：您需要手动执行 `dpkg -i` 或 `rpm -i` 来安装和更新到下一个 nightly 版本，而不是使用 `apt-get` 或 `yum`。但是，如果您在 Arch 上，只需重新安装 `keybase-git` 即可更新。

要启用实验性 GUI 功能，请创建一个 debug 文件：

```bash
$ cat ~/.cache/keybase/keybase.app.debug # 或者在您的 $XDG_CACHE_HOME/keybase
{ "featureFlagsOverride": "admin" }
```

当然，这不会给您任何额外的访问权限，并且其中一些功能可能还需要服务器端授权，因此它们可能无法正常工作或根本无法工作。

如果您发现这些 nightly 版本有任何错误或问题，请[报告它们](#feedback-and-questions)，我们会尽力尽快修复！请在问题标题中注明 `[NIGHTLY]`。

## 自动启动 (Autostart)

如果您使用的是图形桌面环境（如 KDE 或 Gnome），Keybase 会在 `~/.config/autostart/keybase_autostart.desktop` 中安装一个自动启动桌面文件。如果您不想要此行为，可以在桌面环境设置中禁用它，或运行：

```bash
keybase ctl autostart --disable
```

如果您在无界面系统上，您可能希望使用 systemd 单元。如果您使用的是像 i3wm 这样的窗口管理器，您可以在启动时执行 `run_keybase`。如果您希望 Keybase 启动但不希望 GUI 最大化，请将命令更改为 `run_keybase -a`。您将能够从系统托盘中的图标打开 GUI。

当使用 `systemctl` 启动 GUI 时，您必须将 `KEYBASE_AUTOSTART=1` 导入环境，以便 GUI 启动但保持在后台。单元文件会在此之后立即取消设置此变量，因此后续调用将启动并最大化，除非再次设置该变量：

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
  -a  启动后将 GUI 最小化到系统托盘 (env KEYBASE_AUTOSTART=1)
  -f  不启动 KBFS (env KEYBASE_NO_KBFS=1)
  -g  不启动 gui (env KEYBASE_NO_GUI=1)
  -h  打印此帮助文本
  -k  关闭所有 Keybase 服务 (env KEYBASE_KILL=1)
```

当 `run_keybase` 执行时，最多会启动四个后台进程：`keybase`, `kbfsfuse`, `Keybase`, 和 `keybase-redirector`。

- `keybase` 是驱动所有其他 Keybase 操作的主服务，同时也提供命令行工具。如果您愿意，可以单独使用 `keybase`。
- `kbfsfuse` 允许您使用 KBFS 和 KBFS git，它依赖于 `keybase`。
- `Keybase` 是 GUI 应用程序，依赖于 `keybase` 和 `kbfsfuse`。
- `keybase-redirector` 提供神奇的 `/keybase` KBFS 目录，但使用 KBFS 并非必须。

如果您的系统支持 systemd 用户管理器（Arch, Ubuntu, Debian），`run_keybase` 会尝试作为 systemd 用户管理器服务运行其进程，如果不支持，则回退到启动常规后台进程。

您可以通过以下命令查看是否正在通过 systemd 运行：

```bash
systemctl --user status keybase keybase.gui kbfs keybase-redirector
# (如果您没有该命令，则说明您没有使用 systemd)
```

如果您不想启动后台进程，可以尝试：

```bash
keybase --standalone {rest-of-command}
```

但并非所有 Keybase 功能（例如聊天）都支持此模式，并且可能会更慢。

## systemd 和运行无界面 Keybase

如果您在服务器上运行 Keybase，您可能希望对 Keybase 进行比 `run_keybase` 提供的更细粒度的控制。在这种情况下，您可以直接配置 systemd 单元，而无需使用 `run_keybase`。

请注意，`keybase` *不能*作为 root 运行，必须作为用户运行。因此，它在特定用户的 systemd 用户管理器下运行，而不是全局系统管理器。

首先，执行一些 systemd 单元所需的基本环境设置。

```bash
keybase ctl init
```

除其他事项外，这会将一些环境变量转发给 systemd 单元。如果它们发生变化，您需要再次运行此命令（或 `run_keybase`）以刷新它们。由于 systemd 单元不会自动转发用户环境，因此*不能*在 `ExecStartPre` 指令中自动运行此命令。但是，您可以选择在 shell 配置文件或 rc 文件中登录时运行它。具体来说，这会在 `~/.config/keybase/keybase.autogen.env`（或您的 `$XDG_CONFIG_HOME`）中创建一个文件。可以通过写入同一目录中的 `keybase.env` 或使用 `Environment` 指令创建 systemctl drop-in 配置来覆盖环境变量。

（可选）启用单元以在系统启动时自动启动。您可以选择其中一部分，但请记住 KBFS 依赖于 Keybase（如果尚未启动，它将启动它）。

```bash
systemctl --user enable keybase.service
systemctl --user enable kbfs.service
systemctl --user enable keybase-redirector.service
```

（可选）允许 Keybase 即使在您注销后也继续运行。如果您已通过 SSH 连接到服务器，您可以这样做，以便 Keybase 和 KBFS 在您的会话结束后继续工作。

```bash
loginctl enable-linger
```

接下来，启动 Keybase 服务。

```bash
systemctl --user start keybase.service
systemctl --user start kbfs.service
systemctl --user start keybase-redirector.service
```

现在，您应该能够从命令行使用 KBFS 和 Keybase。

```bash
keybase id
```

如果遇到问题，可以使用以下命令重启服务：

```bash
systemctl --user restart keybase kbfs keybase-redirector
```

请注意，GUI 也作为一个 systemd 单元运行。

```bash
systemctl --user start keybase.gui
```

要使其工作，您必须在 environmentfile 中配置 `$DISPLAY`，如果您按照上述说明配置了 environmentfile 或在会话中执行了 `run_keybase`，则应该已经是这种情况。当然，除非您配置了 X 转发，否则它在 ssh 会话中将无法工作。

如果您需要编辑 systemd 单元，请运行

```
systemctl --user edit {unit-name}
```

您将能够在 [drop-in 目录](https://www.freedesktop.org/software/systemd/man/systemd.unit.html) 中单独覆盖指令。如果您在升级后遇到问题，可能需要合并上游单元文件的更改，因此请仅将其作为最后的手段。

最后，如果您不希望 `run_keybase` 使用 systemd，可以导出 `KEYBASE_SYSTEMD=0`，它将回退到启动后台进程。如果它检测到您的系统不支持 systemd 用户管理器，它会自动执行此操作。

## 示例：systemd 定时器上的每日 KBFS 备份

现在您已了解基础知识，让我们看看如何在服务器上运行 Keybase 并每日备份到 KBFS（同样，加密并自动同步到您的所有其他 Keybase 设备，甚至是一组用户或团队！）。

除了 systemd 定时器，您也可以选择编写 cronjob。只需确保它作为您的用户 cronjob 运行，如果不使用 systemd，请先执行 `run_keybase`，以便 Keybase 服务在启动脚本之前启动。

请记住，您的 KBFS 配额（由 `keybase fs quota` 给出的）目前为 250GB。

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

当然，您可以使用 `rsync` 等工具改进这个简单的示例。

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

完成了！您可以检查定时器的日志，并使用 `journalctl --user` 检查故障。

要手动运行一次备份，只需执行：

```bash
systemctl --user start kbfs-backup.timer
```

## 配置 KBFS (Configuring KBFS)

有关 KBFS 工作原理的更多信息，请阅读 [理解 KBFS](https://keybase.io/docs/kbfs/understanding_kbfs)。

在 Linux 上，`kbfsfuse` 将 FUSE 文件系统挂载到运行 Keybase 的用户拥有的目录。然后，`keybase-redirector` 挂载在 `/keybase`，并根据请求 KBFS 数据的用户显示 `/keybase` 的不同版本。

如果配置了 `$XDG_RUNTIME_USER`（通常由 systemd 配置），此挂载目录位于 `$XDG_RUNTIME_USER/keybase/kbfs/`，否则位于 `~/.config/keybase/kbfs`。此外，您的软件包维护者可能已将其预配置为其他位置。

要查看当前的挂载目录，请运行

```bash
keybase config get -b mountdir
```

您可以通过运行以下命令更改它：

```bash
keybase config set mountdir ~/another-mount-dir
run_keybase # 或重启 systemd 服务
```

在重启服务之前，请确保没有任何东西在使用 KBFS。另外，请注意不要将挂载目录设置在主目录中，以免像 `find` 或 `grep` 这样的工具意外爬取 KBFS。

最后，您可能希望禁用重定向器。这是一个管理员命令：它需要 root 权限。

您可以通过以下命令执行此操作：

```bash
sudo keybase --use-root-config-file ctl redirector --disable
```

或者通过以下命令重新打开它：

```bash
sudo keybase --use-root-config-file ctl redirector --enable
```

同样，在运行这些命令之前，请确保未使用 KBFS。启用的重定向器归 root 所有并设置了 setuid 位。当您禁用它时，该位被取消设置，用户将无法访问 `/keybase` 或运行重定向器。为了方便起见，用户可以包含类似以下内容

```bash
export keybase="$(keybase config get --direct --bare mountdir)"
```

在他们的 shell 配置文件或 rc 文件中，以便他们可以通过 `$keybase/private/<their-username>` 等访问他们的文件。

## 在没有 Root 权限的情况下安装 Keybase

Keybase 仅在使神奇的 `/keybase` 目录可用时使用 root 权限。

如果您想在没有 root 权限的情况下安装 Keybase，例如，您可以解压 `.deb` 文件并从那里运行二进制文件。如果您将二进制文件放在 `$PATH` 中，您甚至可以将提供的 systemd 单元文件符号链接到您的 `~/.config/systemd/user` 目录，并使用 systemd 用户管理器来管理您的自定义 Keybase 安装。请注意，KBFS 挂载将无法在 `/keybase` 访问，而是在用户可写的挂载目录访问（请参阅 [配置 KBFS](#configuring-kbfs)）。

或者，您可以选择从源代码构建 Keybase 以完全自定义您的安装，如 [对于软件包维护者](#for-package-maintainers) 中所述。

## 对于软件包维护者 (For Package Maintainers)

很高兴您有兴趣打包 Keybase！这涉及很多活动部件，因此打包可能会很棘手。

我们的脚本位于 https://github.com/keybase/client/tree/master/packaging/linux。

特别值得注意的是 `post_install.sh` 和 `run_keybase`。您不必打包这些，但您应该包含必要的配置和文档，以便用户能够使用 Keybase。

我们的代码签名指纹位于同一目录下的 `code_signing_fingerprint`，也可在 [我们的网站](https://keybase.io/docs/server_security/our_code_signing_key) 上找到。

您还可以从 [我们的发布目录](https://prerelease.keybase.io/linux_binaries/deb/index.html) 中的 `.deb` 文件中提取我们要构建的二进制文件，而不是从源代码构建。您可以选择将 Keybase、KBFS 和 GUI 全部打包在一起或分打包，但请确保指定了依赖关系。

如果您创建了一个软件包并希望被添加到本页顶部的列表中，请告诉我们。特别是 SysVinit 和 OpenRC 的 init 脚本可能会引起其他软件包维护者的兴趣。

## 反馈和问题 (Feedback and Questions)

我们的目标是使 Keybase 灵活，供从桌面用户到服务器管理员的所有人使用。

如果您认为发现了安全问题或错误，请参阅我们的 [错误报告页面](https://keybase.io/docs/bug_reporting)。在提交错误报告时，请从命令行执行 `keybase log send`，以便开发人员可以更快地为您提供帮助。

如果您有功能请求，可以创建一个 [GitHub issue](https://github.com/keybase/client/issues/new) 或加入 Keybase 上的 keybasefriends 团队并在 `#feature-requests` 频道发帖。或者如果您只需要一般帮助，请在 `#general` 频道发帖。
