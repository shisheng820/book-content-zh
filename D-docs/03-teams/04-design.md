
# 团队高层设计

本文档提供了 Keybase 团队的高层描述，指定了应用程序、团队角色和团队结构。

## 团队和子团队

根团队是 Keybase 命名空间中的顶级标识符，它遵循与 Keybase 用户名相同的解析规则。因此，有效的根团队包括 `nike`、`google` 或 `friends_of_max`。这些名称对全世界都是可见的，所以如果你创建了团队 `lets_fire_bob`（让我们解雇鲍勃），全世界都会看到它，只是除非他们自己是团队成员，否则他们无法获得有关成员是谁的任何详细信息。

子团队嵌套在根团队之下。所以 `nike.hr`、`nike.hr.interns` 和 `nike.hr.interns.volleyball` 都是有效的子团队。对于非子团队成员的所有人来说，子团队的存在本身就是隐藏的。因此，如果你想创建团队 `lets_fire_bob.just_kidding_fire_bruce`（让我们解雇鲍勃.开玩笑的解雇布鲁斯），那么 Bruce 将无法知道他的末日到了。

正如我们将看到的，每个团队和子团队都有自己的签名链，该签名链直接插入 Keybase 全局树中。但是子团队在化名下存在于此树中，由其父团队指向。因此它们可以保持私有，但团队成员可以确定 Keybase 服务器没有对团队定义含糊其辞。

## 应用程序

[聊天](/blog/keybase-chat) 和 [KBFS](/docs/crypto/kbfs) 是我们最初在 Keybase 团队中支持的两个应用程序。在这两种情况下，团队都是可变的，并由名称唯一标识，而不必担心恶意服务器重新映射团队。

对于聊天，每个像 `nike.hr.interns.volleyball` 这样的团队都将拥有私人聊天，包含多个频道，并且团队的每个成员（无论其角色如何）都将拥有对聊天的完全访问权限。

对于 KBFS，团队共享将在诸如 `/keybse/team/nike` 和 `/keybase/team/nike.hr.interns.volleyball` 之类的路径下可用。那些拥有写入权限（或更高权限）的人将能够读取和写入团队，而那些只有读取权限的人将无法拥有写入权限。

目前，Keybase 不支持跨团队共享，如 `/keybase/team/nike,adidas`，因为这样做会向 `adidas` 透露 `nike` 的成员身份，反之亦然。

## 团队角色

*   **团队**是一组 keybase 用户，包括：**所有者 (owners)**、**管理员 (admins)**、**隐式管理员 (implicit admins)**、**读者 (readers)** 和 **作者 (writers)**。
*   **读者**可以读取团队的 KBFS 文件夹，并且可以读取和写入团队的聊天。
*   **作者**拥有读者的所有权限，但也可以写入团队的 KBFS 资源。
*   **管理员**可以向团队添加或删除管理员、读者和作者，并为团队建立子团队。管理员还可以停用团队，只要它不是根团队。
*   **隐式管理员**是父子团队的管理员，但不是该子团队的管理员。
*   所有显式管理员都拥有对其团队的读/写访问权限，并获得对服务器门控密钥的完全访问权限，这反过来允许访问 KBFS 和聊天数据。
*   尚未显式添加到子团队的子团队隐式管理员无法获得对该团队的服务器门控密钥的访问权限，因此无法访问 KBFS 和聊天数据。
*   因此，子团队可以避免所有成员都失去数据访问权限的危险情况。
*   但是 Keybase 仍然可以强制执行，例如，Campbell Soup Corp. 的系统管理员无法下载 C*O 团队文档。
*   **所有者**是根团队的管理员，此外还有权删除团队。

这里的加密机制是，对于团队需要的任何共享秘密团队密钥（用于聊天或 KBFS 或 Saltpack），最终使用的密钥是以下各项的异或：(1) 为所有用户的每用户密钥加密的共享密钥；(2) 仅在 ACL 允许的情况下才分发的服务器存储的密钥半部分。这种设置使服务器能够破坏用户解密其 KBFS 或聊天的尝试，但它无论如何都有这种能力，只需破坏所有密文即可。

用户所在的团队将需要轮换其共享的对称密钥，但这可以懒惰地发生（在下一次写入之前）并且不在关键路径上（参见 [级联惰性密钥轮换 (CLKR)](/docs/teams/clkr)）。

## 访问矩阵

上述属性总结在以下访问矩阵中：

<table class="access-matrix" id="main-table">
<tr>
	<th>角色</th>
	<th>所有者</th>
	<th>管理员</th>
	<th>隐式管理员</th>
	<th>作者</th>
	<th>读者</th>
</tr>
<tr>
	<td>添加/删除所有者</td>
	<td>1</td>
	<td>0</td>
	<td>0</td>
	<td>0</td>
	<td>0</td>
</tr>
<tr>
	<td>添加/删除读者、作者、管理员</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>0</td>
	<td>0</td>
</tr>
<tr>
	<td>写入 TLF 元数据</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>0</td>
</tr>
<tr>
	<td>读取 TLF 元数据</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
</tr>
<tr>
	<td>请求重新生成 TLF 元数据密钥</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
</tr>
<tr>
	<td>读取 KBFS 文件</td>
	<td>1</td>
	<td>1</td>
	<td>0.5</td>
	<td>1</td>
	<td>1</td>
	<td>隐式管理员被访问控制阻止</td>
</tr>
<tr>
	<td>写入 KBFS 文件</td>
	<td>1</td>
	<td>1</td>
	<td>0.5</td>
	<td>1</td>
	<td>0</td>
	<td>隐式管理员被访问控制阻止</td>
</tr>
<tr>
	<td>读取聊天</td>
	<td>1</td>
	<td>1</td>
	<td>0.5</td>
	<td>1</td>
	<td>1</td>
	<td>隐式管理员被访问控制阻止</td>
</tr>
<tr>
	<td>写入聊天</td>
	<td>1</td>
	<td>1</td>
	<td>0.5</td>
	<td>1</td>
	<td>1</td>
	<td>隐式管理员被访问控制阻止</td>
</tr>
<tr>
	<td>创建聊天频道</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>0.5</td>
	<td>读者被访问控制阻止</td>
</tr>
<tr>
	<td>创建当前团队的子团队</td>
	<td>1</td>
	<td>1</td>
	<td>1</td>
	<td>0</td>
	<td>0</td>
</tr>
<tr>
	<td>如果是根团队，可以删除团队</td>
	<td>1</td>
	<td>0</td>
	<td>N/A</td>
	<td>0</td>
	<td>0</td>
	<td>根团队（例如 nike）没有隐式管理员</td>
</tr>
<tr>
	<td>如果是子团队，可以删除团队</td>
	<td>N/A</td>
	<td>1</td>
	<td>1</td>
	<td>0</td>
	<td>0</td>
	<td>子团队（例如 nike.usa）不能有所有者</td>
</tr>
</table>

### 图例

<table class="access-matrix" id="legend">
<tr><td class="explicit">允许访问 (✓)</td></tr>
<tr><td class="implicit">通过服务器信任的访问控制拒绝访问 (👮)</td></tr>
<tr><td class="nada">通过密码学拒绝访问 (✗)</td></tr>
</table>

<script>
$(function() {
  $(".access-matrix td").filter(function() { return $(this).html() === "1" }).addClass('explicit').html("✓");
  $(".access-matrix td").filter(function() { return $(this).html() === "0" }).addClass('nada').html("✗");
  $(".access-matrix td").filter(function() { return $(this).html() === "0.5" }).addClass('implicit').html("👮");
  $(".access-matrix#main-table tr > td:first-child").addClass("right-label");
});
</script>
