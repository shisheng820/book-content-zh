# 手机号码与电子邮件

当您希望与互联网上相识的人通信时，Keybase 是极佳的选择，因为您可以通过其社交身份（Twitter、Reddit、Mastodon 等）与其联系。

但对于您在_现实生活中_认识的许多人而言，身份证明并不那么有用。他们可能并未与您使用相同的社交媒体，或者您可能刚刚在咖啡店结识此人。

在 Keybase 4.3.0 版本中，用户现可添加并验证其手机号码与电子邮件，并向手机号码与电子邮件发送消息。与社交身份一样，[即使接收者尚未加入 Keybase](/blog/keybase-chat)，您也可以向其发送消息。

## 使用指南

首先，请确保您已更新至最新的 Keybase 版本。

要添加手机号码或电子邮件地址，请前往“设置”选项卡（或在移动端，点击汉堡菜单 -> 您的账户）。

<center style="margin:40px 0;"><img src="/docs-assets/contacts/settings.png" class="img img-responsive" width="500"
    alt="Keybase Settings tab on desktop"></center>

要发起与手机号码或电子邮件的对话，请前往“聊天”选项卡，点击左上角的新建对话按钮（Ctrl-N 或 Mac 上的 ⌘N）。

<center style="margin:40px 0;"><img src="/docs-assets/contacts/chat.png" class="img img-responsive" width="500"
    alt="Keybase Chat tab on desktop"></center>

输入手机号码或电子邮件地址。若 Keybase 用户已验证该联系方式并将其设为可搜索，其账户将会显示；否则，您仍可发起对话，接收者将在加入 Keybase、验证其联系方式并将其设为可搜索后收到消息。

<center style="margin:40px 0;"><img src="/docs-assets/contacts/new-chat.png" class="img img-responsive" width="300"
    alt="Keybase New Chat modal on mobile"></center>

在移动端，您可以导入通讯录以快速查找哪些联系人已加入 Keybase。您可以在汉堡菜单 -> 手机联系人中切换此设置。

## 安全考量

与所有 Keybase 设备均可公开查验的身份证明不同，手机号码与电子邮件验证仅由 Keybase 服务器进行验证。这意味着当您发起与手机号码或电子邮件的对话时，您信任 Keybase 服务器会在首次提供正确的用户——这被称为首次使用信任（TOFU）。

初始对话开启后，Keybase 服务器便无法再进行欺诈，因为双方用户的设备此时会相互验证。此后，当用户聊天时，其设备仅针对已验证的设备加密消息。

在 Signal、Wire 和 Riot 等应用中，您可以选择验证[密钥指纹或安全码](https://support.signal.org/hc/en-us/articles/360007060632-What-is-a-safety-number-and-why-do-I-see-that-it-changed-)，以确保您正在与正确的人交谈。

得益于[全局 Merkle 树](/docs/server_security)，在 Keybase 上与手机号码及电子邮件发起对话时，若要达到同等安全级别，您仅需在 Keybase 之外（当面、通过电话等）交换 Keybase 用户名。

## 隐私考量

部分用户可能不希望 Keybase 服务器知晓其手机号码或电子邮件地址。Keybase 绝不会强制用户添加手机号码，尽管目前注册 Keybase 仍需电子邮件地址，但在未来的 Keybase 版本中，我们将移除此项要求。

部分用户可能希望注册手机和电子邮件以接收 Keybase 通知，但不希望其他用户通过这些手机号码或电子邮件地址找到他们。这可以通过在添加时取消选中“允许好友通过此号码/电子邮件地址找到您”选项来实现。您可以在“设置”选项卡中通过将其设为“不可搜索”来切换此选项。

<center style="margin:40px 0;"><img src="/docs-assets/contacts/unsearchable.png" class="img img-responsive" width="500"
    alt="Make unsearchable menu in the Keybase settings tab on desktop"></center>

在此功能推出之前注册的所有用户，其电子邮件默认设为不可搜索。

部分用户可能不希望 Keybase 服务器知晓其通讯录。联系人同步是一项可选功能，旨在帮助您查找可能已加入 Keybase 的好友。进行联系人同步时，设备会向服务器发送通讯录中联系人的手机号码和电子邮件，但不会发送姓名、标签或其他元数据。服务器将回复拥有匹配这些手机号码和电子邮件账户的 Keybase 用户，随即丢弃该数据：用户通讯录不会永久存储在服务器上。

目前，我们尚未通过私有集合交集或 Signal 的 [基于 SGX 的私有联系人发现](https://signal.org/blog/private-contact-discovery/) 等系统来证明这一点。未来，我们希望提高联系人同步的隐私性，使用户无需信任 Keybase 服务器会丢弃通讯录数据。
