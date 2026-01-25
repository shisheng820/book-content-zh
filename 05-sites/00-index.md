{% set section_title = "站点" %}
{% set section_subtitle = "构建并托管一个简单的网站。" %}
{% set nav_title = "站点" %}
{% set page_title = "了解如何使用 Keybase 站点" %}
{% set page_description = "使用 Keybase 文件构建并托管一个简单、安全的网站。使用自定义域名或通过 Git 发布。了解更多。" %}

# Keybase 站点

[Keybase 文件](/files) 的一个好处是，你可以轻松地在你的公共文件夹中构建并托管一个简单的网站。

## 入门指南

要了解它是如何工作的，请在文档中输入任何内容。你可以从任何你想写的内容开始，但在互联网上尝试新事物时，按照传统通常会写这个：

```
# Hello, world!
```

这个例子使用了 [Markdown](https://daringfireball.net/projects/markdown/basics) 格式（`#` 表示标题）。你也可以使用 [HTML](https://www.w3schools.com/html/)。

如果你使用 Markdown，请将你的文档命名为 `index.md`。如果你使用 HTML，请将你的文档命名为 `index.html`。

将这个 index 文件拖入你的公共文件夹。你会立即在你的主页 `https://yourusername.keybase.pub/` 上看到它。

### 添加页面

要添加更多页面：

1. 在你的公共文件夹中创建一个新文件夹。用页面名称命名该文件夹。
2. 添加一个包含你内容的 index 文件（记住，它是公开的）。
3. 重复此步骤——创建一个新文件夹并添加一个新的 index 文件——用于每一个新页面。

![ !Create and organize index files in your public folder to build your site.](/static/img/sites-filestructure.png)

只有 **index 文件**，即标题为 `index.md` 或 `index.html` 的文档，才会显示在你的网站上。

例如，假设你想从你的主页链接到另一个名为 `foo` 的页面。为此，在你的公共文件夹中创建一个名为 `foo` 的文件夹。向 `foo` 文件夹添加一个包含你内容的 index 文件。这个新页面将出现在 `https://yourusername.keybase.pub/foo/`。

### 编辑页面

要编辑页面，打开 index 文件，进行编辑并保存。你的更改将自动更新到你的网站上。

### 了解更多

如果你感兴趣，可以在 [Keybase.pub](https://keybase.pub/) 查看一些示例并搜索其他人的网站。

## 自定义域名

你也可以在 Keybase 站点使用自定义域名。这让你的网站可以显示在你拥有的任何域名上，而不是 `https://{username}.keybase.pub/`。

### 使用 kbpbot

`kbpbot` 是一个 Keybase 机器人，旨在帮助你使用自定义域名发布你的网站。

例如，假设你想在 `myname.com` 发布你的网站。为此：

1. 在你的私有 Keybase 文件夹中，创建一个名为 `yourusername,kbpbot` 的新文件夹。只有你和 `kbpbot` 可以访问、读取和编辑此文件夹中的文件。
2. 在此文件夹内，添加另一个文件夹来存放你的站点内容。我们将其命名为 `my-site`。完整的文件夹名称将是 `/keybase/private/person,kbpbot/my-site`。
3. 将你想要在网站上公开分享的任何其他文件拖入此文件夹。你可以使用 Markdown、HTML、CSS 和图像文件。

### 团队文件夹

任何 `kbpbot` 可以读取的 Keybase 文件夹都可以，所以你也可以使用团队文件夹（例如 `/keybase/team/awesometeam/awesome-site`）并将 `kbpbot` 添加为读者。

### DNS 记录

为了让你的域名/主机名指向 Keybase 服务器，你需要设置一个指向主机名 `kbp.keybaseapi.com` 的 `CNAME` 记录（你也可以使用 `ALIAS` 记录来转发 `A`/`AAAA` 记录）。所以，你会得到类似这样的内容：

```
my-site.example.com. 300 IN CNAME kbp.keybaseapi.com.
```

注意，你不能在根域名（例如 `example.com`）上使用 `CNAME`。一些 DNS 提供商支持将其作为仅针对 `A`/`AAAA` 记录的代理。这有时被称为 `ALIAS`。如果你需要在 Keybase 站点上使用根域名，但你的 DNS 提供商不允许，请尝试切换到其他 DNS 提供商。

除了 DNS 记录外，`kbpbot` 需要知道你想在这个主机名上分享哪个共享文件夹。你需要为 `_keybase_pages` 添加一个 `TXT` 记录作为你的主机名的子域名。在这种情况下，那就是 `_keybase_pages.my-site.example.com`。如果不允许 `_keybase_pages` 前缀，你也可以使用 `_keybasepages.my-site.example.com`。

此记录的内容是前缀 `kbp=`，以及你想要分享的文件夹的完整 Keybase 路径（如上所创建）。对于此示例设置，记录将如下所示：

```
_keybase_pages.my-site.example.com. 300 IN TXT "kbp=/keybase/private/person,kbpbot/my-site"
```

此记录告诉 `kbpbot` 在此文件夹中查找以分享你的文件。

### HTTPS 安全

感谢 [Let’s Encrypt](https://letsencrypt.org/)，`kbpbot` 能够透明地请求并在你的托管域名上安装 HTTPS TLS/SSL 证书，完全免费。

如果你的配置顺利，你的文件夹内容现在将通过安全的 HTTPS 连接共享。

如果你添加了 `/keybase/private/person,kbpbot/my-site/index.html`，该文件将在 `https://my-site.example.com/`（以及 `https://my-site.example.com/index.html`）上可用。

如果你在 `/keybase/private/person,kbpbot/my-site/puppy/gettingbig.jpg` 分享了一张图片，它将在 `https://my-site.example.com/puppy/gettingbig.jpg` 上可用，依此类推。

## Git 发布

你也可以通过 [Git](/git) 而不是 [文件](/files) 来发布你的网站。

你可以创建一个共享的 Keybase Git 仓库并发布它，而不是与 [kbpbot](/sites#使用-kbpbot) 共享一个文件夹。

首先，你需要与 `kbpbot` 在同一个团队中：

1.  在团队中，选择 `创建团队` (Create a team) 并给它一个名字。（我们将这个称为 `gitwithkbpbot`，但它可以是任何名字。）
2.  `添加成员` (Add members) 并邀请 `kbpbot` 作为读者 (Reader)。你也可以将 `kbpbot` 添加到现有团队中。现在你可以创建一个 Git 仓库用于你的新站点。
3.   在 Git 中，选择 `新仓库` (New repository) 和 `新团队仓库` (New team repository)。选择你与 `kbpbot` 共享的团队，并给仓库一个名字。（我们将这个称为 `git-site`。）  
4.  克隆仓库并向其中添加一些内容。推送到 `master`。

Git 的 DNS 配置略有不同。主要的 `CNAME`/`ALIAS` 记录是相同的（指向 `kbp.keybaseapi.com`）。但是 `TXT` 记录需要告诉 `kbpbot` 关于 Git 仓库的信息，而不是像之前那样的文件系统位置。它看起来像这样：

```
_keybase_pages.my-site.example.com. 300 IN TXT "kbp=git@keybase:team/gitwithkbpbot/git-site"
```

在常规 DNS 传播延迟之后，你的仓库 `master` 分支的推送内容将在 `https://my-site.example.com` 上可用。

{# note: the old bits about private shared (no team) Git repositories seem to be deprecated; I can’t figure out how to do it if it’s still possible #}

## 更多自定义

默认情况下，当你在 Keybase 托管自定义域名时，目录列表是禁用的。你可以通过在站点根目录创建一个 `.kbp_config` 文件来启用列表。此配置文件允许对站点的不同部分进行一些简单的自定义，包括启用跨域资源共享 (CORS)。

了解更多关于 [`.kbp_config`](/docs/sites/access-control)。
