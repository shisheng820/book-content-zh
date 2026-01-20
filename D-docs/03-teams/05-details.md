# 团队：命名、Merkle 树集成和签名链

## 命名、ID 和 Merkle 树

每个团队都有一个 16 字节的唯一标识符，该标识符在团队的生命周期内是不可变的。
对于根团队，标识符的前 15 个字节是团队名称的 SHA256 哈希的前 15 个字节，后面跟着字节 `0x24`。这意味着根团队永远不能重命名。

例如，以团队 `Keybase` 为例。在 Node 中运行以下 JavaScript：

```javascript
const crypto = require('crypto');
var team = "Keybase";
var lowered = team.toLowerCase()
var hashed = crypto.createHash('SHA256').update(lowered).digest();
var clamped = hashed.slice(0,15)
var suffixed = Buffer.concat([clamped, Buffer.from([0x24])])
var hexed = suffixed.toString('hex')
console.log(hexed);
```

输出字符串 `05327b776e5fbf5ee3d7a5905bff26`。实际上，根 `Keybase` 团队的团队 ID 是
`05327b776e5fbf5ee3d7a5905bff2624`，这在主 Merkle 树中是 [公开可见的](https://keybase.io/_/api/1.0/merkle/path.json?leaf_id=05327b776e5fbf5ee3d7a5905bff2624)。

当客户端创建新的 Keybase 子团队时，它们会生成一个随机的 15 字节值，然后附加一个 `0x25`
后缀来制作一个 ID。

子团队和根团队都有签名链，这些签名链按其 ID 索引插入到主 Merkle 树中。
对于根团队，任何外部观察者都可以在树中看到团队的存在，并且可以进一步观察团队是否更新。
但是，除非他们有权访问该团队，否则他们无法看到团队签名链中的实际链接。
对于子团队，任何观察者都可以在 Keybase Merkle 树中看到子团队 ID 的存在，以及它何时更新，
但他们无法仅根据 ID 知道子团队的名称或子团队的父级。

虽然这种结构很简单，但它有一个明显的缺点。外部观察者可能能够根据树中叶子的相关更改猜测团队的父级。
虽然 `adidas` 团队的成员无法知道像 `nike.hr`、`nike.hr.interns` 或 `nike.acquisitions.puma` 这样的团队名称，
但他们可以推断出 `nike` 子团队树的 **形状**，以及这些子团队何时更新。
我们认为这种轻微的数据泄露是值得的，因为它允许所有用户审计 Keybase 操作的完整性。

团队与普通用户一起存在于 Merkle 树中，但它们不会发生冲突，因为用户 ID 以后缀 `0x00` 或 `0x19` 结尾。
理论上允许一个名为 `acme` 的用户和一个名为 `acme` 的团队，因为它们将分别映射到 ID `822b33ad87c148a0a20a5ba7cd5ebc19` 和 `822b33ad87c148a0a20a5ba7cd5ebc24`。
但为了清晰和简单起见，我们目前不允许这种结构。
在未来的某个时候，这些限制可能会放宽。

## 团队签名链 (Team Sigchains)

像 Keybase 用户一样，Keybase 团队也有自己的“签名链”或“sigchains”。签名链是一个仅追加的数据结构，每当需要变动时就会追加。
用户在添加外部证明、添加或撤销设备、关注或取消关注朋友时会变动其身份。
团队在添加、移除、升级或降级成员，添加或重命名子团队，加密密钥轮换等情况下会变动其组成。
签名链链接的一般形状如 [Keybase 签名链 V2](/docs/teams/sigchain) 中所示，但 JSON 签名主体中新的 `team` 部分捕获了特定于团队的功能。
此外，所有团队签名链接都采用 [Keybase 签名链 V2](/docs/teams/sigchain) 格式。

### team.root

`team.root` 签名是新根团队的初始签名。所有根团队签名链必须以这样的签名开始。
以下是 `team.root` 链链接的示例片段：

```javascript
"team": {
	"id": "9b46c6085b3e5e48ec3829bcf46d7c24",
	"members": {
		"admin": [],
		"owner": [
			"93b82086be2f8e206cd6bbef8483b219"
		],
		"reader": [],
		"writer": []
	},
	"name": "6339c082",
	"per_team_key": {
		"encryption_kid": "0121385b48c13958e8eb474a97a80fd508560f26cdc2c184054d3837b22fb23be5470a",
		"generation": 1,
		"reverse_sig": "hKRib...",
		"signing_kid": "012091eaf617c0b0469b10465bc166744233d0540df8ef76d6078586fdffa8f9c3390a"
	}
},
"type": "team.root",
"version": 2
```

团队部分指定了团队名称、团队 ID（如上所述确定）、团队的初始成员以及团队的初始公钥。
与 [每用户密钥 (Per-User Keys)](/docs/teams/puk) 一样，使用每团队签名密钥对整个链链接计算反向签名。
有关团队密钥密码学细节的更完整描述，请参见下文。

团队角色列表使用常规 Keybase UID 指定。如果用户重置了他/她的账户，UID 的形式为 `<uid>%<seqno>`，
其中 `<seqno>` 是自用户重置以来用户的最早签名链序列号。

团队必须始终至少有一名所有者（当前用户），但团队的所有者可以在创建团队时指定额外的管理员、读者、作者和所有者。

### team.subteam_head

`team.subteam_head` 类似于 `team.root`，但代表子团队签名链的第一个链接。
此类链的示例片段如下所示：

```javascript
 "team": {
	"admin": {
		"seq_type": 3,
		"seqno": 1,
		"team_id": "7b392b1aaec8b189cfd14fa1a46c8225"
	},
	"id": "b55f84038205c958ee9ec9e87d9e5325",
	"members": {},
	"name": "nike.hr.interns.2019",
	"parent": {
		"id": "2698d3406bed19fa8f4b1463f66f3f25",
		"seq_type": 3,
		"seqno": 2
	},
	"per_team_key": {
		"encryption_kid": "0121b21a1b538cd562818f10f2d85c1c79fa29e6bbfbdd39d36efe180e857f2beb700a",
		"generation": 1,
		"reverse_sig": "g6Rib2...",
		"signing_kid": "012049819898a9b5c2d179626ba78544b065fecd38052567a32e4ddfc73f9825c3d10a"
	}
},
"type": "team.subteam_head",
```

像 `team.root` 链链接一样，`team.subteam_head` 链链接包含子团队名称、子团队 ID、初始成员列表和加密密钥。
它们有额外的子对象：

* `parent` 是指向授权此子团队创建的父团队签名链链接的指针；
* `admin` 是指向某个祖先团队签名链的指针，显示执行此操作的权力来源。
由于隐式管理员身份的递归性质，来自 `nike`、`nike.hr` 或 `nike.hr.interns` 的管理员可以创建子团队 `nike.hr.interns.2019`。
签名的 `admin` 部分确切地告诉此签名链的读者在哪里可以找到此签名用户执行此操作的授权。

### team.new_subteam

当创建一个新的子团队时，会写入两个链接。创建者将 `team.subteam_head` 链接写入新子团队的头部，
并将 `team.new_subteam` 链接写入父团队。作为文件系统，父级控制所有子级写入的命名空间。
因此，写入父级强制执行命名空间的可序列化和一致性。这是一个示例片段：

```javascript
 "team": {
	"admin": {
		"seq_type": 3,
		"seqno": 1,
		"team_id": "60ca2fa24b1097a3f08c1d00fe429724"
	},
	"id": "2698d3406bed19fa8f4b1463f66f3f25",
	"subteam": {
		"id": "b55f84038205c958ee9ec9e87d9e5325",
		"name": "nike.hr.interns.2019"
	}
},
"type": "team.new_subteam",
```

服务器和客户端都应检查每个 `team.new_subteam` 链接是否有对应的 `team.subteam_head` 新子团队，
并且序列号和哈希是否正确对齐。这里 `team.id` 是父团队的 ID，`team.subteam.id` 是新子团队的 ID。

### team.change_membership

`team.change_membership` 链接允许管理员更改团队或子团队的成员资格。
这是一个示例片段：

```javascript
"team": {
	"admin": {
		"seq_type": 3,
		"seqno": 1,
		"team_id": "1439170a29f084cf447426cb851bd924"
	},
	"id": "1439170a29f084cf447426cb851bd924",
	"members": {
		"none": [
			"6bbc642b05c079918f12bb2921713319"
		],
		"writer": [
			"93b82086be2f8e206cd6bbef8483b219"
		],
		"reader" : [
			"00aa4b027e3e132f918d3205d6e96819"
		]
	},
	"per_team_key": {
		"encryption_kid": "01218ba2aa312e74a292ce6e8136fa8343bd5146acbb5b60e30ad3d29e2ae67bd53c0a",
        "generation": 2,
        "reverse_sig": "g6Rib...","
        "signing_kid": "0120026dc6e1b7d514474c192d7cf0cd6c6e65312d77227117f0779fb7b5aa23207f0a"
    }
},
"type": "team.change_membership",
```

与 `team.subteam_head` 链接一样，这些链接必须明确指定管理员的权限来自何处。
就像 `team.root` 或 `team.subteam_head` 链接一样，`team.change_memberhip` 链接有一个 `members` 子对象来描述更改。
通过在 `none` 列表中包含用户 ID，管理员将用户从群组中移除。
管理员可以通过在不同的角色列表中指定其 UID 来升级或降级现有用户（因为用户在团队中一次只能担任一个角色）。
在上面的示例中，如果用户 `93b82086be2f8e206cd6bbef8483b219` 之前是该组的管理员，
将其指定为 `writer` 将被视为角色降级。管理员可以在此处通过将用户的 UID 包含在适当的列表中来添加新用户。
因此，例如，如果用户 `00aa4b027e3e132f918d3205d6e96819` 之前不是该团队的一部分，在此更新后他们现在是团队中的读者。

请注意，当用户从团队中移除时，执行更改的管理员还应轮换团队的密钥。
她可以通过指定 `per_team_key` 部分并为其余成员上传加密密钥来做到这一点。

### team.rotate_key

`team.rotate_key` 指定团队的加密共享密钥已轮换，但成员资格没有任何相应的更改。
例如，当团队成员重置其设备之一时可能需要这样做（请参阅 [级联惰性密钥轮换 (CLKR)](/docs/teams/clkr)）。这是一个示例片段：

```javascript
"team": {
	"id": "fa6d7ff1d4bab8c204753202134ad724",
	"per_team_key": {
		"encryption_kid": "01218ba2aa312e74a292ce6e8136fa8343bd5146acbb5b60e30ad3d29e2ae67bd53c0a",
        "generation": 2,
        "reverse_sig": "g6Rib...","
        "signing_kid": "0120026dc6e1b7d514474c192d7cf0cd6c6e65312d77227117f0779fb7b5aa23207f0a"
    }
},
"type": "team.rotate_key",
```

`per_team_key` 子对象与团队（或子团队）创建中的一样，但这里的关键区别是 `generation` 设置为大于 `1` 的数字，因为密钥正在轮换。

### team.leave

当非管理员想要离开团队时，他们会签署一份“离开”声明，大意如下：

```javascript
"team": {
	"id": "54339639186bc64e9030affed0d39a24"
},
"type": "team.leave",
```

团队读者和作者可以发表 `team.leave` 声明。管理员不允许；他们需要先将自己降级为读者或作者。

### team.rename_subteam

与根团队不同，子团队可以重命名，但前提是它们在团队树中的位置不改变。
例如，`nike.hr` 可以重命名为 `nike.human_resources`，但不能重命名为 `nike.subdivisions.hr`。
重命名将产生级联效应。在上面的示例中，`nike.hr.interns` 将被重命名为 `nike.human_resources.interns`。
这是此类链接的示例，它位于被重命名团队的 *父团队* 中。
因此，例如，上述重命名将发生在 `nike` 的团队链中，以便父级可以序列化对其命名空间的所有更改，而不必担心更新冲突。

这是一个示例：

```javascript
"team" : {
	"admin": {
		"seq_type": 3,
		"seqno": 1,
		"team_id": "fb0ef07743d99b130f5c69cbb8991624"
	},
	"id": "fb0ef07743d99b130f5c69cbb8991624",
	"subteam": {
		"id": "18c1463be9524a2d555e9c1501a82125",
		"name": "adidas.omg"
	}
 },
 "type" : "team.rename_subteam"

```

在这里，`team.subteam.name` 指定了团队的新名称。

### team.reaname_up_pointer

与 `team.new_subteam` 头部和 `team.subteam_head` 一样，每当团队的子团队命名空间发生更改时，
我们都会对父链和子链进行更新。因此，`adidas` 中的上述 `team.rename_subteam` 更新在 `adidas.omg` 的链中有一个伴随的 `rename_up_pointer` 链接。
示例如下：

```javascript
{
	"admin": {
		"seq_type": 3,
		"seqno": 1,
		"team_id": "fb0ef07743d99b130f5c69cbb8991624"
	},
	"id": "18c1463be9524a2d555e9c1501a82125",
	"name": "adidas.omg",
	"parent": {
		"id": "fb0ef07743d99b130f5c69cbb8991624",
		"seqno": 3,
		"seq_type": 3
	}
},
"type" : "team.rename_up_pointer"
```

### team.invite

管理员可以邀请非 Keybase 用户的成员加入团队。邀请可以通过社交媒体句柄或电子邮件地址进行引用。
在前一种情况下，当用户注册时，管理员可以在为用户提供团队密钥之前检查社交媒体证明是否令人满意。
在基于 `email` 的邀请的情况下，管理员必须相信 Keybase 对此证明的合法性。
没有打开电子邮件邀请的管理员将永远不会通过此服务器信任的 TOFU 系统重新生成密钥，因此它是严格选择加入的。

这是一个示例片段：

```javascript
"team" : {
	"id": "57a7fffc8799ddafe1859c96cc67d924",
	"invites": {
		"admin": [
			{
				"id": "243af3d8b33d170fec892218ed167a27",
				"name": "u_be6ef086a4a5",
				"type": "twitter"
			}
		],
		"cancel": [ "117b4f1d1048042cb67e204c84d07927" ],
		"reader": [
			{
				"id": "752d07d2c3b316105dcea2d983fffe27",
				"name": "u_be6ef086a4a5",
				"type": "reddit"
			}
		],
		"writer": [
			{
				"id": "54eafff3400b5bcd8b40bff3d225ab27",
				"name": "max+be6ef086a4a5@keyba.se",
				"type": "email"
			},
			{
				"id": "868882ad389a3023e810c376034b9d27",
				"name": "l52701844",
				"type": "keybase"
			}
		]
	}
},
"type" : "team.invite"
```

还有一些细节需要指出。首先，我们可以取消以前发出的邀请，如：`"cancel": [ "117b4f1d1048042cb67e204c84d07927" ]` 中所示。
其次，这里有一个有趣的“keybase”邀请概念。这里发生的事情是，用户 `l52701844` 是 Keybase 用户，
但没有 [每用户密钥 (Per-User Keys)](/docs/teams/puk)。他们必须先解决这种情况，一旦建立了自己的 PUK，
团队管理员就可以过来为该用户重新生成团队密钥。它与站外邀请共享很多机制，以至于我们将它实现为一种有趣的邀请。

管理员或所有者必须发出邀请。一旦用户注册并建立了 PUK，任何管理员都可以通过为用户生成团队密钥来完成闭环。
有关 Keybase 服务器如何协调此后台密钥生成操作的更多信息，请参见 [级联惰性密钥轮换 (CLKR)](/docs/teams/clkr)。

### team.delete_root

所有者可以删除根团队。此操作不可逆，并且永久删除团队：

```javascript
"team": {
	"id": "254066fbfdcf55d43e9f7be763793a24"
},
"type": "team.delete_root"
```

### team.delete_subteam

子团队管理员（隐式或显式）可以删除子团队，释放命名空间中的名称以便将来可能重新创建。
例如，在下面的 `adidas` 父链中：

```javascript
"team": {
	"admin": {
		"seq_type": 3,
		"seqno": 1,
		"team_id": "2463dcf9117ddba832bb622199fedd24"
	},
	"id": "2463dcf9117ddba832bb622199fedd24",
	"subteam": {
		"id": "617627599eba38e2aed1b9a1df8eea25",
		"name": "adidas.hr"
	}
},
"type": "team.delete_subteam",
```

### team.delete_up_pointer

`team.delete_up_pointer` 伴随上面的 `team.delete_subteam`。例如：

```javascript
"team": {
	"admin": {
		"seq_type": 3,
		"seqno": 1,
		"team_id": "2463dcf9117ddba832bb622199fedd24"
	},
	"id": "617627599eba38e2aed1b9a1df8eea25",
	"name": "t_cdd8bb5c.hr",
	"parent": {
		"id": "2463dcf9117ddba832bb622199fedd24",
		"seq_type": 3,
		"seqno": 3
	}
},
"type": "team.delete_up_pointer",
```

## POST 端点和参数

在变动团队时，用户将上述形式的签名发布到 `/_/api/1.0/sig/multi.json` 端点。
多个签名可以（并且通常需要）在一个 HTTP post 中发布。
例如，重命名和子团队删除操作需要同时变动多个团队签名链，并在服务器上的单个数据库事务中执行。

涉及这些 post 的一些相关字段包括：

* `per_team_key` — 为团队成员的 PUK 加密的新团队密钥，使用 NaCl 的 DH 原语
* `downgrade_lease_id` — 安全移除权限所需的预先建立的租约，确保没有竞争操作同时尝试使用该权限。
请参阅 [降级租约 (Downgrade Leases)](/docs/teams/downgrade-leases)。
* `implicit_team_keys` — 像 `per_team_key`，但是是针对正在操作的团队的 *子团队* 的 DH 盒子。
当用户被提升为团队 `T` 的管理员，因此需要访问 `T` 的所有传递子团队时需要。

## GET 端点

团队用户可以通过 `/_/api/1.0/team/get.json` 端点加载团队签名链，该端点采用各种参数。
服务器将返回团队签名链中的链接，以及随附的团队密钥加密。
请注意，如果非管理员加载团队，某些链接可能显示为“存根 (stubbed)”，意味着将返回其外部内容，但省略其内部内容。
此功能允许，例如，`nike` 的管理员对 `nike.interns` 的成员隐藏 `nike.merger_with_puma` 子团队的存在，
等等，方法是隐藏 `team.rename_subteam` 链接的内容。
但是，团队的读者仍然可以重建完整的签名链，而不必担心服务器篡改，因为外部链接包含序列号、先前的哈希和链接类型。
