{# yername = me?.basics?.username or 'yourname' #}
{# botname = 'kbpbot' #}
{# kbpdomain = 'kbp.keybaseapi.com' #}


<div id="introducing-kbp">

<md>

## Keybase Pages 入门

Keybase Pages 从 Keybase 文件系统或 Keybase Git 提供静态站点服务，使用你自己的域名，并带有由 [Let's Encrypt](https://letsencrypt.org/docs/faq/) 颁发的 HTTPS 证书。

你可以通过两个简单的步骤使用 Keybase Pages 托管静态站点：

1. 将站点内容放入 Keybase 文件系统或 Keybase Git 中，放在我们的机器人用户 #{botname} 可读的文件夹（或仓库）中。

2. 配置你的域名的 2 个 DNS 记录，以 1) 将域名的流量引导至 Keybase Pages 服务器，以及 2) 告诉 Keybase Pages 服务器去哪里查找站点内容。

### 准备或更新站点

准备站点最简单的方法是将带有静态站点内容的目录复制到 Keybase 文件系统的一个文件夹中。这可以简单地是你的公开文件夹 (`/keybase/public/#{yername}`)，或者是一个 `#{botname}` 有读取权限的非公开文件夹。例如，`/keybase/private/#{yername},#{botname}` 或 `/keybase/team/aclu.bots`（假设 #{botname} 是 `aclu.bots` 的读取者）。

如果你更喜欢使用 git 进行部署以便轻松进行原子更新，你也可以将静态站点推送到 git 仓库中。例如，`keybase://private/#{yername},#{botname}/my-site.git`。

例如，要在与 `#{botname}` 共享的文件夹中创建一个 hello-world 站点：

</md>
  <div class="well">
    <div class="form-group">
      <label for="populate-site-with">填充你的站点使用 ... </label>
      <select class="form-control auto-focus"
        name="populate-site-with" id="populate-site-with">
        <option value="kbfs" selected>KBFS 路径</option> 
        <option value="git">Git</option>
      </select>
    </div>
      <pre id='populate-site-output-kbfs'>
mkdir /keybase/private/#{yername},#{botname}/my-site
echo 'Hello, World!' > /keybase/private/#{yername},#{botname}/my-site/index.html</pre>
      <pre id='populate-site-output-git'>
mkdir my-site; cd my-site
echo 'Hello, World!' > index.html
git init . && git add . && git commit -m init
git remote add kbp keybase://private/#{yername},#{botname}/my-site.git
git push kbp master</pre>
    </div>
  </div>
<md>

### DNS 配置

要将流量处理委托给 Keybase Pages，你需要配置你的域名指向 Keybase Pages 端点 #{kbpdomain}。这通常通过 `CNAME` 记录完成。但如果你的 DNS 服务支持 `A`/`AAAA` `ALIAS` 记录，你也可以使用那个。

还需要第二个记录来指定站点的根目录，以便 Keybase Pages 服务器知道从哪里提供静态站点服务。如上所述，支持两种类型的根目录：KBFS 路径和托管在 Keybase 上的 Git 仓库。这是通过在站点所在域名下的 `_keybase_pages.` 子域名上的单个 TXT 记录完成的。例如，如果你在 `https://example.com` 上有一个静态站点，你需要在 `_keybase_pages.example.com` 上有这个 TXT 记录（除了 `example.com` 上的 CNAME 记录）。TXT 记录的值应为以下格式之一：

1. KBFS 路径：`"kbp=<kbfs_path>"`
2. Git 仓库：`"kbp=git@keybase:<private|public|team>/<folder_name>/<repo_name>"`

你可以使用以下工具为你的站点生成 DNS 记录：

</md>
  <div class="well">
    <div class="form-group">
      <label for="user-domain-name">域名：</label>
      <input class="form-control auto-focus" id="user-domain-name"
               autocapitalize="off" autocorrect="off" spellcheck="false"
               value="example.com" />
    </div>
    <pre id="dns-output">
    </pre>
  </div>
<md>

注意，我们这里使用的是 5 分钟的 TTL。在你确定配置无误后，你可以将其更改为更大的值，例如 3600（1 小时）。

每个域名注册商都有不同的 DNS 配置界面，所以很容易弄错。为了验证 DNS 配置，你可以使用 `dig` 查询配置的域名。你应该看到类似这样的内容：

</md>
  <pre id='dig-cname'>
  </pre>
  <pre id='dig-txt'>
  </pre>
<md>

注意，这可能不会立即显示，因为新添加的记录通常会有几分钟的 DNS 传播延迟。如果你正在更新现有记录，现有记录的 TTL 是传播延迟的上限。

</md>
  <p>
    DNS 传播后，你的站点应该可以在 <a id="site-url"></a> 访问了 🎉
  </p>
<md>

### 访问控制

默认情况下，Keybase Pages 启用整个站点的读取和列表功能。如果你更喜欢关闭目录列表，或者想要使用 [HTTP 基本认证](https://tools.ietf.org/html/rfc2617) 进行简单的 ACL 控制，你可以在站点根目录下提供一个可选的 `.kbp_config`。查看 [.kbp_config 文档](/docs/kbp/kbp_config) 获取更多详情。

</md>

<script type="text/javascript">
var kbp_getting_started_script = function() {
  var update_dns = function() {
    var domain = "", root = ""

    return function(data) {
      if (data.domain === domain && data.root === root) {
        return
      }

      domain = data.domain
      root = data.root

      $('#dns-output').text(
        domain + '                300 CNAME #{kbpdomain}\n' +
        '_keybase_pages.' + domain + ' 300 TXT   ' + data.root)

      $('#dig-cname').text('$ dig ' + domain + ' CNAME\n' +
        '...\n;; ANSWER SECTION:\n' + domain +
        ' <number> IN CNAME #{kbpdomain}.' + '\n...')
      $('#dig-txt').text('$ dig _keybase_pages.' + domain + ' TXT\n' + 
        '...\n;; ANSWER SECTION:\n_keybase_pages.'
        + domain + ' <number> IN TXT ' + root + '\n...')
    }
  }()

  var update_site_url = function() {
    var domain = ""

    return function(data) {
      if (data.domain === domain) {
        return
      }

      domain = data.domain

      var site_url = "https://" + domain + "/"
      $('#site-url').text(site_url)
      $('#site-url').attr("href", site_url)
    }
  }()

  var update_populate_site = function() {
    var root_type = ""

    return function(data) {
      if (root_type === data.root_type) {
        return
      }

      root_type = data.root_type

      if (root_type === 'kbfs') {
        $('#populate-site-output-git').hide()
        $('#populate-site-output-kbfs').show()
      } else if (root_type === 'git') {
        $('#populate-site-output-git').show()
        $('#populate-site-output-kbfs').hide()
      } else {
        $('#populate-site-output-git').hide()
        $('#populate-site-output-kbfs').hide()
      }
    }
  }()

  var get_data = function() {
    return {
      domain: $('#user-domain-name').val(),
      root_type: $('#populate-site-with').val(),
      root: function() {
        var root_type = $('#populate-site-with').val();
        if (root_type === 'kbfs') {
          return '"kbp=/keybase/private/#{yername},#{botname}/my-site"'
        } else if (root_type === 'git') {
          return '"kbp=git@keybase:private/#{yername},#{botname}/my-site"'
        } else {
          return "<invalid>"
        }
      }(),
    }
  }

  var update = function() {
    d = get_data();
    update_dns(d)
    update_site_url(d)
    update_populate_site(d)
  }

  $('#populate-site-with').change(update)
  $('#user-domain-name').on('input', update)

  update()
}()
kbp_getting_started_script()
</script>

</div>
