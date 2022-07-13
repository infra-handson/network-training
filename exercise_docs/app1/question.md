<!-- HEADER -->
[Previous](../l4nw3/answer.md) << [Index](../index.md) >> [Next](../app1/answer.md)

---
<!-- /HEADER -->

<!-- TOC -->

- [App-1 (問題編)](#app-1-問題編)
  - [前置き](#前置き)
  - [シナリオ](#シナリオ)
  - [構成図](#構成図)
  - [通信要件表](#通信要件表)
  - [はじめる前に](#はじめる前に)
    - [社内システムで動かしているサービスについて](#社内システムで動かしているサービスについて)
    - [各問題の通信確認方法について](#各問題の通信確認方法について)
  - [問題1: 新規システムA環境構築](#問題1-新規システムa環境構築)
  - [問題2: L3設定](#問題2-l3設定)
  - [問題3: L4設定](#問題3-l4設定)

<!-- /TOC -->

# App-1 (問題編)

## 前置き

この問題で知ってほしいこと

* これまでのトピックの組み合わせ: 実際のネットワーク設計・運用でどんなことを考えているのか
  * IP アドレスの設計、IP アドレスの管理
  * システムの通信要件とファイアウォールのルール設定
* 企業内部署の移転(引越し)シナリオに沿って、ネットワークが情報システムの中で果している役割を理解する。
  * ネットワークがどのように物理的な場所を吸収しているのか?
  * 物理的な場所と関連して、どのように論理構成(L3 設計)やセキュリティ設定(L3 ファイアウォール設定) を修正する必要があるか?
  * そうした作業を進めるために必要なインプット = 他の担当者と連携して収集する必要がある情報はなにか?

<details>

<summary>この問題で使用するコマンド :</summary>

* インタフェースの一覧表示・設定確認
  * IP アドレス一の確認
    * `ip addr show [dev インタフェース名]`
  * VLAN サブインタフェース vlan-id の確認
    * `ip -d link show インタフェース名`
* スイッチ・ポートの設定確認
  * `ovs-vsctl show`
* ノード内のプロセス操作
  * プロセス一覧表示
    * `ps -o pid,args` : `-o` 表示するフィールドの指定。長い文字列が途中で削られるのを防ぎたい場合は `--width 100` のように最大幅を数字で指定する。
  * プロセス停止
    * `kill プロセスID`
* ノード内でオープンされているポートの一覧
  * `ss -ltn` : `-l` (listen), `-t` (tcp), `-n` (numeric), オプションは適宜選択すること
* L3 の通信確認
  * `ping 宛先IPアドレス` (オプション `-c N` は送信するパケット数を指定します。)
* L3 通信経路の確認
  * `traceroute 宛先IPアドレス`
* ルーティングテーブルの確認
  * `ip route`
* ルーティングテーブルの操作 (静的経路の追加・削除)
  * `ip route add 宛先ネットワーク via 中継先ルータ(nexthop)IPアドレス`
  * `ip route del 宛先ネットワーク`
+ L4 の通信確認 (:white_check_mark: 演習内では L4 はすべて Web サーバになっています)
  * `curl URL`
* Firewall パケットフィルタルールの一覧表示
  * `iptables -nvL`: オプション `--line-numbers` で行番号表示
* Firewall パケットフィルタルールの操作
  - [コマンドリスト](../common/command_list.md#通信設定-l4パケットフィルタ操作) 参照
  - ルールを追加
    - `iptables -A チェーン ルール` : 単純に(末尾に)追加されます。例 `iptables -A FORWARD -p icmp -j ACCEPT` (FORWARD chain に icmp を許可するルールを追加する)
  - 行番号を指定してルールを挿入
    - `iptables -I チェーン 行番号 ルール`: 例 `iptables -I FORWARD 3 -p icmp -j DENY` (FORWARD chain の 3 行目にルールを挿入)
  - 特定のフィルタルールの削除
    - `iptables -D チェーン 行番号`: 行番号でルールを指定して削除。例 `iptables -D FORWARD 5` (FORWARD chain の 5 行目の削除)
    - `iptables -D チェーン ルール`: 指定したルールを削除。例 `iptables -D FORWARD -p icmp -j ACCEPT` (FORWARD chain にある `-p icmp -j ACCEPT` ルールを削除)
  - フィルタのルールは多数のオプションがあるので別途資料を参照してください
* パケットキャプチャ (必要に応じて)
  * `tcpdump -l [-i インタフェース名]` : オプション `-l` がないとリアルタイムに表示されません。
  * 必要に応じてスクリプトを作成してください ([チュートリアル5](../tutorial5/scenario.md#l4パケットフィルタ操作) 参照)

</details>

## シナリオ

あなたは T 社情報システム部のメンバーです。このたび、T 社は自社新社屋となるビルを新たに豊洲に用意し、都内に分散している部署を新社屋へ集約することにしました。T 社東京地区の社屋移転に伴う社内ネットワーク変更作業を完了させてください。

* T 社は都内数カ所に拠点があります。
  * データセンタ: 全社共通システムを置いています。都内・地方含めて全社から利用するシステムです。
  * 新宿ビル A/B 棟: 全社共通部門のいくつかの部署が入居しています。
  - 豊洲ビル: 新社屋 (移転先) です。
* 実施済み (移転第 1 フェーズ)
  * 豊洲ビル - データセンタ間と閉域網で接続済みです。
  * すでに都内の別なビルにはいっていた事業部 A/B は移転を完了しており、豊洲で業務を開始しています。(事業部 A/B が入居していたビルはすでに解約しました。)
* 現状 (移転第 2 フェーズ)
  * 新宿ビル B 棟に入居している部署を豊洲の新社屋ビルへ移転します。
  * いま社内ネットワークは構成図 (図 2) の状況にあります。これは、新宿ビル B 棟に入っていた部署が移転した直後の状態です。金曜日に新宿ビル B 棟で梱包、土日で荷物配送・月曜に開梱というスケジュールで、ちょうど土日のタイミングにあたります。
* これからすること
  * 月曜から総務部・経理部が移転先 (豊洲ビル) で開梱・ネットワーク接続して業務開始できるように社内ネットワークの設定を変更します。(もちろん、すでに移転が終わって稼働開始している事業部 A/B への業務影響がおきないようにする必要があります。)
  * 移転に伴うネットワーク停止時間を設定するので、そのタイミングにあわせて、部署移転作業の後に社内リリースする予定の "新規システム A" 環境も構築します。

## 構成図

図 1: 概要 (L3 構成図)

![Topology overview](topology_a.drawio.svg)

図 2: 詳細 (`exercise/app1/question.json`)

* 演習(通信確認)用に、各部署のサブネットにそれぞれ 1 台、代表ノードとして Server/Host を置いています。

![Topology detail](topology_b.drawio.svg)

## 通信要件表

|No.|from\to|インターネット|社外Web|社内ポータル|勤怠管理システム|新規システムA|企画部|情報システム部|経理部|総務部|事業部A|事業部B|
|---|--|--|--|--|--|--|--|--|--|--|--|--|
| 1 |インターネット inet||icmp, 80/tcp|-|-|-|-|-|-|-|-|-|
| 2 |社外Web Server.0a|icmp 80/tcp||icmp|icmp|icmp|icmp|icmp|icmp|icmp|icmp|icmp|
| 3 |社内ポータル Server.1a|icmp, 80/tcp|icmp||icmp|icmp|icmp|icmp|icmp|icmp|icmp|icmp|
| 4 |勤怠管理システム Server.1b|icmp, 80/tcp|icmp|icmp||icmp|icmp|icmp|icmp|icmp|icmp|icmp|
| 5 |新規システムA Server.1c|icmp, 80/tcp|icmp|icmp|icmp||icmp|icmp|icmp|icmp|icmp|icmp|
| 6 |企画部 Host.2a|icmp, 80/tcp|icmp, 80/tcp|icmp, 80/tcp|icmp, 8000/tcp|icmp, 8000/tcp||icmp|icmp|icmp|icmp|icmp|
| 7 |情報システム部 Host.2b|icmp, 80/tcp|icmp, 22/tcp, 80/tcp|icmp, 22/tcp, 80/tcp|icmp, 8000/tcp, 22/tcp|icmp, 8000/tcp, 22/tcp|icmp||icmp|icmp|icmp|icmp|
| 8 |経理部 Host.3a|icmp, 80/tcp|icmp, 80/tcp|icmp, 80/tcp|icmp, 8000/tcp|icmp, 8000/tcp|icmp|icmp||icmp|icmp|icmp|
| 9 |総務部 Host.3b|icmp, 80/tcp|icmp, 80/tcp|icmp, 80/tcp|icmp, 8000/tcp|icmp, 8000/tcp|icmp|icmp|icmp||icmp|icmp|
|10 |事業部A Host.4a|icmp, 80/tcp|icmp, 80/tcp|icmp, 80/tcp|icmp, 8000/tcp|icmp, 8000/tcp|icmp|icmp|icmp|icmp||icmp|
|11 |事業部B Host.4b|icmp, 80/tcp|icmp, 80/tcp|icmp, 80/tcp|icmp, 8000/tcp|icmp, 8000/tcp|icmp|icmp|icmp|icmp|icmp|

基本ポリシ:

* 社内→インターネットは Web アクセスのみ許可
* インターネット→社内の接続は拒否
* 社内間および社内→社外の icmp (ping) は許可
* 部署→社内システムには、社内システムで動作しているアプリケーション通信を許可
  * 情報システム部はシステムメンテナンスのため、社内システムに対するリモートアクセス (ssh, 22/tcp) を許可
* 部署間のアプリケーション通信は拒否

## はじめる前に

### 社内システムで動かしているサービスについて

:customs: "SSH, 22/tcp" については、演習システムの都合で実際の ssh サーバを起動しているわけではありません。

他のサービスと同じく 22/tcp で HTTP サーバが listen しているので、Web サーバと同様に `curl` コマンドで応答が返ることを確認してください。

例: 下記のようにサービス種別も表示されます。

```text
mininet> inet curl localhost:80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
Serving HTTP on 0.0.0.0 port 22 (http://0.0.0.0:22/) ...
127.0.0.1 - - [09/Jul/2021 09:45:52] "GET / HTTP/1.1" 200 -
Internet - http

   ____     __                   __          __   __  __     
  /  _/__  / /____ _______  ___ / /_  ____  / /  / /_/ /____ 
 _/ // _ \/ __/ -_) __/ _ \/ -_) __/ /___/ / _ \/ __/ __/ _ \
/___/_//_/\__/\__/_/ /_//_/\__/\__/       /_//_/\__/\__/ .__/
                                                      /_/    
mininet> inet curl localhost:22
127.0.0.1 - - [09/Jul/2021 09:45:57] "GET / HTTP/1.1" 200 -
Internet - ssh

   ____     __                   __                  __ 
  /  _/__  / /____ _______  ___ / /_  ____  ___ ___ / / 
 _/ // _ \/ __/ -_) __/ _ \/ -_) __/ /___/ (_-<(_-</ _ \
/___/_//_/\__/\__/_/ /_//_/\__/\__/       /___/___/_//_/
                                                        
```

### 各問題の通信確認方法について

社内の各部署からインターネット・社内サービスへの接続確認用のスクリプトがあります。

* 環境変数 `S1C_ADDR` で Server.1c の IP アドレスを指定できます。(問題 1)

```sh
cd /exercise
S1C_ADDR=自分で設定したs1cのIPアドレス ./nw_test.sh app1_l3
S1C_ADDR=自分で設定したs1cのIPアドレス ./nw_test.sh app1_l4
# または
# export S1C_ADDR=自分で設定したs1cのIPアドレス
# ./nw_test.sh app1_l3
# ./nw_test.sh app1_l4
```

App-1 用の自動テストでは、通信要件表のとおりに通信ができるかどうかを確認します。このネットワークにはファイアウォールが含まれているため、通信ができることだけでなく「できないこと」も要件に含まれます。

* テストスクリプトは、基本的な通信要件について通信できる・できないの確認をしています (表の全パターン網羅ではありません)。下記の実行例のように、通信できること (success case)・通信できないこと (fail case) のどちらも Fail がなくなれば完了です。
* テストは L3/L4 の 2 種類あります。それぞれに通信できること・できないことのテストが含まれています。

```text
# Server.1c の IP アドレス設定
root@nwtraining01:/exercise# export S1C_ADDR=172.x.x.x

# App-1 L3 の通信テスト (問題2)
root@nwtraining01:/exercise# ./nw_test.sh app1_l3
# L3 success case test
.................................

Total Duration: 4.032s
Count: 33, Failed: 0, Skipped: 0
# L3 fail case test
..................

Total Duration: 1.111s
Count: 18, Failed: 0, Skipped: 0

# App-1 L4 の通信テスト (問題3)
root@nwtraining01:/exercise# ./nw_test.sh app1_l4
# L4 success case test
....................................................................

Total Duration: 1.569s
Count: 68, Failed: 0, Skipped: 0
# L4 fail case test
......................................................

Total Duration: 2.098s
Count: 54, Failed: 0, Skipped: 0
```

## 問題1: 新規システムA環境構築

社内向けのシステムは、172.16.0.128/25 の範囲を /29 のブロックに分割し、システムごとに先頭から順に割り当てることになっています。

* 図 1/2 のように、現在 2 つの社内システムがあります。新規システム A を追加するとしたら、 アドレスブロックはどのアドレスになりますか?
* このアドレス採番ルールの下では最大いくつの社内システムを作れますか?

新規システム A セグメントの Server.1c の設置(ネットワーク配線)は終わっています。しかし IP 設定はまだできていません。

* アドレス採番ルールに従って、Server.1c ほか必要な箇所に IP アドレス設定を追加してください。
  * 図 2 (`question.json`) 起動時にはダミーの IP アドレスが設定されています。
* アドレス採番ルール
  * 社内は全て、上流側機器から小さな数字の IP アドレスを設定するルールです。(若番から採番するルール)
  * サブネットの先頭 (サブネットの中でホストに割り振れる範囲のうち最も小さな数字のアドレス) をデフォルトゲートウェイに設定します。
  * デフォルトゲートウェイを除いて、数字の小さな順にサーバのアドレスとして設定していきます。

問題 1 では、まず Server.1c と Router.A 間の通信 (ping) ができるようにしてください。社内の各部署から接続できるようにするためには、社内ネットワークの設定が必要です → 問題 2/3 で設定します。

## 問題2: L3設定

新宿ビル B 棟に入居していた経理部・総務部を、新しくできた豊洲ビルに移転させます (図 2)。移転した部署内の機材設置と豊洲ビル内ルータ・スイッチ (Router.D, Switch.D) の設定だけしてある状態で、まだ社内ネットワークのルータ・ファイアウォール設定は入っていません。

* 社内 NW の各ルータ・ファイアウォールについて、どこにどのような設定を追加・削除する必要がありますか?
* 実際に設定して動作確認をしてください。
  * 各部署から社内システムに接続できること (ping)
  * インターネットに接続できること (ping)
* L3 の自動テストを実行して Fail がなければ完了です。(参照:[各問題の通信確認方法について](#各問題の通信確認方法について))

参考: `pingall` するとタイムアウト待ちで時間がかかるため、結果を載せておきます (問題 1 実施後・問題 2 設定前の状態)。移転したセグメントの Host.3a/b への通信が失敗していることがわかります。これが成功するように社内 NW のルータ・ファイアウォールを設定してください。

```text
mininet> pingall
*** Ping: testing ping reachability
fa -> fb fc h2a h2b X X h4a h4b inet ra rb rc rd re s0a s1a s1b s1c 
fb -> fa fc h2a h2b X X h4a h4b inet ra rb rc rd re s0a s1a s1b s1c 
fc -> fa fb h2a h2b X X h4a h4b inet ra rb rc rd re s0a s1a s1b s1c 
h2a -> fa fb fc h2b X X h4a h4b inet ra rb rc rd re s0a s1a s1b s1c 
h2b -> fa fb fc h2a X X h4a h4b inet ra rb rc rd re s0a s1a s1b s1c 
h3a -> X X X X X h3b h4a h4b X X X X rd X X X X X 
h3b -> X X X X X h3a h4a h4b X X X X rd X X X X X 
h4a -> fa fb fc h2a h2b h3a h3b h4b inet ra rb rc rd re s0a s1a s1b s1c 
h4b -> fa fb fc h2a h2b h3a h3b h4a inet ra rb rc rd re s0a s1a s1b s1c 
inet -> fa X X X X X X X X X X X X X s0a X X X 
ra -> fa fb fc h2a h2b X X h4a h4b inet rb rc rd re s0a s1a s1b s1c 
rb -> fa fb fc h2a h2b X X h4a h4b inet ra rc rd re s0a s1a s1b s1c 
rc -> fa fb fc h2a h2b X X h4a h4b inet ra rb rd re s0a s1a s1b s1c 
rd -> fa fb fc h2a h2b h3a h3b h4a h4b inet ra rb rc re s0a s1a s1b s1c 
re -> fa fb fc h2a h2b X X h4a h4b inet ra rb rc rd s0a s1a s1b s1c 
s0a -> fa fb fc h2a h2b X X h4a h4b inet ra rb rc rd re s1a s1b s1c 
s1a -> fa fb fc h2a h2b X X h4a h4b inet ra rb rc rd re s0a s1b s1c 
s1b -> fa fb fc h2a h2b X X h4a h4b inet ra rb rc rd re s0a s1a s1c 
s1c -> fa fb fc h2a h2b X X h4a h4b inet ra rb rc rd re s0a s1a s1b 
*** Results: 20% dropped (272/342 received)
```

## 問題3: L4設定

* Firewall.B, Firewall.C ではどのような設定を追加・削除する必要がありますか?
  * 各部署から社内システムに接続できること (http, ssh)
  * インターネットに接続できること (http)
* L4 の自動テストを実行して Fail がなければ完了です。(参照:[各問題の通信確認方法について](#各問題の通信確認方法について))

<!-- FOOTER -->

---

[Previous](../l4nw3/answer.md) << [Index](../index.md) >> [Next](../app1/answer.md)
<!-- /FOOTER -->
