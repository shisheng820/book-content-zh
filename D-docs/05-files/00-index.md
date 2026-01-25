# Keybase 文件系统介绍

Keybase 应用的 Alpha 版本开始附带一个加密安全的文件挂载。它是全新的，且与众不同。

![终端一瞥 /keybase/public/chris](https://keybase.io/images/getting-started/terminal1.png)

### 面向全世界的公开、签名目录

您现在可以在一个非常特殊的地方写入数据：

```
/keybase/public/yourname
```

或者，在 Windows 中：

```
k:\\public\\yourname
```

*您在其中写入的每个文件均经过签名。* 无需手动签名过程，无需 `tar` 或 `gzip` 打包，也无需分离的签名文件。相反，该文件夹中的所有内容在每个人的计算机上均显示为明文文件。您甚至可以在 Finder 或资源管理器中打开 `/keybase/public/yourname` 并拖入文件。

这是我的公开文件夹：

```
/keybase/public/chris
```

![Mac 用户输入 `open /keybase/public/chris` 后看到的内容](https://keybase.io/images/getting-started/finder2.png)

或者，也许您通过其他方式认识我。在这种情况下，您可以*声明*我已将某个身份与我的密钥进行了双向连接。这些文件夹名称同样有效：

```
/keybase/public/malgorithms@hackernews/
/keybase/public/malgorithms@twitter/
/keybase/public/malgorithms@reddit/
```

在我的文件夹中，您会发现一些技术相关的内容，例如我的 SSH 公钥、我的 Signal 应用指纹，以及一些我已手动验证并希望安全分发给朋友的软件。

在您的文件夹中放置什么由您决定：全世界都会高兴地知道，他们看到的*正是您所看到的比特位*，没有任何服务端或中间人作恶的风险。

当您访问*陌生人*的文件夹（例如，[我的](https://keybase.io/chris)）时，

![/keybase/public/chris](https://keybase.io/images/getting-started/coyne-tracker.png)

弹出窗口显示明文和普通用户名。以下是它隐藏的幕后繁杂工作：

1.  从 Keybase 请求该用户的信息（密钥 + 证明）
2.  回放该用户签名的声明与吊销
3.  实际抓取推文、帖子、个人资料等
4.  以密码学方式验证您所做的声明是否通过
5.  如果一切顺利，下载数据块
6.  确保数据块已签名，并且
7.  重建文件夹
8.  以普通文件形式呈现

与 Dropbox、Google Drive 和 Box 不同，这里没有同步模型。文件按需流式传输。

如果您想了解更多信息，请继续查看这个由我签名的文本文件：

```bash
cat /keybase/public/chris/plan.txt
```

### Keybase.pub

作为概念验证，https://keybase.pub 是一个直接从 `/keybase/public` 提供静态内容的网站。您可以在 https://keybase.pub/chris/plan.txt 查看我的 `plan.txt` 文件。该网站也是一个正在进行中的项目。

### 还有更多！

Keybase 将 **端到端加密文件夹** 挂载在 **`/keybase/private`** 中。

```
/keybase/private/{people}
```

这是您自己的加密文件夹，仅供您使用：

```
/keybase/private/yourname
```

这是一个只有您和我可以读取的文件夹。您无需创建此文件夹，它隐式存在。

```
/keybase/private/yourname,chris
```

同样，也许您在 Twitter 上认识我，并更喜欢声明：

```
/keybase/private/yourname,malgorithms@twitter
```

这些文件夹仅使用您和我的设备特定密钥进行加密。

*Keybase 服务器没有可以读取此数据的私钥。* 它们也无法在此过程中注入任何公钥，以诱骗您为额外的参与方加密。您和我对密钥的添加和移除均由我们在公开 Merkle 树中签名，该树反过来哈希进比特币区块链中，以防止分叉攻击。这是我的 7 个设备密钥和 9 个公开身份的截图，以及它们是如何关联的。

![粉色和橙色的设备拥有解密密钥，蓝色的节点是您可能做出的声明](https://keybase.io/images/getting-started/cc-graph2.png)

来源: https://keybase.io/chris/sigchain

提醒一下，Keybase 是 [开源 Go 项目](https://github.com/keybase/client/tree/master/go/kbfs)。这是关于文件挂载的 [加密规范](/docs/kbfs-crypto)，随着项目的演进，我们将乐于对其进行更改和更新。（期待反馈！）

### 无摩擦分享

很快，您将能够把数据扔进 `/keybase/private/yourname,pal@twitter`，*即使该 Twitter 用户尚未加入 Keybase*。您的应用将*仅为您*加密，然后在该 Twitter 用户加入并声明密钥时在后台唤醒并重新生成密钥（rekey）。

当我们意识到这种密钥-身份解决方案实际上可以降低分享的摩擦时，我们决定全职投入 Keybase 的工作。

相比之下，这张截图出现在今年早些时候 Keybase 的融资演示文稿中：

![电子邮件或电话号码作为分享标识符非常有 2007 年的感觉](https://keybase.io/images/getting-started/dropbox_sharing.png)

我们的目标：恰好在一个公开的 Reddit、HackerNews 或 Twitter 对话中，您*应该*能够说“嘿，我把那些 gif/库/随便什么扔进了我们的加密 keybase 文件夹”，而无需索要更多身份信息。如果那个人尚未安装 Keybase，您的人工工作依然完成了。他们可以在几秒钟内加入并访问数据，而您的设备将悄悄处理验证和重新生成密钥的工作，无需信任 Keybase 的服务器。

### 回到您身上...

无论如何，如果您拥有新的 Keybase，请继续，开始写日记：

```bash
cd /keybase/private/yourname
echo 'The brain...it moved again.' > diary.txt
```

在 Mac 上，您可以直接在 Finder 中打开文件夹：

```bash
open /keybase/private/yourname
```

然后拖入文件。

## 问题与其他细节

### 纸质密钥 (Paper keys)

这是一个全功能的私钥。它可用于配置甚至重新生成密钥。如果您想在无需已配置设备的情况下配置新的 Keybase 安装，请将其放在钱包中携带。您可以使用 `keybase paperkey` 制作额外的纸质密钥，并使用 `keybase device [list|remove]` 吊销丢失的密钥。

![您将选择 `选项 2`，除非您有两台并排的电脑；`选项 3` 通常不起作用（它适用于您设置的第一台电脑）](https://keybase.io/images/getting-started/provision.png)

### 元数据与安全性

Keybase 服务器显然可以读取 `/keybase/public` 中的所有内容。

至于 `/keybase/private`，Keybase *可以* 知道

1.  您正在哪些顶级文件夹中工作（例如 `/keybase/private/yourname,pal`），
2.  您*何时*写入和读取数据，以及
3.  大约*多少*数据。

Keybase 服务器*不知道*单个文件名或子目录名。它可以尝试猜测您是在写入 100 个小文件还是 1 个大文件，但这将是基于时间的猜测。如果您在名为 `/keybase/private/yourname/pics_of_me/thong.jpg` 的私有文件夹中写入一个 1MB 的文件，Keybase 服务器完全不知道这是一个名为 `pics_of_me` 的文件夹，或者有一个名为 `thong.jpg` 的文件，或者您看起来是否不错。它不知道您是在写入图片、Excel 文档、您的 DNA 序列还是 MP3。

### “关注”他人增加安全性

当您在 Keybase 上关注某人时，您会对您看到并验证过的他们的身份摘要进行签名。从那时起，每当您使用他们的 keybase 用户名时，*您关注声明中的所有内容*必须保持有效。这比仅仅声明一个身份要安全得多。

![](https://keybase.io/images/tracking/maria_twitter.jpg)

所以，关注别人吧。

### 数据丢失风险

在撰写本文档时，只有极少数人使用此系统。我们刚刚开始测试。请注意，我们可能会（假设地）随时丢失您的数据。或者推送一个导致您丢弃私钥的 bug。呃，太糟了。

作为我们的首批测试者之一：*请备份您放入 Keybase Alpha 版的任何内容*，并记住：我们无法恢复丢失的加密数据。

此外，如果您丢弃了所有设备，您将丢失您的私有数据。您的加密数据仅针对您的设备和纸质密钥加密，而非您拥有的任何 PGP 密钥。

### 存储

我们为每个人提供 250 GB 的空间。我们的配额模型：

- 在共享目录中写入时，仅影响写入者的配额。哇哦！所以您永远不必担心损害他人的配额或磁盘空间（再次强调：摩擦）。Keybase 必须以这种方式工作，因为它不基于同步模型工作，也不需要在加密和与他人分享之前获得批准。

- 历史数据确实会计入您的配额，您很快将拥有控制保留已删除块时长的选项。

目前没有付费升级。250GB 的免费账户将保持免费，但我们可能会为希望存储更多数据的人提供付费存储。

### 性能

我们尚未进行任何性能优化。还有很多唾手可得的优化空间。

### 迭代发布

Keybase 即将成为一个全功能的 GUI 应用。

当 Keybase 应用提示安装更新时，我们鼓励您接受它。它将由我们签名。

### 感兴趣的公开文件夹

* [/keybase/public/libevent](https://keybase.pub/libevent) – 流行的回调通知库。[浏览](https://keybase.pub/libevent) | [精美站点](https://libevent.keybase.pub)
* /keybase/public/chris - 我的示例文件夹 [浏览](https://keybase.pub/chris) | [精美站点](https://chris.keybase.pub)

如果上面有人是流行软件包的知名作者或知名人士，我会添加他们。如果您有任何有趣的东西，请发邮件给我 (chris@keybase.io)。

### 错误报告

如果您遇到任何类型的 bug，请运行：

```
keybase log send
```

这将 (1) 为我们打包您的日志并发送，以及 (2) 生成一个预填好的 github issue 页面，其中包含您的日志 ID。

### 商业模式？

我们距离担心这个问题还很远，但我们永远不会再经营广告支持的业务。Keybase 永远不会出售数据。这是我们的约束：

- 无广告
- 不出售数据
- 我们希望为全世界每个人提供免费、简便的公钥
- 我们提供的任何托管服务（例如此文件系统）对大多数人应该是免费的
- “客户”将是拥有许多用户的组织和/或希望获得超额资源的个人。

但是，如上所述，目前没有付费模式，我们也不试图赚钱。我们目前正在测试产品，并且我们希望将公钥带给大众。

### 链接

* [下载它！](https://keybase.io/download)
* [所有其他文档](https://keybase.io/docs)
* [通过 GitHub 报告问题](https://github.com/keybase/client/issues)
