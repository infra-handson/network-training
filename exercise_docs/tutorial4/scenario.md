<!-- HEADER -->
[Previous](../tutorial3/scenario.md) << [Index](../index.md) >> [Next](../tutorial5/scenario.md)

---
<!-- /HEADER -->

# チュートリアル4

## このチュートリアルの目的

ネットワーク知識の理解

* 複数の L2 セグメントの動作(VLAN) : 1 つのスイッチを使って複数の "部屋" を作ってみる
  * ブロードキャストドメインの分割とはなにか? (ARP の見え方などの違い)
- VLAN によるブロードキャストドメインの分割
- VLAN で使用するポートの種類と役割
  - trunk port
  - access port
- Linux サブインタフェースと VLAN

## VLAN (Virtual LAN)

古典的な Ethernet (L2 ネットワーク) は、[チュートリアル 2](../tutorial2/scenario.md)・[チュートリアル 3](../tutorial3/scenario.md) のように 1-switch : 1-L2 セグメントでした。このようにネットワーク機器と L2 セグメントが 1:1 に結びついてしまうと、セグメントを増やすたびに、そのセグメント用の機器を増やす (買い足す) ことになります。そうなってしまうと、ネットワークの拡張性・柔軟性・リソースの利用効率などの面で対応が難しくなります。そのため、1 つのネットワーク機器に複数の L2 セグメントを実現するための機能 : **VLAN** が考えられました。VLAN は **IEEE 802.1Q** という規格で標準化されており、多くの機器で共通して使用できます。

> [!NOTE]
> VLAN を実現するためのプロトコルは IEEE 802.1Q 以外にもありますが、802.1Q 以外を使うことはまずありません。

VLAN は 1 つの物理リソースを複数個の論理リソースに見せるタイプの仮想化技術です。そのメリットは、同じタイプの仮想化技術 (1→複数) である仮想マシン (VM, Virtual Machine) やコンテナを使うメリットに似ています。アプリケーションを動かす際、VM を使用することで、1 つのサーバリソースを複数の OS (その上のアプリケーション) で共有できます。これによって、大きな物理リソース (サーバが持つ計算機資源) を複数の OS/アプリケーションで共有したり配分を変えるなど、リソース利用率やシステムの拡張性・柔軟性が向上しました。VLAN も同様で、物理的なネットワーク(機器)資源を複数の L2 セグメントで共有し、利用効率・拡張性・柔軟性を向上させるために使われています。

## VLANによるブロードキャストドメインの分割

チュートリアル 4 のネットワーク (4a) を起動します。

```sh
cd /exercise
./nw_training.py tutorial4/scenario_a.json
```

起動したら Mininet CLI で `nodes`, `links`, `net` を実行し、図のようなトポロジになっていることを確認してください。

![Topology A](topology_a.drawio.svg)

* 1 台のスイッチ (Switch.1) があります。
* 4 台のホスト (Host.A-D) があり、Switch.1 に接続しています。
  * 4 台とも、同じサブネット 192.168.0.0/24 の IP アドレスを持っています。
  * Host.C/D は同じ IP アドレスを持っています (IP アドレス重複)。

このネットワークは、Switch.1 の設定 (スイッチの「中身」)を除けば、[チュートリアル 3](../tutorial3/scenario.md) で使用したネットワークから Switch.2 を外したものと同じです。VLAN を使うと、L2 セグメントとノード/インタフェースの対応関係を 1:1 ではなく N:1 にできます。チュートリアル 4a ネットワークでは、チュートリアル 3 ネットワークのセグメントを 2 つに分割して、重複する IP アドレスを持つノードとの通信がどう変化するかを見てみます。

### 初期状態の確認

各ノードの IP アドレス・MAC アドレスが[チュートリアル 3](../tutorial3/scenario.md) と同じになっていることを確認してください。
* :customs: チュートリアル 3 の演習ネットワークでは表のように MAC アドレスを設定して固定しています。

```sh
# Host.A
ha ip -4 addr show dev ha-eth0  # L3アドレス: IP アドレスの確認
ha ip link show dev ha-eth0     # L2アドレス: MAC アドレスの確認
# Host.B
hb ip -4 addr show dev hb-eth0
hb ip link show dev hb-eth0
# Host.C
hc ip -4 addr show dev hc-eth0
hc ip link show dev hc-eth0
# Host.D
hd ip -4 addr show dev hd-eth0
hd ip link show dev hd-eth0
```

| Node   |Interface| IP address  | MAC address       |
|--------|---------|-------------|-------------------|
|Host.A  | ha-eth0 |192.168.0.1  |`00:00:5e:00:53:0a`|
|Host.B  | hb-eth0 |192.168.0.2  |`00:00:5e:00:53:0b`|
|Host.C  | hc-eth0 |192.168.0.3 (重複) |`00:00:5e:00:53:0c`|
|Host.D  | hc-eth0 |192.168.0.3 (重複) |`00:00:5e:00:53:0d`|

### スイッチの設定を確認する

(Shell ターミナル) Switch.1 の設定情報を確認します

```sh
ovs-vsctl show
```
```text
root@nwtraining01:/# ovs-vsctl show
83c670f3-306d-4f3f-be2f-a8f5d0c461ed
    Bridge sw1
        fail_mode: standalone
        Port sw1-eth2
            tag: 20
            Interface sw1-eth2
        Port sw1-eth3
            tag: 10
            Interface sw1-eth3
        Port sw1
            Interface sw1
                type: internal
        Port sw1-eth4
            tag: 20
            Interface sw1-eth4
        Port sw1-eth1
            tag: 10
            Interface sw1-eth1
    ovs_version: "2.13.0"
```

[チュートリアル 3](../tutorial3/scenario.md) のときにはなかった `tag` という設定が追加されていることがわかります。この `tag` は **VLAN ID** と呼ばれます。L2 セグメント (ブロードキャストドメイン) を識別するための 12bit の整数 (0/4095 を除いた 1-4094 の範囲) が使用できます。このスイッチでは、VLAN ID 10, 20 の 2 つの L2 セグメントがあることになります (各セグメントを VLAN10, VLAN20 と呼びます)。

スイッチの `tag` を見ると、ポート eth1/eth3 は VLAN10 に、eth2/eth4 は VLAN20 に割り当てられています。
これによって、各ポートに入ってきたパケットが指定された VLAN ID の L2 セグメントにマップされていることになります。つまり、Switch.1 は 1-L3 サブネット : 2-L2 セグメントにマッピングされています。IP アドレスだけを見ると同一の "部屋" にいるように見えますが、実は異なる "部屋" (ブロードキャストドメイン) にマップされています。実際に動作を確認してみましょう。

### ノード間通信確認

IP アドレスが重複している Host.C/D の前に、まず Host.A から Host.B の通信が可能かどうかを試してみます。

(Shell ターミナル) パケットキャプチャ@Host.A

```text
ip netns exec ha tcpdump -l
```
```text
root@nwtraining01:/# ip netns exec ha tcpdump -l
...
```

(Mininet ターミナル) Host.A → Host.B 通信確認

```sh
ha ping -c3 192.168.0.2
ha ip neigh
```
```text
mininet> ha ping -c3 192.168.0.2
PING 192.168.0.2 (192.168.0.2) 56(84) bytes of data.
From 192.168.0.1 icmp_seq=1 Destination Host Unreachable
From 192.168.0.1 icmp_seq=2 Destination Host Unreachable
From 192.168.0.1 icmp_seq=3 Destination Host Unreachable

--- 192.168.0.2 ping statistics ---
3 packets transmitted, 0 received, +3 errors, 100% packet loss, time 2028ms
mininet> 
mininet> ha ip neigh
192.168.0.2 dev ha-eth0  ❶FAILED
```

Host.A, Host.B は、同一サブネットに属する IP アドレスを持っていますが、通信できませんでした。Host.A の ARP テーブルを見ると、192.168.0.2 (Host.B) の MAC アドレスが解決できていません。❶ `FAILED` は ARP request に対する応答がなかったことを示しています。パケットキャプチャを見ると、Host.A から ARP request を送信していますがどこからも応答がありません。

```text
01:36:54.874167 ARP, Request who-has 192.168.0.2 tell 192.168.0.1, length 28
01:36:55.898834 ARP, Request who-has 192.168.0.2 tell 192.168.0.1, length 28
01:36:56.928529 ARP, Request who-has 192.168.0.2 tell 192.168.0.1, length 28
```

VLAN によって L2 セグメント = ブロードキャストドメインが分割されているため、ARP request (ブロードキャスト) が Host.B に届いていません。結果として Host.A/B は通信できません (L2 = "メディア" がつながっていない状態)。

### ノード間通信確認 (IPアドレス重複)

次に、IP アドレスが重複している Host.C/D に対しての通信確認をしてみます。Host.C/D どちらと通信してるかをパケットキャプチャして確認してみましょう。


(Mininet ターミナル) Host.A → 192.168.0.3 (Host.C or D)

```sh
# ARP テーブルに 192.168.0.3 のエントリがあったら消しておく
ha ip neigh flush to 192.168.0.3
ha ping -c3 192.168.0.3
```

このときのパケットキャプチャの様子 @Host.A

```text
...

01:41:37.022937 ❶ARP, Request who-has 192.168.0.3 tell 192.168.0.1, length 28
01:41:37.023190 ❷ARP, Reply 192.168.0.3 is-at 00:00:5e:00:53:0c (oui IANA), length 28
01:41:37.023212 IP 192.168.0.1 > 192.168.0.3: ICMP echo request, id 1777, seq 1, length 64
01:41:37.023357 IP 192.168.0.3 > 192.168.0.1: ICMP echo reply, id 1777, seq 1, length 64
01:41:38.035289 IP 192.168.0.1 > 192.168.0.3: ICMP echo request, id 1777, seq 2, length 64
01:41:38.035320 IP 192.168.0.3 > 192.168.0.1: ICMP echo reply, id 1777, seq 2, length 64
01:41:39.058996 IP 192.168.0.1 > 192.168.0.3: ICMP echo request, id 1777, seq 3, length 64
01:41:39.059060 IP 192.168.0.3 > 192.168.0.1: ICMP echo reply, id 1777, seq 3, length 64
...
```

[チュートリアル 3](../tutorial3/scenario.md) で同一 L2 セグメント上の重複する IP アドレスがある場合の動作を思い出してください。重複している IP アドレスへの通信確認をすると、1 回の ARP Request に対して 2 個の応答が返ってきていました。ここでは 1 回の ARP Request ❶ に対して 1 個の応答 ❷ が返ってきており、応答した 1 ノード (host.C) とだけ通信しています。

IP アドレスが重複しているもう片方のノード (Host.D) → Host.A への通信を試してみましょう。チュートリアル 3 ではこれによって Host.A 側の ARP table で 192.168.0.3 に対応する MAC アドレスが書き換わっていました。

```sh
hd ping -c3 ha
```
```text
mininet> hd ping -c3 ha
PING 192.168.0.1 (192.168.0.1) 56(84) bytes of data.
From 192.168.0.3 icmp_seq=1 Destination Host Unreachable
From 192.168.0.3 icmp_seq=2 Destination Host Unreachable
From 192.168.0.3 icmp_seq=3 Destination Host Unreachable

--- 192.168.0.1 ping statistics ---
3 packets transmitted, 0 received, +3 errors, 100% packet loss, time 2029ms
pipe 3
mininet> hd ip neigh
192.168.0.1 dev hd-eth0  ❸FAILED
```

Host.D から Host.A への通信はできませんでした。そもそも ARP による IP/MAC アドレスの解決ができていません (❸)。また、Host.A のパケットキャプチャを見ると、Host.D からの ARP request がそもそも届いていないことがわかります。

このように、各ノードについて ping/arp を確認すると、次の表のようになります。

|from / to| A | B | C | D |
|---------|---|---|---|---|
|Host.A   |   | x |ok | x |
|Host.B   | x |   | x |ok |
|Host.C   |ok | x |   | x |
|Host.D   | x |ok | x |   |

チュートリアル 4a ネットワークでは、スイッチによって L2 セグメント (ブロードキャストドメイン) が分断されています。Host.A-D の全てのノードは L3 (IP) の観点では 1 つのサブネットにいるように見えます。しかし、L2 (ethernet) の観点からは 2 つの独立したセグメントに分割されおり、Host.A-C, Host.B-D のペアに分割されています。これは、同じ "住所" が異なる "部屋" に割り当てられている状態です。

### スイッチL2テーブル確認

VLAN によるブロードキャストドメインの分割はスイッチ (Switch.1) で実現されています。
Switch.1 の MAC アドレステーブルを確認してみましょう。

```sh
# OVS ポート番号/インタフェース名の対応確認
sh ovs-ofctl show sw1 | grep sw1-eth
# MAC アドレステーブルの表示
sh ovs-appctl fdb/show sw1
```
```text
mininet> sh ovs-ofctl show sw1 | grep sw1-eth
 1(sw1-eth1): addr:3a:16:f2:ec:0a:f6
 2(sw1-eth2): addr:0e:f6:69:9d:6a:96
 3(sw1-eth3): addr:4a:fb:99:0b:25:a4
 4(sw1-eth4): addr:c6:a6:17:1a:17:a4
mininet> 
mininet> sh ovs-appctl fdb/show sw1
 port  VLAN  MAC                Age
    2    20  00:00:5e:00:53:0b  105
    3    10  00:00:5e:00:53:0c   89
    1    10  00:00:5e:00:53:0a   56
    4    20  00:00:5e:00:53:0d   56
mininet> 
```

MAC アドレステーブルの `VLAN` 列に注目してください。[チュートリアル 2](../tutorial2/scenario.md): OVS デフォルト設定では VLAN 列はすべて `0` になっていました。デフォルトでは全てのポートが VLAN 0 になっています。言い換えれば、OVS がデフォルトで持つ L2 ドメイン (ブロードキャストドメイン) は VLAN ID 0 として識別されています。

見てきたように、VLAN ID によって L2 ドメインが分離されますが、これは MAC アドレステーブルで同一 VLAN ID をもつテーブルエントリだけを検索対象にすることで動作しています。どのパケットがどの VLAN に紐付いているのかは、パケットに追加される **VLAN ヘッダ** ・ポートで設定する VLAN ID によって決まります。

## VLAN で使用するポートの種類と役割

VLAN をつくることで、1 つのスイッチに複数の L2 セグメントを作れることがわかりました。では、スイッチ間、スイッチ - ノード間を接続する場合はどのような構成になるでしょうか? L2 セグメント (VLAN) を増やすごとにポートを用意する必要があると、面倒ですしコストがかかってしまいます ([L2NW-2](../l2nw2/question.md) で具体的に扱います)。

複数デバイスをつないだ際、L2 セグメント数が増えたとしてもなるべく物理的な構造を変えずにすませる方法が必要になります。複数のデバイスをつなぐ際に、リンク・インタフェース・ノードの中でどのように複数の L2 セグメントを扱うことができるかを見ていきます。

### 演習ネットワークの切替

(Mininet ターミナル) 演習ネットワークを切り替えます

チュートリアル 4a のネットワークを実行している場合は終了します。

```text
mininet> exit
```

チュートリアル 4b のネットワークを起動します。

```sh
cd /exercise
./nw_training.py tutorial4/scenario_b.json
```

起動したら Mininet CLI で `nodes`, `links`, `net` を実行し、図のようなトポロジになっていることを確認してください。

![Topology B](topology_b.drawio.svg)

* 2 台のスイッチ (Switch.1/2) があります。
* 3 台のホストがあり、Host.A は Switch.1 と、Host.B/C は Switch.2 と接続されています。
* どちらのスイッチにも 2 つの VLAN (VLAN10, VLAN20) があるようです。

Switch.2、Host.B/C の接続はこれまで見てきた VLAN 接続と同様に見えます。問題は Switch.1-2 間の接続、Switch.1-Host.A 間の接続です。それぞれ順に見ていきます。

### スイッチの設定を確認する

(Shell ターミナル) スイッチ設定情報確認

```sh
ovs-vsctl show
```
```text
root@nwtraining01:/# ovs-vsctl show
83c670f3-306d-4f3f-be2f-a8f5d0c461ed
    Bridge sw2
        fail_mode: standalone
        Port sw2
            Interface sw2
                type: internal
        Port sw2-eth1
            tag: 10
            Interface sw2-eth1
        Port sw2-eth2
            tag: 20
            Interface sw2-eth2
        Port sw2-eth0
            ❶trunks: [10, 20]
            Interface sw2-eth0
    Bridge sw1
        fail_mode: standalone
        Port sw1-eth1
            ❶trunks: [10, 20]
            Interface sw1-eth1
        Port sw1-eth0
            ❶trunks: [10, 20]
            Interface sw1-eth0
        Port sw1
            Interface sw1
                type: internal
    ovs_version: "2.13.0"
```

Host.A-Switch.1 間, Switch.1-2 間のポートについて、❶`trunks: [10, 20]` という設定が入っていることがわかります。

* これは、1 つのポートに対して複数の VLAN をマップしていることを示しています。
  * パケット的には、このポートで入出力されるパケットには VLAN ID を含むヘッダ(タグ)が追加されます。
  * このように 1 port - N vlan でマップされたポートを **VLAN trunk port** と呼びます。

### ホスト側トランクポート設定確認

Switch.1-2 間では、1 つのリンクに VLAN 10/20 のパケットが流れています。では Switch.1-Host.A 間ではどうでしょうか? Switch.1 の Host.A 接続ポートは Switch.1-2 間と同じ trunk port 設定です。

(Mininet ターミナル) Host.A-C ポート設定確認

```sh
# Host.A ... すべてのインタフェース情報を確認する
ha ip link show
ha ip -4 addr show
# Host.B
hb ip -4 addr show dev hb-eth0
hb ip link show dev hb-eth0
# Host.C
hc ip -4 addr show dev hc-eth0
hc ip link show dev hc-eth0
```
```text
mininet> ha ip link show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: ❶ha-eth0@if129: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 00:00:5e:00:53:0a brd ff:ff:ff:ff:ff:ff link-netnsid 0
3: ❷ha-eth0.10@ha-eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 00:00:5e:00:53:a1 brd ff:ff:ff:ff:ff:ff
4: ❸ha-eth0.20@ha-eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 00:00:5e:00:53:a2 brd ff:ff:ff:ff:ff:ff
mininet> 
mininet> ha ip -4 addr show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
3: ❷ha-eth0.10@ha-eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    inet 192.168.0.1/24 scope global ha-eth0.10
       valid_lft forever preferred_lft forever
4: ❸ha-eth0.20@ha-eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    inet 172.16.0.1/24 scope global ha-eth0.20
       valid_lft forever preferred_lft forever
```

| Node   | Interface    | IP address | MAC address       |
|--------|--------------|------------|-------------------|
|Host.A  | ❶ha-eth0    | なし       |`00:00:5e:00:53:0a`|
|Host.A  | ❷ha-eth0.10 |192.168.0.1 |`00:00:5e:00:53:a1`|
|Host.A  | ❸ha-eth0.20 |172.16.0.1  |`00:00:5e:00:53:a2`|
|Host.B  | hb-eth0      |192.168.0.2 |`00:00:5e:00:53:0b`|
|Host.C  | hc-eth0      |172.16.0.2  |`00:00:5e:00:53:0c`|

ha-eth0 について以下のようになっています。

* ❶ ha-eth0 (物理ポート)
* ❷ ha-eth0.10: 192.168.0.0/24 サブネット (VLAN10) のアドレスを持つ
* ❸ ha-eth0.20: 172.16.0.0/24 サブネット (VLAN20) のアドレスを持つ

これは Linux で 1 つの物理ポートに複数の IP アドレスを設定する際に使用される機能で、**サブインタフェース** と呼ばれます。
Host.A はこのサブインタフェースを使って trunk port を実現しています。そのため、Switch.1-2 間と同じ形で Switch.1-Host.A 間を接続できています。
(サブインタフェースの技術的な詳細については [補足: サブインタフェースについて](#%E8%A3%9C%E8%B6%B3-%E3%82%B5%E3%83%96%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%95%E3%82%A7%E3%83%BC%E3%82%B9%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6) を参照してください。)

### ノード間通信確認

Host.A → Host.B/C に対して通信できるかどうかを見てみます。

(Mininet ターミナル) Host.A → Host.B/C

```sh
ha ping -c3 hb
ha ping -c3 hc
```

どちらも成功します。Host.A の ARP テーブルで、Host.B/C の送信先が対応するサブインタフェースになっていることを確認してください。

```sh
ha ip neigh
```
```text
mininet> ha ip neigh
172.16.0.2 dev ha-eth0.20 lladdr 00:00:5e:00:53:0c REACHABLE
192.168.0.2 dev ha-eth0.10 lladdr 00:00:5e:00:53:0b STALE
```

逆方向 (Host.B/C → Host.A) も見てみます。

```sh
hb ping -c1 ha
hc ping -c1 ha
```
```text
mininet> hb ping -c1 ha
ping: ha: Temporary failure in name resolution
mininet> hc ping -c1 ha
ping: ha: Temporary failure in name resolution
```

:customs: Mininet CLI でコマンド中にノード名を指定した場合の動作について :

* ping 等コマンドの引数に演習ネットワーク中で作っているノード名を使うと、(Mininet が) そのノード名を IP アドレスに置き換えてコマンドを実行します。
* Host.B/C のように 1 つのノードが 1 つの IP アドレスを持つ場合は問題なく動作します。しかし、Host.A のように複数のネットワークインタフェース (複数の IP アドレス) があったり、サブインタフェースがあったりする場合、上記のように意図した動作になりません。
  * 上の実行例の場合、Host.A のインタフェース ha-eth0 自体は IP アドレスを持たないので、"failure in name resolution" となっています。
  * Mininet はノードが複数の IP アドレスを持つ場合、いずれか 1 つのアドレスを選択して使用します。複数のネットワークインタフェースを持つ場合は、どこに対して通信確認をしたいのかを明示する (IP アドレスで指定する) 必要があります。

Host.A は複数サブインタフェースを持っているので、それぞれ通信確認したい IP アドレスでを明示的に指定します。

```sh
hb ping -c1 192.168.0.1
hc ping -c1 172.16.0.1
```
```text
mininet> hb ping -c1 192.168.0.1
PING 192.168.0.1 (192.168.0.1) 56(84) bytes of data.
64 bytes from 192.168.0.1: icmp_seq=1 ttl=64 time=0.349 ms

--- 192.168.0.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.349/0.349/0.349/0.000 ms
mininet> 
mininet> hc ping -c1 172.16.0.1
PING 172.16.0.1 (172.16.0.1) 56(84) bytes of data.
64 bytes from 172.16.0.1: icmp_seq=1 ttl=64 time=0.439 ms

--- 172.16.0.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.439/0.439/0.439/0.000 ms
```

Host.A の ARP テーブルでは Host.B/C それぞれの IP/MAC アドレスの対応関係が取得できています。

```sh
ha ip neigh
```
```text
mininet> ha ip neigh
172.16.0.2 dev ha-eth0.20 lladdr 00:00:5e:00:53:0c STALE
192.168.0.2 dev ha-eth0.10 lladdr 00:00:5e:00:53:0b STALE
```

Host.B の ARP テーブルを見てみましょう。IP アドレス (192.168.0.1) に対して、この IP アドレスを持つ Host.A のサブインタフェースの MAC アドレス❶が登録されていることがわかります。(Host.C/❷ についても同様)

```sh
hb ip neigh
hc ip neigh
```
```text
mininet> hb ip neigh
192.168.0.1 dev hb-eth0 lladdr 00:00:5e:00:53:a1 REACHABLE  ...❶
mininet> hc ip neigh
172.16.0.1 dev hc-eth0 lladdr 00:00:5e:00:53:a2 STALE       ...❷
mininet> 
```

Switch.1 の MAC アドレステーブルでは、以下のようになります。Host.A と接続されているポート (port 1) についてサブインタフェースの MAC アドレス❶❷がそれぞれ登録されていることがわかります。サブインタフェース (論理的なインタフェース) の情報がどのように "1 つの(物理)実体" とマッピングされているかを確認してください。

(Shell ターミナル) スイッチ状態確認

```sh
# ポート名とポート番号の対応
sh ovs-ofctl show sw1 | grep sw1-eth
sh ovs-ofctl show sw2 | grep sw2-eth
# MAC アドレステーブル
ovs-appctl fdb/show sw1
```
```text
mininet> sh ovs-ofctl show sw1 | grep sw1-eth
 1(sw1-eth1): addr:6a:38:a6:75:ed:6e
 2(sw1-eth0): addr:ca:c5:33:40:59:b2
mininet> sh ovs-ofctl show sw2 | grep sw2-eth
 1(sw2-eth0): addr:0a:b5:fc:d3:fd:d5
 2(sw2-eth1): addr:26:b6:92:cc:14:b1
 3(sw2-eth2): addr:8a:c8:3d:21:41:9b
root@nwtraining01:/# 
root@nwtraining01:/# ovs-appctl fdb/show sw1
 port  VLAN  MAC                Age
    1    10  00:00:5e:00:53:a1  108    ... ❶ ha-eth0.10
    2    10  00:00:5e:00:53:0b  108
    1    20  00:00:5e:00:53:a2   40    ... ❷ ha-eth0.20
    2    20  00:00:5e:00:53:0c    7
```

## 補足: サブインタフェースについて

> [!NOTE]
> 以降は技術面での補足情報です。サブインタフェースとVLAN設定まわりについて確認したいときに参照してください。

### サブインタフェースについて

:customs: サブインタフェースの命名ルール:

* 演習中でサブインタフェースを使用する場合、以下のルールでインタフェース名が設定されています。
  * 物理インタフェース : "ホスト名 - ethX"
  * サブインタフェース : "物理インタフェース名 **.** VLAN-ID" (ホスト名-ethX.N)

サブインタフェースの特徴:
* サブインタフェースは、親(物理)インタフェースの設定を受け継ぎません。独立したインタフェースとして設定されます。
* サブインタフェースは論理的なインタフェースで、物理インタフェースと同等に扱えます。物理インタフェースとの "親子関係" や、VLAN ID 設定についてはオプションを指定して情報表示することで確認できます。

### インタフェースのVLAN設定確認

<details>

<summary>インタフェースのVLAN設定確認</summary>

演習ネットワークではインタフェース名で VLAN ID がわかるようにしてありますが、実際の設定も確認してみましょう。

(Mininet ターミナル) サブインタフェースの詳細情報表示

```text
mininet> ha ip -d link show ha-eth0.10
3: ha-eth0.10@ha-eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 00:00:5e:00:53:a1 brd ff:ff:ff:ff:ff:ff promiscuity 0 minmtu 0 maxmtu 65535 
    ❹vlan protocol 802.1Q ❺id 10 <REORDER_HDR> addrgenmode eui64 numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
```

ha-eth0.10 について、❹ VLAN のプロトコルとして 802.1Q を使用していること、❺ VLAN ID が 10 であることがわかります。

ノードが持つ VLAN 一覧を確認したい場合は以下のように `/proc/net/vlan/config` を参照してください。(参照: [linux - listing parent interface of a vlan - Server Fault](https://serverfault.com/questions/882754/listing-parent-interface-of-a-vlan))

```text
mininet> ha cat /proc/net/vlan/config
VLAN Dev name    | VLAN ID
Name-Type: VLAN_NAME_TYPE_RAW_PLUS_VID_NO_PAD
ha-eth0.10     | 10  | ha-eth0
ha-eth0.20     | 20  | ha-eth0
```

</details>

### インタフェース・サブインタフェースの依存関係の確認

<details>

<summary>インタフェース・サブインタフェースの依存関係の確認</summary>

`/proc/net/vlan/インタフェース名` を参照すると VLAN に関する詳細情報が確認できます。❺ VLAN ID だけでなく、サブインタフェースに対する ❶ 親インタフェースの情報も含まれます。

```sh
ha cat /proc/net/vlan/ha-eth0.10
```
```text
mininet> ha cat /proc/net/vlan/ha-eth0.10
ha-eth0.10  ❺VID: 10    REORDER_HDR: 1  dev->priv_flags: 1021
         total frames received            9
          total bytes received          560
      Broadcast/Multicast Rcvd            9

      total frames transmitted           12
       total bytes transmitted          956
Device: ❶ha-eth0
INGRESS priority mappings: 0:0  1:0  2:0  3:0  4:0  5:0  6:0 7:0
 EGRESS priority mappings: 
```

他にも、インタフェース・サブインタフェースの親子関係は以下のように確認できます。(参照: [linux - listing parent interface of a vlan - Server Fault](https://serverfault.com/questions/882754/listing-parent-interface-of-a-vlan))

```text
mininet> ha readlink /sys/class/net/ha-eth0/upper* | xargs basename -a
ha-eth0.10
ha-eth0.20
mininet> ha readlink /sys/class/net/ha-eth0.10/lower* | xargs basename -a
ha-eth0
mininet> ha readlink /sys/class/net/ha-eth0.20/lower* | xargs basename -a
ha-eth0
```

</details>

### VLANアクセスポートとトランクポート

<details>

<summary>VLANアクセスポートとトランクポート</summary>

チュートリアル 4b における Switch.2-Host.B/C 間の接続において、Host.B/C は VLAN についての情報を持ちません。Host.B/C は VLAN ヘッダのない (通常の) パケットを送信します。スイッチは受け取ったときに、受け取ったポートの `tag` 設定にそって、そのパケットがどの L2 セグメント宛てに送られたものかを判断します。スイッチからホストに送信する際も同様で、VLAN ID をもとにどのセグメント宛か判断し、Host.B/C 宛に出力する際は VLAN ヘッダを外してから送信します。

このようなポートのことを **VLAN access port** と呼びます。

|                 | Access port | Trunk port |
|-----------------|-------------|------------|
| VLAN ヘッダ     | つかない    | つく       |
| VLANへの関連付け| 1-VLAN      | 複数 VLAN  |

</details>

## チュートリアル4のまとめ

* VLAN
  * ブロードキャストドメインの分割
  * VLAN ID (1-4094) で識別
* デバイス間をまたがる VLAN
  * access port, trunk port
  * Linux sub-interface (trunk port 同等の機能を使える)

チュートリアル 4 はここまでです。演習ネットワークを終了させて[チュートリアル 5](../tutorial5/scenario.md) に進んでください。

```text
mininet> exit
```

<!-- FOOTER -->

---

[Previous](../tutorial3/scenario.md) << [Index](../index.md) >> [Next](../tutorial5/scenario.md)
<!-- /FOOTER -->
