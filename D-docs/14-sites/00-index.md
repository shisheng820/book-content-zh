
  ## Keybase.pub

  [Keybase.pub](https://keybase.pub) 提供它在 `/keybase/public` 中能找到的任何内容。诗歌。猫图。Midi 文件。热门食谱。

  例如，这里我们看到 `/keybase/public/chris/photos/` 在 https://keybase.pub/chris/photos 上提供服务：

  <img src="/images/getting-started/kpub-screenshot.jpg" class="img img-responsive">

  #### 原始 vs 包装 (Raw vs. wrapped)

  - https://keybase.pub/#{yername} 提供一个*包装*的站点，允许人们浏览你的文件。
  - https://#{yername}.keybase.pub 提供*原始*文件
  - 如果你请求一个目录，https://#{yername}.keybase.pub 也将提供 index.html 或渲染 index.md。

  ## 安全性

  如果你从 Keybase.pub 下载东西，你是信任 (a) 通过 https 的 Keybase，以及 (b) 没有人入侵 Keybase.pub。所以这是一个探索的好网站，但如果你正在下载一些关键的东西，比如最新的 `libssl` 或 `bitcoind` 或来自朋友的 `GPG Tools Suite.dmg` 副本，你应该真的只看你自计算机上的 `/keybase/public`。这将验证所有的加密，并保证你看到的是他们签名的相同位。而且这更容易。

  ### 灵感

  Keybase.pub 网站由 Keybase 团队制作，但它实际上是一个概念验证。该网站没有特权。它有点笨——只是 nginx 重写一些 URL，以及一个基本的 Node.js 网站，提供静态资源并打印用户信息。Keybase.pub 展示了在 Keybase 文件系统之上构建东西是多么容易。我们听到的其他想法……请随意实现：

  - 一个服务，**"somehost"**，基于 /keybase/private/user,somehost/ 中的代码为每个用户启动*真正的网站*
  - 一个比特币钱包，在私有文件夹内共享硬币
  - 一个“如果我死了”的应用程序，在一群朋友之间拆分秘密。
  - 一个签名的博客平台
  - 你的想法在这里
  - 你的其他想法在这里
  - 你的第三个也是最后一个想法
