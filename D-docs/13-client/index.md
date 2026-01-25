
# Keybase 客户端架构

Keybase 客户端是一个用 [Go](https://golang.org/) 编写的命令行应用程序。目前它运行在 macOS、Linux 和 Windows 上。
代码位于 [keybase/client](https://github.com/keybase/client) GitHub 仓库中。

## 客户端与服务的拆分

Keybase 二进制文件既可以作为命令行工具，也可以作为长期运行的“服务”——每次你运行一个命令时，工具（“客户端”）和服务都会参与其中。服务在每个命令之后保持活动状态，而每个命令都会创建一个单独的客户端进程并终止。如果需要响应命令执行工作（访问网络、运行 PGP 等），则由服务完成。

在 Linux 上，当你第一次运行客户端命令时，服务会在后台启动，后续的客户端命令会检查 `$XDG_RUNTIME_DIR/keybased.sock` 是否有活动服务，如果有则使用它——这被称为 "autofork" 模式。

在 macOS 上，服务由 `launchd` 在启动时启动。

为了调试，你可能会发现使用 `--standalone` 模式很有帮助，它只是在一个进程中运行所有内容。

对于我们即将推出的 KBFS 项目，`kbfsfuse` 二进制文件将作为一个客户端，通过长期运行的套接字与常规 Keybase 服务通信。

对于 iOS 和 Android，应用程序无法生成额外的线程，因此我们将在那里使用独立模式。我们甚至不能有一个 iOS/Android 进程和一个单独的 Go 进程，所以我们需要将 Go 运行时嵌入到单个应用程序进程中并向其传递消息。

对于 macOS 和 Electron 桌面 GUI 客户端，我们将使用单独的进程，就像我们对命令行客户端所做的那样。

## 机密信息 (Secrets)

服务缓存用户的口令，以避免每次运行命令时都询问用户（因此如果你使用 `--standalone`，你必须每次都输入它）。

被缓存的机密信息是：

- `libkb.PassphraseStream`: 用户 Keybase 口令的 [scrypt](https://en.wikipedia.org/wiki/Scrypt)，作为 `libkb.PassphraseStreamCache` 缓存在服务中。
- 一个登录会话盐，缓存为 `libkb.LoginSession.Salt()`。

## 与 GPG 交互

我们尝试使用 Go 的 `openpgp` 模块在内部运行加密操作，但在某些情况下（例如导入本地密钥）需要调用外部 GPG——你可以运行 `keybase help gpg` 来了解更多信息。

## RPC 协议

客户端和服务通过使用一种称为 [framed-msgpack-rpc](https://github.com/maxtaco/go-framed-msgpack-rpc) 的 RPC 协议进行通信（这是添加了消息分帧的 [msgpack-rpc](https://github.com/msgpack-rpc/msgpack-rpc) 版本）。这是一个双工协议——客户端打开到服务的 RPC 连接并进行函数调用，服务也可以对客户端做同样的事情。

传递参数 `--local-rpc-debug-unsafe=csv` 允许你查看这些 RPC 事务的内容。（它是“不安全”的，因为私有数据会被输出到日志中。）

## 协议绑定

我们使用与语言无关的协议描述格式来定义所有可用的命令及其参数和返回值。协议格式称为 [AVDL](http://avro.apache.org/docs/1.7.5/idl.html)，位于 [`client/protocol/avdl/*`](https://github.com/keybase/client/tree/master/protocol/avdl)。

我们根据此协议自动生成每种语言的绑定（objc, JS, Golang）。例如，生成的 Golang 绑定写入 [`client/go/protocol/keybase_v1.go`](https://github.com/keybase/client/blob/master/go/protocol/keybase_v1.go) 并作为 `keybase1` 导入到客户端代码中。

使用与语言无关的协议的原因是，我们期望拥有使用不同编程语言的命令行、GUI 和移动客户端，并希望能够在一个地方更新绑定。

在 Golang 中调用生成的函数如下所示：

```go
type CmdTrack struct {
        user    string
        options keybase1.TrackOptions
}

func (v *CmdTrack) Run() error {
        cli, err := GetTrackClient()
        if err != nil {
                return err
        }

        protocols := []rpc2.Protocol{
                NewIdentifyTrackUIProtocol(),
                NewSecretUIProtocol(),
        }
        if err = RegisterProtocols(protocols); err != nil {
                return err
        }

        return cli.Track(keybase1.TrackArg{
                UserAssertion: v.user,
                Options:       v.options,
        })
}
```

这里 `GetTrackClient()` 返回 `keybase1.TrackClient` 生成的函数；`protocols` 描述了客户端和服务在请求期间希望使用哪些 RPC 端点；`keybase1.TrackArg` 是绑定生成的 `Track` 参数结构体；`Track` 的返回值是内置的 Golang 类型 `error`。所以 `cli.Track` 将在服务上运行，将其结果返回给客户端。

### 向协议添加新函数

如果我们想向 `TrackClient` 添加一个新函数，我们将把它的定义添加到 [`client/protocol/avdl/track.avdl`](https://github.com/keybase/client/blob/master/protocol/avdl/track.avdl)，然后在安装了 Java 的情况下在 [`client/protocol`](https://github.com/keybase/client/tree/master/protocol/) 中运行 `make`。（如果我们想在一个新的 AVDL 文件中添加一个新的协议，我们也要把它添加到 [`client/protocol/Makefile`](https://github.com/keybase/client/blob/master/protocol/Makefile) 的 build-stamp 部分。）

## 一般文件结构

- `client/cmd_*` - 命令的客户端处理，例如 `client/cmd_track.go`
- `libkb/` - 服务端低级库函数，例如 `libkb/track.go`
- `engine/*` - 服务端高级库函数，例如 `engine/track*.go`。大多数对服务的调用只是围绕做大部分工作的引擎的包装器。这也是大多数测试发生的地方。

## 消息传递

由于服务正在做实际的工作，它将生成要向用户显示的消息。消息通过 `NewLogUIProtocol` 发送到客户端，其本身在 `keybase1.LogUiProtocol` 中描述。

日志（通常使用 `G.Log.*()` 创建）会自动从服务转发（再次通过 RPC）到客户端，以便可以在一个地方看到它们。你可以使用 `keybase -d <command>` 打开调试日志。

## 处理代码的技巧

### 构建

在 OSX 上，从源代码构建的受支持方式是使用 `brew`：

```sh
brew install go  # avoid building Go from source
brew --build-from-source keybase/beta/kbstage
```

在 Linux 上，你可以直接从 `client` 仓库构建：

```sh
git clone https://github.com/keybase/client
cd client/packaging
./clean_build_kbstage.sh
```

{## Commented until the public repo is available.

### Installing our git precommit hook

```sh
cd .git/hooks
ln -s ../../git-hooks/pre-commit
```

-->
##}
