{% set section_title = "kbpgp.js" %}

# JavaScript 中的 PGP

*kbpgp* 是 Keybase 的 JavaScript PGP 实现。它易于使用，专为并发设计，并且在 Node.js 和浏览器中都很稳定。它目前正在积极维护中，并基于 BSD 许可证永久属于你。本页开始一个简短的教程。

{# TODO: JavaScript mini app thing from https://keybase.io/kbpgp #}

### 获取它

Zip 文件（用于浏览器）

- [kbpgp-2.1.0-release.zip](https://keybase.io/kbpgp_public/releases/kbpgp-2.1.0-release.zip)

用于 Node.js（通过 NPM）

```
npm install kbpgp
```

源码来自 [GitHub](https://github.com/keybase/kbpgp)

```
git clone https://github.com/keybase/kbpgp.git
```

### 入门

浏览器

```
<script src="kbpgp-2.1.0.js"></script>
```

Node.js

```
var kbpgp = require('kbpgp');
```


## Key Manager (密钥管理器)

*在执行任何加密操作之前，你需要一个 KeyManager。*

一个 KeyManager 包含一个公钥，可能还包含特定人员的私钥和子钥。一旦你有了一个 KeyManager 实例，你就可以使用其中的密钥执行操作。对于签名和加密操作，你需要两个 KeyManager：一个包含私钥（用于签名者），另一个包含公钥（用于接收者）。

例如，假设我们要执行加密，且有两个 KeyManager 实例：`alice` 和 `chuck`。

```javascript
var params = {
  encrypt_for: chuck,
  sign_with:   alice,
  msg:         "Hey Chuck - my bitcoin address is 1alice12345234..."
};

kbpgp.box(params, function(err, result_string, result_buffer) {
  console.log(err, result_string, result_buffer);
});
```

kbpgp 的 `box` 函数执行所有工作。请注意，它会回调返回字符串和 Buffer 表示形式。Buffer 要么是 [Node.js Buffer](http://nodejs.org/api/buffer.html)，要么是具有类似功能的浏览器友好对象。

很简单，对吧？那么，如何获得 KeyManager 呢？有 2 种方法：

- [加载密钥或密钥对](#loading-a-key)
- [生成新的密钥对](#generating-a-pair)

### <a id="loading-a-key"></a>加载密钥

以下示例演示了将 PGP 密钥字符串（经典 ASCII armored 格式）转换为 KeyManager 的过程。

#### 示例 1 - 从公钥创建 KeyManager

```javascript
var alice_pgp_key = "-----BEGIN PGP PUBLIC ... etc.";

kbpgp.KeyManager.import_from_armored_pgp({
  armored: alice_pgp_key
}, function(err, alice) {
  if (!err) {
    console.log("alice is loaded");
  }
});
```

#### 示例 2 - 从私钥创建 KeyManager

现在假设我们有 alice 的私钥。回想一下，这包含了她的公钥，所以这就是我们需要的一切。

```javascript
var alice_pgp_key    = "-----BEGIN PGP PRIVATE ... etc.";
var alice_passphrase = "martian-dung-flinger";

kbpgp.KeyManager.import_from_armored_pgp({
  armored: alice_pgp_key
}, function(err, alice) {
  if (!err) {
    if (alice.is_pgp_locked()) {
      alice.unlock_pgp({
        passphrase: alice_passphrase
      }, function(err) {
        if (!err) {
          console.log("Loaded private key with passphrase");
        }
      });
    } else {
      console.log("Loaded private key w/o passphrase");
    }
  }
});
```

#### 示例 3 - 从公钥创建 KeyManager，然后添加私钥

上面的示例 ([#2](example-2-a-keymanager-from-a-private-key)) 可以分两步执行。你可以使用 alice 的公钥创建一个 KeyManager 实例，然后将她的私钥添加到其中。如果她的私钥与公钥不匹配，这将产生错误。

```javascript
var alice_public_key = "-----BEGIN PGP PUBLIC ... etc.";
var alice_private_key = "-----BEGIN PGP PRIVATE ... etc.";
var alice_passphrase = "ovarian fred savage ";

kbpgp.KeyManager.import_from_armored_pgp({
  armored: alice_public_key
}, function(err, alice) {
  if (!err) {
    alice.merge_pgp_private({
      armored: alice_private_key
    }, function(err) {
      if (!err) {
        if (alice.is_pgp_locked()) {
          alice.unlock_pgp({
            passphrase: alice_passphrase
          }, function(err) {
            if (!err) {
              console.log("Loaded private key with passphrase");
            }
          });
        } else {
          console.log("Loaded private key w/o passphrase");
        }
      }
    });
  }
});
```


### <a id="generating-a-pair"></a>生成密钥对

你可以创建一个 KeyManager 并一次性生成新密钥。

在以下过程结束时，我们将拥有一个 KeyManager 实例 `alice`，它可用于任何加密操作。

#### 示例 1 - RSA - 使用自定义设置

为了说明一个常见用例，我们将为签名和加密生成子钥。顺便说一句，当 kbpgp 使用 KeyManager 执行操作时，它会自动选择合适的子钥。

```javascript
var F = kbpgp["const"].openpgp;

var opts = {
  userid: "User McTester (Born 1979) <user@example.com>",
  primary: {
    nbits: 4096,
    flags: F.certify_keys | F.sign_data | F.auth | F.encrypt_comm | F.encrypt_storage,
    expire_in: 0  // never expire
  },
  subkeys: [
    {
      nbits: 2048,
      flags: F.sign_data,
      expire_in: 86400 * 365 * 8 // 8 years
    }, {
      nbits: 2048,
      flags: F.encrypt_comm | F.encrypt_storage,
      expire_in: 86400 * 365 * 8
    }
  ]
};

kbpgp.KeyManager.generate(opts, function(err, alice) {
  if (!err) {
    // sign alice's subkeys
    alice.sign({}, function(err) {
      console.log(alice);
      // export demo; dump the private with a passphrase
      alice.export_pgp_private ({
        passphrase: 'booyeah!'
      }, function(err, pgp_private) {
        console.log("private key: ", pgp_private);
      });
      alice.export_pgp_public({}, function(err, pgp_public) {
        console.log("public key: ", pgp_public);
      });
    });
  }
});
```

太简单了！

#### 示例 2 - RSA - 使用合理的默认值

上面的参数是合理的。如果你对它们满意，可以直接调用 `KeyManager::generate_rsa` 快捷方式：

```javascript
kbpgp.KeyManager.generate_rsa({ userid : "Bo Jackson <user@example.com>" }, function(err, charlie) {
   charlie.sign({}, function(err) {
     console.log("done!");
   });
});   
```

### 示例 3 - ECC 密钥对 - 自定义

Kbpgp 支持椭圆曲线 PGP (有关详细信息，请参阅 [RFC-6637](http://tools.ietf.org/html/rfc6637))。你可以向上述生成调用提供 `ecc : true` 选项，以生成 ECC 密钥对而不是标准 PGP 密钥对。但请记住，目前大多数 GPG 客户端并不支持 ECC。

```javascript
var F = kbpgp["const"].openpgp;

var opts = {
  userid: "User McTester (Born 1979) <user@example.com>",
  ecc:    true,
  primary: {
    nbits: 384,
    flags: F.certify_keys | F.sign_data | F.auth | F.encrypt_comm | F.encrypt_storage,
    expire_in: 0  // never expire
  },
  subkeys: [
    {
      nbits: 256,
      flags: F.sign_data,
      expire_in: 86400 * 365 * 8 // 8 years
    }, {
      nbits: 256,
      flags: F.encrypt_comm | F.encrypt_storage,
      expire_in: 86400 * 365 * 8
    }
  ]
};

kbpgp.KeyManager.generate(opts, function(err, alice) {
  // as before...
});
```

#### 示例 4 - ECC 密钥对 - 使用合理的默认值

为了使用这些默认参数，我们同样提供了快捷方式：

```javascript
kbpgp.KeyManager.generate_ecc({ userid : "<user@example.com>" }, function(err, charlie) {
   charlie.sign({}, function(err) {
     console.log("done!");
   });
});
```

#### 监控

所有 kbpgp 函数都支持传递一个“异步包” (ASync Package, ASP) 对象，用于监控。你的 ASP 可以有一个 progress_hook 函数，它将随进度信息被调用。这对于 RSA 密钥生成特别重要，因为它可能需要一点时间。如果这是在任何类型的客户端应用程序中，你会希望 (a) 显示一些指示器表明你正在工作，以及 (b) 有一个取消按钮。

```javascript
var my_asp = new kbpgp.ASP({
  progress_hook: function(o) {
    console.log("I was called with progress!", o);
  }
});

var opts = {
  asp: my_asp,
  userid: "user@example.com",
  primary: {
    nbits: 4096
  },
  subkeys: []
};

kbpgp.KeyManager.generate(opts, some_callback_function);
```

#### 取消

如果你如上所述传递了一个 ASP 对象，你可以使用它来取消你的进程。

```javaascript
kbpgp.KeyManager.generate(opts, some_callback_function);

// oh, heck, let's give up if it takes more than a second
setTimeout((function() {
  my_asp.canceler.cancel();
}), 1000);
```

在上面的例子中，如果生成未在一秒内完成，工作将停止，并且 `some_callback_function` 将立即被调用，参数为 `err, null`。


### API

给定 `KeyManager` 类 (`kbpgp.KeyManager`) 和一个实例 `alice`，你可以访问以下函数。

#### 首先，选项说明

1. 当 `opts` 作为参数时，它是一个字典。你可以传递空字典 `{}`
2. 在任何 kbpgp 函数中，你可以设置 `opts.asp` 为一个 ASP 对象来监控进度并可选地取消它。有关更多信息，请参阅示例。

{# TODO: table #}

- `KeyManager.generate(opts, cb)` `KeyManager.generate_rsa(opts, cb)` `KeyManager.generate_ecc(opts, cb)`: 回调返回 `err, key_manager` ([见示例](#generating-a-pair))
- `KeyManager.import_from_armored_pgp(opts, cb)`: 回调返回 `err, key_manager`。如果你正在导入私钥，你会想要检查它是否有密码并解锁它。([见示例](#loading-a-key))
- `alice.has_pgp_private()`: 如果 alice 的 `key_manager` 包含私钥，则返回 true
- `alice.is_pgp_locked()`: 如果 alice 的私钥受密码保护且已锁定，则返回 true
- `alice.unlock_pgp(opts, cb)`: 如果 alice 的私钥已锁定，则解锁它；回调返回任何错误 ([见示例](#loading-a-key))；`opts.passphrase`: 包含 alice 私钥密码的字符串
- `alice.check_pgp_public_eq(chuck)`: 如果 alice 和另一个 KeyManager 实例 (chuck) 具有相同的主键和子键，则返回 true
- `alice.merge_pgp_private(opts, cb)`: 如果 alice 加载时没有私钥，此函数允许你事后合并她的私钥。一旦合并，如果它是密码保护的，你会想要 (a) 用 `alice.is_pgp_locked()` 识别它，然后 (b) 用 `alice.unlock_pgp_key()` 解锁它；`
opts.armored`: 包含她私钥的字符串（armored 格式）
- `alice.export_pgp_public(opts, cb)`: 回调返回 `err, str`。这将生成 alice 公钥的标准 PGP armored 格式。([见示例](#generating-a-pair))
- `alice.export_pgp_private(opts, cb)`: 回调返回 `err, str`。这将生成 alice 密钥的标准 PGP armored 格式，受密码保护。([见示例](#generating-a-pair))；`opts.passphrase`: 保护密钥的密码

### 加密和/或签名

在 kbpgp 中，加密、签名或两者兼有的步骤都是相同的。唯一的区别是你需要什么 [KeyManager](#key-manager)。要签名某些东西，你需要一个包含私钥的 KeyManager。要加密某些东西，你需要一个包含接收者公钥的 KeyManager。如果你的 KeyManager 包含子钥，kbpgp 将自动使用合适的子钥。

#### 示例 1 - 仅加密

假设：我们有一个 KeyManager 实例 `chuck`，用于接收者。

```javascript
var params = {
  msg:         "Chuck chucky, bo-bucky!",
  encrypt_for: chuck
};

kbpgp.box(params, function(err, result_string, result_buffer) {
  console.log(err, result_armored_string, result_raw_buffer);
});
```  

#### 示例 2 - 仅签名

同样，签署明文消息很容易。只需提供 `sign_with` KeyManager，但不提供 `encrypt_for`。

```javascript
var params = {
  msg:        "Here is my manifesto",
  sign_with:  alice
};

kbpgp.box (params, function(err, result_string, result_buffer) {
  console.log(err, result_string, result_buffer);
});
```

#### 示例 3 - 签名 + 加密

假设：我们也有一个 KeyManager 实例 `alice`，用于发送者。

```javascript
var params = {
  msg:         "Chuck chucky, bo-bucky! This is Alice here!",
  encrypt_for: chuck,
  sign_with:   alice
};

kbpgp.box (params, function(err, result_string, result_buffer) {
  console.log(err, result_string, result_buffer);
});
```

#### 示例 4 - 使用输入和输出 Buffer

kbpgp 可以接受 *Node.js Buffer* 作为输入，而不是字符串。以下代码读取 .png 文件并写入一个新的加密副本。有关更多信息，请查看 kbpgp [buffers](#files-and-buffers) 文档。

```javaascript
var kbpgp  = require('kbpgp');
var fs     = require('fs');
var buffer = fs.readFileSync('dirty_deeds.png');
var params = {
  msg:         buffer,
  encrypt_for: chuck,
  sign_with:   alice
};

kbpgp.box (params, function(err, result_string, result_buffer) {
  fs.writeFileSync('dirty_deeds.encrypted', result_buffer);
});
```

浏览器中也可以使用 Buffer，以便对文件进行 HTML5 操作。`kbpgp.Buffer` 提供了与 Node.js 匹配的浏览器实现。

#### 示例 5 - 进度钩子和取消

大多数 kbpgp 函数都可以接受一个 `kbpgp.ASP` 对象，用于监控进度并检查取消请求。

```javascript
var asp = new kbpgp.ASP({
  progress_hook: function(info) {
    console.log("progress...", info);
  }
});

var params = {
  msg:         "a secret not worth waiting for",
  encrypt_for: chuck,
  asp:         asp
};

kbpgp.box(params, function(err, result_string, result_buffer) {
  console.log("Done!", err, result_string, result_buffer);
});

// sometime before it's done
asp.canceler().cancel();
```

### 解密和验证

解密和验证比加密或签名稍微复杂一些，因为通常你不知道通过什么 KeyManager。对于签名和加密的 PGP 消息，你只有在成功解密后才知道需要哪个验证密钥。此外，PGP 中的消息可以为多个接收者加密，任何给定的接收者可能只能访问许多可能的解密密钥中的一个。

在 kbpgp 中，`unbox` 函数处理解密和验证的细节。你需要传递给它一个 PGP 消息（加密、签名或两者兼有），以及一种中途获取密钥的方法——一个 `kbpgp.KeyFetcher` 对象。你可以直接使用我们提供的，也可以子类化你自己的（例如，如果你想从你的服务器获取密钥）。

#### 开箱即用：KeyRing

```javascript
var ring = new kbpgp.keyring.KeyRing();
var kms = [ alice, bob, charlie ];
for (var i in kms) {
  ring.add_key_manager(kms[i]);
}
```

#### 解密和验证示例

通过 `unbox` 函数解密并验证。传递消息、KeyFetcher（如上面的 `ring`）、ASP（如果你打算取消或监控进度），以及完成时触发的回调：

```javascript
var ring = new kbpgp.keyring.KeyRing;
var kms = [alice, bob, charlie];
var pgp_msg = "---- BEGIN PGP MESSAGE ----- ....";
var asp = /* as in Encryption ... */;
for (var i in kms) {
  ring.add_key_manager(kms[i]);
}
kbpgp.unbox({keyfetch: ring, armored: pgp_msg, asp }, function(err, literals) {
  if (err != null) {
    return console.log("Problem: " + err);
  } else {
    console.log("decrypted message");
    console.log(literals[0].toString());
    var ds = km = null;
    ds = literals[0].get_data_signer();
    if (ds) { km = ds.get_key_manager(); }
    if (km) {
      console.log("Signed by PGP fingerprint");
      console.log(km.get_pgp_fingerprint().toString('hex'));
    }
  }
});
```

`unbox` 回调有两个参数：如果出错则为 Error，否则为 `Literals` 数组。`Literal` 对象支持 `toString(enc)` 和 `toBuffer()` 方法。前者调用接受一个可选参数，即编码；如果没有提供，kbpgp 将使用 PGP 消息中指定的编码；如果你想覆盖该编码，可以指定 `utf8`、`ascii`、`binary`、`base64` 或 `hex`。

此示例表明 `unbox` 处理解密和验证。要检查消息的某些部分是否已签名，请对消息中的每个 `Literal` 调用 `get_data_signer`。请注意，你加载到 KeyFetcher 中的同一个 KeyManager 会出现在这里。因此，如果你用自定义字段扩充该 KeyManager，它们将在此处可用。

#### KeyFetcher 接口

在更通用的解密/验证场景中，你可能需要从辅助或远程存储中获取适当的解密和/或验证密钥。在这种情况下，你不应该使用上述的 KeyRing，而应该提供一个自定义的 KeyFetcher。

所有可用的 KeyFetcher 必须实现一个方法：`fetch`。给定几个 PGP 密钥 ID 和一个指定请求操作的标志，fetch 方法应该回调返回一个 `KeyManager`（如果能找到）。

`fetch(ids,ops,cb)` 调用有三个参数：

1. `ids`—[Buffers](#files-and-buffers) 数组，每个都包含一个 PGP 密钥的 64 位 ID。这些密钥可能引用子钥，通常用于加密和签名消息。
2. `ops`—此密钥所需的加密选项；`kbpgp.const.ops` 中常量的按位或，包括：
    - encrypt : `0x1`
    - decrypt : `0x2`
    - verify : `0x4`
    - sign : `0x8`
3. `cb`—完成时的回调，回调返回一个三元组：`(err,km,i)`
    - `err` 是解释出错原因的 Error，成功则为 null。
    - `km` 是（成功时）满足给定要求的 KeyManager
    - `i` 是（成功时）指示在查找中找到了哪个密钥的整数。如果此处返回 `0`，则 `ids[0]` 是 `km` 内密钥的 64 位 ID。

### <a id="files-and-buffers"></a>文件和 Buffer

*在大多数示例中，我们处理的是字符串明文和密文。当然，有时你想要读取和写入文件并转换为有趣的字符串，如 hex 或 base64。*

回想一下，当我们加密时，我们期望消息是一个字符串：

```javascript
var params = {
  msg: "Chuck chucky, bo-bucky!",
  encrypt_for: chuck // a KeyManager instance
};
```

在 Node.js 中，我们可以传递一个 [Node.js Buffer](http://nodejs.org/api/buffer.html)。这可以来自文件。请记住，此文件的 Buffer 和输出需要能轻松放入内存。（对于任意大的文件，kbpgp 未来将支持流。）

```javascript
fs.readFile('foo.png', function(err, buff) {
  var params = {
    msg:         buff,
    encrypt_for: chuck
  };
});
```

在浏览器中，我们有类似的 Buffer 可用：`kbpgp.Buffer`。它的行为与 Node.js buffer 完全相同，这要归功于 [native-buffer-browserify](https://github.com/substack/native-buffer-browserify)。

```javascript
// using a string as a Buffer, in the browser
var params = {
  msg:         kbpgp.Buffer.from("Chuck chucky, bo-bucky!"),
  encrypt_for: chuck
};
```

#### 输出 Buffer

kbpgp 的 `burn` 函数回调返回 result_string（加密或签名时的 armored 字符串）和 result_buffer（只是原始二进制数据）。后者要么是 Node.js Buffer（如上所述），要么在浏览器中是 `kbpgp.Buffer`。

```javascript
kbpgp.burn(params, function(err, result_string, result_buffer) {
  console.log(result_buffer.toString('hex'));
  console.log(result_buffer.toString('base64'));
  // etc...
  // ...these work in both the browser and Node.js
});
```

#### 在浏览器中，使用 HTML5

如果你想在浏览器中支持文件处理，你可以使用 HTML5 `FileReader` 并将文件内容转换为 Buffer，就在客户端。根据浏览器的不同，你会有内存限制。

```javascript
var f = some_html_5_file_object;
var r = new FileReader();   // modern browsers have this
r.readAsBinaryString(f);
r.onloadend = function(file) {
  var buffer = kbpgp.Buffer.from(r.result);
  // ... now process it using kbpgp
};
```

### FAQ

#### 本文档缺少某些内容——我该如何______？

kbpgp 网站是全新的，我们才刚刚开始编写文档。请在 [GitHub issues](https://github.com/keybase/kbpgp/issues) 中告诉我们。

#### 你说的“专为并发设计”是什么意思？

加密是 CPU 密集型的。最糟糕的是 RSA 密钥对生成，此时我们要寻找巨大的素数。这加上 JavaScript 的单线程特性简直是一场噩梦。看看这个有趣的东西：

```javascript
weird_sum = function() {
  var x = 0;
  for (var i = 0; i < 10000000; i++) {
    x -= Math.cos(Math.PI)
  }
  return x;
};
console.log(weird_sum());
```

上述函数在浏览器中可能需要几秒钟，在此期间它将无响应——没有其他 JavaScript 可以运行，没有按钮或链接可以点击，什么都没有。它会暂停你美好的生活体验。在 Node.js 中，你的整个进程将锁定，你会去下载 Go。

浏览器中的一种解决方案是将此过程转移到 Web Worker。这通常有效，尽管 Web Worker 是新的并且有些错误（在撰写本文时，让 Chrome 崩溃并不难），而且它们有很高的开销。在 Node 方面，你可以运行一个单独的进程来执行数学运算，并向其发送 RPC。（旁注：无论如何这都是个好主意。）

无论你在哪里运行它，繁重的数学运算都可以考虑到单线程并发来编写。你只需要 (1) 分批工作，(2) 通过 `setTimeout` 或 `process.nextTick` 定期服从事件循环，以及 (3) 回调返回答案，而不是直接返回。一个简单的例子：

```javascript
var _batch = function(a, batch_size, stop_at, cb) {
  var b, i, sum, _i;
  b = Math.min(stop_at, a + batch_size);
  sum = 0;
  for (i = _i = a; a <= b ? _i < b : _i > b; i = a <= b ? ++_i : --_i) {
    sum -= Math.cos(Math.PI);
  }
  if ((a = b) === stop_at) {
    cb(sum);
  } else {
    setTimeout(function() {
      _batch(a, batch_size, stop_at, function(sub_sum) {
        cb(sum + sub_sum);
      });
    }, 0);
  }
};

var weird_sum = function(cb) {
  _batch(0, 100000, 10000000, cb);
};

weird_sum(function(sum) {
  console.log(sum);
});
```

编写这样的代码——通过回调返回答案——是具有传染性的。如果 foo 调用 bar，bar 回调返回答案，foo 不能直接返回该答案。它也必须回调。

所有 kbpgp 都是这样编写的，尽管比上面的例子稍微漂亮一点。此外，kbpgp 支持中止和进度钩子函数，不像上面的例子。总之，你可以在与其他代码相同的线程上运行 kbpgp，没有任何问题。

#### 为什么你们使用 CoffeeScript？或者更确切地说，IcedCoffeeScript？

我们认为 CoffeeScript 是对 JavaScript 的巨大改进，因为它可以编写更简洁、更易读的代码。至于 [IcedCoffeeScript](http://maxtaco.github.io/coffee-script/)，是我们写的！嗯，具体来说是 Max fork 了 CoffeeScript。IcedCoffeeScript 与 CoffeeScript 相同，但有两个新增功能（`await` 和 `defer`），使异步编程更加美好。请注意我们在上面的示例中完全没有 worker 函数，转换为 Iced：

```coffeescript
weird_sum = (cb) ->
  x = 0
  for i in [0...10000000]
    x -= Math.cos Math.PI
    if not (x % 10000)
      await setTimeout defer(), 0
  cb x
```

当然，作为我们构建过程的一部分，kbpgp 被编译为 JavaScript，因此你不需要使用 CoffeeScript 就可以使用它。

#### 为什么你们不直接在 Keybase 中使用 OpenPGP.js 或 Google 的 End-to-End？

在撰写本文时，Google 的 End-to-End 需要椭圆曲线密钥生成——这与最流行的 PGP 实现不兼容。kbpgp 可以生成和处理 RSA 和 EC 密钥，因此它旨在与 GPG 和其他 PGP 实现配合使用。

至于 OpenPGP.js，在 2013 年底，我们查看了 OpenPGP.js。不幸的是，当时我们看到了一些我们不喜欢的东西。这已在别处讨论过，Google 团队也对此发表了评论。我们没有审查 OpenPGP.js 的当前状态。

### 野外应用！

这些是使用 kbpgp 的社区项目。如果你做了一些很酷的事情（发送电子邮件至 `chris@keybase.io`），我们会添加你。Keybase 团队和 KBPGP 贡献者未审核且**不负责**以下项目。

- [OnlyKey WebCrypt](https://apps.crp.to/encrypt?type=e)，一个无服务器 Web 应用程序，与 [OnlyKey](https://crp.to/p/) 和 Keybase 集成，随时随地提供 PGP 加密。
- [Top Secret](https://playtopsecret.com/demo.html)，一款受斯诺登泄密事件启发的游戏。([Kickstarter](https://www.kickstarter.com/projects/1928653683/top-secret-a-game-about-the-snowden-leaks))
- [pgpkeygen.com](https://pgpkeygen.com/)，一个使用 kbpgp 的在线 PGP 密钥生成器。
- [fnContact.com/pgpkeys](https://fncontact.com/pgpkeys)，一个使用 kbpgp 的在线 PGP 密钥生成器。
- [PGP generator](https://thechiefmeat.github.io/pgp/)，一个用于浏览器中 PGP 的网站

----

我们的教程和示例才刚刚开始。如果缺少任何内容，请[在 GitHub 上](https://github.com/keybase/kbpgp)联系我们。
