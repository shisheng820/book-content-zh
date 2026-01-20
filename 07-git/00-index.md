{% set section_title = "Git" %}
{% set section_subtitle = "创建并分享私有仓库。" %}
{% set page_title = "了解如何使用 Keybase Git" %}
{% set page_description = "使用 Keybase 为个人和团队提供加密、经过身份验证和私有的 Git 仓库。了解更多。" %}

# Keybase Git

Keybase 支持免费、加密、经过身份验证和私有的 [Git](https://git-scm.com/) 仓库。

你可以在这些仓库中放置任何类型的内容，但它们对于个人私有仓库或团队间共享的秘密内容特别有用。

这些仓库是 *真正的* Git 仓库，但你可以在 Keybase 应用中查看它们。它们是 100% 私有、加密和经过验证的。你可以确信它们是安全的，不仅可以防止窥探，还可以防止可能试图更改你代码的恶意人员。（他们怎么敢？！）

#### 你的所有数据都会自动加密和验证。

在底层，Git 支持 [远程助手](https://git-scm.com/docs/gitremote-helpers)。这允许 Git 本身与本地文件系统以外的数据存储进行交互。Keybase 创建了一个 [开源远程助手](https://github.com/keybase/client/tree/master/go/kbfs/kbfsgit/) 来促进这种交互，通过你的本地 Keybase 应用将你仓库中的数据保持在你的控制之下。

这意味着你的数据是加密的——甚至 Keybase 也无法看到里面的内容（包括它的名称、文件名、你的其他配置——什么都看不到）。这也意味着每当你或你的团队成员向这些仓库之一推送或拉取（或克隆）数据时，所有写入都由你的私钥验证，而私钥永远不会离开你的设备。你可以确信你的团队成员确实推送了 Git 历史记录日志中所说的更改。

#### 没有覆盖或冲突。

在 Keybase 中使用 Git 仓库（或通过命令行）比仅仅在 Keybase [文件](/files) 中托管你的本地 Git 仓库要好。有了原生 Git 仓库，Keybase 知道在必要时锁定你的仓库。这可以防止两个人（或同一个人控制的两台设备）覆盖彼此的更改并导致冲突。

## 创建仓库

导航到 Git 并选择 `新建仓库` (New Repository)。你可以将其设为你的个人仓库或与团队共享。

一旦你创建了一个仓库（或选择了一个现有的仓库），会有一个 `克隆:` (Clone:) 字段显示你将用于访问此仓库的地址。它看起来像这样：

```
keybase://team/Mary_Poppins_Bag/secrets
```

在命令行上，或在你选择的 Git UI 工具中（例如 [GitHub Desktop](https://desktop.github.com/) 也可以），使用此地址来克隆仓库。从那里，你可以像使用任何其他 Git 仓库一样使用它：

```
git clone keybase://team/faculty_secrets/secrets
Cloning into 'secrets'...
Initializing Keybase... done.
Syncing with Keybase... done.
Counting: 77.01 KB... done.
Cryptographic cloning: (100.00%) 77.01/77.01 KB... done.
```

你还可以通过将私有 Keybase 仓库添加为额外的远程仓库，将其与现有仓库一起使用：

```
git remote add private keybase://team/faculty_secrets/secrets
git pull private master
Initializing Keybase... done.
Syncing with Keybase... done.
From keybase://team/faculty_secrets/secrets
 * branch            master     -> FETCH_HEAD
 * [new branch]      master     -> private/master
Already up to date.
```

所有这些也可以通过命令行界面进行管理。假设你想管理一个私有的 `config` 仓库：

```
keybase git create config
Repo created! You can clone it with:
  git clone keybase://private/scoates/config
Or add it as a remote to an existing repo with:
  git remote add origin keybase://private/scoates/config
```
