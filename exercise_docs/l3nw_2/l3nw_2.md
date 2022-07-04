<!-- HEADER -->
[Previous](../l3nw_1/l3nw_1ans.md) << [Index](../index.md) >> [Next](../l3nw_2/l3nw_2ans.md)

---
<!-- /HEADER -->

<!-- TOC -->

- [L3NW-2 (問題編)](#l3nw-2-問題編)
  - [前置き](#前置き)
  - [構成図](#構成図)
  - [問題1](#問題1)
    - [(補足) 問題1の完了判定方法について](#補足-問題1の完了判定方法について)
  - [問題2](#問題2)

<!-- /TOC -->

# L3NW-2 (問題編)

## 前置き

前提

- [チュートリアル4](../tutorial_4/tutorial_4.md): L3 基礎
- [L3NW-1](../l3nw_1/l3nw_1.md)

この問題で知ってほしいこと :

- 静的経路設定・ルーティングの考え方
  * 複数のセグメントに接続するサーバでは、どのように経路設定をすればよいか? ("表/裏" など複数のセグメントにサーバ接続している構成でのネットワーク設定の考え方)
- ルーティング設定の不整合で起こるトラブル
  * ルータは独立してパケットの送付先を判断していること
  * 通信が複数のルータにまたがるとき、経路設定の不整合・それによる通信障害がおきうること

<details>

<summary>この問題で使用するコマンド :</summary>

* インタフェースの一覧表示・設定確認
  * IP アドレス一の確認
    * `ip addr show [dev インタフェース名]`
* ルーティングテーブルの確認
  * `ip route`
* L3 通信経路の確認
  * `traceroute 宛先IPアドレス`
* L3 の通信確認
  * `ping 宛先IPアドレス` (オプション `-c N` は送信するパケット数を指定します。)
* ルーティングテーブルの操作 (静的経路の追加・削除)
  * `ip route add 宛先ネットワーク via 中継先ルータ(nexthop)IPアドレス`
  * `ip route del 宛先ネットワーク`
  * デフォルトルートを設定する場合、宛先ネットワークアドレスとして `default` キーワードが使用可能 (例: `ip route add default via ...`)
* パケットキャプチャ (必要に応じて)
  * `tcpdump -l [-i インタフェース名]` : オプション `-l` がないとリアルタイムに表示されません。

</details>

## 構成図

図 1: l3nw_2 (`exercise/l3nw_2/l3nw_2.json`)

![Topology](topology.drawio.svg)

* Host.A は 3 つのネットワーク(サブネット)に接続されています。
* Router.A-E には静的経路の設定がすでに入っています。
  * :warning: **ルータ (Router.A-E) の設定を変更しないでください** : システム上はできてしまうので設定対象のノードを間違えないように注意してください。
* Server.A-E があります。
* :customs: Server.E について:
  * Server.E は外部(インターネット)にあるサーバという設定です。本来インターネット上のノードは IP アドレスを事前に指定できませんが、演習システム上設定が必要なので代表例としてアドレスをつけています。("inet", 203.0.113.0/24 というサブネットになっています)
  * インターネット上の任意のアドレス(外部の全て)を表現していることに注意してください。

## 問題1

* Host.A が、Server.A-E と通信できるように、Host.A に静的経路設定を追加してください。
* Host.A が、Server.A-E と通信可能にすることを考えると、一部 Server 側の静的経路設定が不足しています。Host.A と通信するための経路情報設定が不足しているサーバはどれでしょうか?
  * 足りない設定をそのサーバに追加して、Host.A と通信できるようにしてください。

### (補足) 問題1の完了判定方法について

Host.A および Server.A-E いずれかに実際に設定を追加して通信可能にしてください。その際、以下のコマンドで Host.A → Server.A-E の通信が可能になることを達成条件とします。

```bash
ha ping -c3 sa
ha ping -c3 sb
ha ping -c3 sc
ha ping -c3 sd
ha ping -c3 se
```

上記の達成条件をチェックするスクリプトが同梱されています。

(Shell ターミナル) l3nw_2 設定テスト実行

```bash
cd /exercise
./nw_test.sh l3nw_2
```

設定前は fail になるテストがあります。(設定投入前に確認してください。)

```text
root@nwtraining01:/exercise# ./nw_test.sh l3nw_2
FFFF..FFFFFFFFFFFF......

Failures/Skipped:

(省略)

Title: ping from ha to 203.0.113.117 will be SUCCESS
Command: ip netns exec ha ping -c3 203.0.113.117: exit-status:
Expected
    <int>: 2
to equal
    <int>: 0
Command: ip netns exec ha ping -c3 203.0.113.117: stdout: patterns not found: [/3 packets transmitted, 3 received/]

Total Duration: 2.084s
Count: 24, Failed: 16, Skipped: 0
```

* 実行時、最初に表示される `F`/`.` はテストのサマリです。(`F`: Failed, `.`: Success)
* その後表示される `Title` から始まる部分は各テストの詳細です。
  * `Title` : テストのタイトル
  * `Command` : テストで実行したコマンド
    * `exit-status: Expected xxx to equal yyy` : `Command` の終了ステータスが xxx だったが yyy になることが期待されている。
    * `stdout: patterns not found: zzz` : `Command` の標準出力にパターン zzz が含まれているか探したが見つからなかった。

全てのテストが成功すると以下のようになります。Failed が 0 になればこの問題は完了です。

なお、この問題で確認してほしいのは Host.A から各サーバ (Server.A-E) への通信ですが、デバッグのため中間経路に含まれるルータへの通信確認も行っています。例えば、Server.E に到達するためには、その前に必ず Router.E へ到達可能でなければならないので、Router.E への通信確認も含まれています。

```text
root@nwtraining01:/exercise# ./nw_test.sh l3nw_2 
........................

Total Duration: 2.195s
Count: 24, Failed: 0, Skipped: 0
```

## 問題2

問題 1 では Host.A を中心に考えていましたが、この問題ではサーバ間の通信を考えます。

以下のパターンで通信できますか? できる場合は経路を・できない場合はその理由を挙げてください。

|No.| ping                        | ping 成功? |
|---|-----------------------------|------------|
| 1 | `sb ping -c3 192.168.0.22`  | ? |
| 2 | `sc ping -c3 203.0.113.117` | ? |
| 3 | `sd ping -c3 192.168.0.30`  | ? |

通信経路についてはノード単位で構いません。たとえば Server.D は初期状態で Server.E (internet) と接続できます。その際の経路は、sd → rd → re → se です。

:bulb: これは、`traceroute` コマンドでも確認できます。(❶ sd → ❷ rd → ❸ re → ❹ se)

```text
mininet> ❶ sd traceroute se
traceroute to 203.0.113.117 (203.0.113.117), 30 hops max, 60 byte packets
 1 ❷ 192.168.0.21 (192.168.0.21)  0.280 ms  0.232 ms  0.221 ms
 2 ❸ 192.168.0.1 (192.168.0.1)  0.214 ms  0.182 ms  0.171 ms
 3 ❹ 203.0.113.117 (203.0.113.117)  0.161 ms  0.135 ms  0.122 ms
```

<!-- FOOTER -->

---

[Previous](../l3nw_1/l3nw_1ans.md) << [Index](../index.md) >> [Next](../l3nw_2/l3nw_2ans.md)
<!-- /FOOTER -->
