<!-- HEADER -->
[Previous](../common/setup.md) << [README](/README.md) >> Next

---
<!-- /HEADER -->

<!-- TOC -->

- [演習を作る](#%E6%BC%94%E7%BF%92%E3%82%92%E4%BD%9C%E3%82%8B)
  - [ディレクトリ構成](#%E3%83%87%E3%82%A3%E3%83%AC%E3%82%AF%E3%83%88%E3%83%AA%E6%A7%8B%E6%88%90)
  - [環境の違い演習用と演習作成用](#%E7%92%B0%E5%A2%83%E3%81%AE%E9%81%95%E3%81%84%E6%BC%94%E7%BF%92%E7%94%A8%E3%81%A8%E6%BC%94%E7%BF%92%E4%BD%9C%E6%88%90%E7%94%A8)
  - [演習ネットワークの作成](#%E6%BC%94%E7%BF%92%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E3%81%AE%E4%BD%9C%E6%88%90)
    - [演習スクリプトのデバッグ](#%E6%BC%94%E7%BF%92%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%97%E3%83%88%E3%81%AE%E3%83%87%E3%83%90%E3%83%83%E3%82%B0)
    - [演習ネットワーク定義ファイルの作成と整合性テスト](#%E6%BC%94%E7%BF%92%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E5%AE%9A%E7%BE%A9%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%AE%E4%BD%9C%E6%88%90%E3%81%A8%E6%95%B4%E5%90%88%E6%80%A7%E3%83%86%E3%82%B9%E3%83%88)
  - [演習ドキュメントの作成](#%E6%BC%94%E7%BF%92%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88%E3%81%AE%E4%BD%9C%E6%88%90)
    - [ローカルWebサーバを起動してドキュメント参照](#%E3%83%AD%E3%83%BC%E3%82%AB%E3%83%ABweb%E3%82%B5%E3%83%BC%E3%83%90%E3%82%92%E8%B5%B7%E5%8B%95%E3%81%97%E3%81%A6%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88%E5%8F%82%E7%85%A7)
    - [Markdownの自動目次挿入](#markdown%E3%81%AE%E8%87%AA%E5%8B%95%E7%9B%AE%E6%AC%A1%E6%8C%BF%E5%85%A5)
    - [ヘッダ・フッタの挿入](#%E3%83%98%E3%83%83%E3%83%80%E3%83%BB%E3%83%95%E3%83%83%E3%82%BF%E3%81%AE%E6%8C%BF%E5%85%A5)
    - [演習ドキュメントの日本語チェック](#%E6%BC%94%E7%BF%92%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88%E3%81%AE%E6%97%A5%E6%9C%AC%E8%AA%9E%E3%83%81%E3%82%A7%E3%83%83%E3%82%AF)
    - [MarkdownをPDFに変換する](#markdown%E3%82%92pdf%E3%81%AB%E5%A4%89%E6%8F%9B%E3%81%99%E3%82%8B)
  - [演習ネットワーク定義](#%E6%BC%94%E7%BF%92%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E5%AE%9A%E7%BE%A9)
  - [TODO](#todo)

<!-- /TOC -->

# 演習を作る

## ディレクトリ構成

- 演習ディレクトリ [exercise](/exercise/) ディレクトリに演習用の (mininet コンテナ内部で使用する) コンテンツやスクリプト類があります。
  - 演習課題別にディレクトリ分割: 演習内でいくつかの演習ネットワークを使う場合、`L2nw_1a`, `L2nw_1b` のように abc... をつけて分割しています。
  - (開発時/通常版コンテナ使用時) exercise ディレクトリは mininet container の `/exercise` ディレクトリにマウントできます。(see. [docker-compose.yml](/docker-compose.yml))
- [exercise_docs](/exercise_docs/) ディレクトリにはテキスト等のドキュメント・演習ネットワーク定義ファイル(コンテナに含める json の元ファイルとなる yaml ファイル)を置きます。
  - これらは演習コンテナには含めません。
- [resources](/resources/) ディレクトリには演習用コンテナに含める追加のリソースがあります。

## 環境の違い(演習用と演習作成用)

- 演習コンテナ内で使用する Python script は原則 python2 向けです。([exercise](/exercise/) ディレクトリの中にあるもの)
  - コンテナ内部には python3 もありますが、mininet Python library が python2 環境に入っているためです。
  - python2 環境には yaml を読むモジュールがふくまれていません。また pip もいれていないのであまりパッケージの追加削除ができません。そのため、演習ネットワーク定義ファイルは json にしてあります。
- 上記以外は、演習問題の作成などに使用する演習開発ツール等です。演習には使用しません。
  - 演習開発ツールでは python3 環境を使用しています。(mininet コンテナの外で実行するもの)

## 演習ネットワークの作成

### 演習スクリプトのデバッグ

演習スクリプト `./nw_training.py` で `-l debug` オプションをつけて実行します。
`Node#cmd` あるいは `Switch#vsctl` などで実行しているコマンド列が表示されます。

### 演習ネットワーク定義ファイルの作成と整合性テスト

演習で使用する演習ネットワーク定義ファイルは json にしますが、json file を直接編集するのは煩雑なので、yaml にも対応しています。

- [exercise_docs](/exercise_docs/) 各ディレクトリ内にはオリジナルの演習ネットワーク定義ファイル (YAML) をおきます。
  - 演習ドキュメント・演習ネットワーク定義の元ファイル等、1 つのシナリオで使う素材をまとめておきます。
- YAML で作成した演習ネットワーク定義ファイルを、下記 `topology_checker.py` で json に変換して演習ディレクトリ ([exercise](/exercise/)) に入れます。
  - __:warning: yaml 編集後、json に変換して exercise 下に置くのを忘れずに。__
- "ModuleNotFoundError: No module named 'declared_topology'" となる場合は `PYTHONPATH` を設定してください。

```sh
export PYTHONPATH="$PYTHONPATH:$(pwd)/exercise/mn_builder"
./topology_checker.py 整合性テストをする演習ネットワーク定義ファイル(yaml/json)
```

[topology_checker.py](/topology_checker.py) で、演習ネットワーク定義ファイルのフォーマット変換 (json/yaml) と整合性のテストができます。

- 引数: 演習ネットワーク定義ファイル
- オプション
  - `-o`, `--oftype`: データ変換して出力 (stdout) するときのフォーマット (json or yaml を指定)
- 動作
  - `--oftype` がない場合は演習ネットワーク定義ファイルの整合性チェックをします。
  - `--oftype` がある場合は引数に与えたファイルを読み込み (ファイルフォーマットを拡張子で判定しています)、`--oftype` フォーマットで出力 (stdout) します。
- 整合性テスト
  - link に指定した node/interface の実体が存在しているか
  - link 両端のインタフェースで設定されている ip address が対になっている(同じセグメントにある)か
  - ノードに設定されている static route の next-hop が directory connected segment のアドレスか
  - etc

[convert_all_contents.sh](/convert_all_contents.sh) は、exercise_docs の中にあるすべての yaml file を json に変換して exercise 下に置きます。

## 演習ドキュメントの作成

### ローカルWebサーバを起動してドキュメント参照

[markserv](https://github.com/markserv/markserv) で HTTP server をたてて演習ドキュメント (markdown) を参照できるようにします。

```sh
# npm install
npx markserv -p 8642 -a 0.0.0.0 exercise_docs/
```

### Markdownの自動目次挿入

* w/VSCode, [Auto Markdown TOC - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=xavierguarch.auto-markdown-toc)
  * Command palette (Ctrl-Shift-p) → "Auto Markdown TOC: Insert/Update"

### ヘッダ・フッタの挿入

ドキュメント中のヘッダ・フッタコメントを置き換えます。

ドキュメント (markdown)

* このサンプルに対してもヘッダ・フッタ処理がかかってしまうので `@` をつけていますが実際のドキュメントでは外して書きます。

```md
<@!-- HEADER -->
ヘッダが挿入されます
<@!-- /HEADER -->

本文

<@!-- FOOTER -->
フッタが挿入されます
<@!-- /FOOTER -->
```

ヘッダ・フッタ挿入コマンド

* exercise_docs/ 下にある markdown ファイルのヘッダ・フッタを置き換えます。
* ドキュメントの順番 (Previous/Next) は [insert_hf.py](../insert_hf.py) の中で定義されています。

```sh
# cd exercise_docs
./insert_hf.py
```

### 演習ドキュメントの日本語チェック

[textlint](https://textlint.github.io/) を使っています。
* 参照: [textlint と VS Code で始める文章校正 - Qiita](https://qiita.com/takasp/items/22f7f72b691fda30aea2)
* w/VSCode, [vscode-textlint - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=taichi.vscode-textlint)
  * Command palette (Ctrl-Shift-p) → "textlint: Fix all auto-fixable Problems"
* リポジトリをクローンした際、`npm install` を実行してください。
  * 要 Node.js, npm
* 設定ファイルは [.textlintrc](/.textlintrc) です。

CLI で実行する場合

```sh
# npm install
npx textlint exercise_docs/**/*.md
```

### MarkdownをPDFに変換する

[md-to-pdf](https://github.com/simonhaenisch/md-to-pdf) を使っています。

* 参照: [MarkdownをPDFに変換する「md-to-pdf」は痒いところに手が届く素敵ツール | DevelopersIO](https://dev.classmethod.jp/articles/md-to-pdf/)
* リポジトリをクローンした際、`npm install` を実行してください。
  * 要 Node.js, npm
* 設定ファイルは [.md2pdf.js](/.md2pdf.js) です。

`exercise_docs/**/*.md` を PDF に変換 (`exercise_docs/**/*.pdf`)

```sh
# npm install
npx md-to-pdf --config-file .md2pdf.js exercise_docs/**/*.md
```

## 演習ネットワーク定義

演習ネットワーク定義ファイルのデータ構造

- `nodes`: _Array\<Node\>_
- `links`: _Array\<Link\>_
- _Node_:
  - `type` : _String_ in[`host`, `router`, `switch`])
    - ノードの種別
    - `host` は linux node
    - `router` は ipv4 forwarding を有効にした linux node
    - `switch` は Open vSwitch Bridge
    - Firewall は `svc_procs` で iptables 設定をする `router` として定義します。
  - `name` : _String_
    - ノード名 = オブジェクト識別子 (unique)
  - `interfaces` : _Array\<Interface\>_
    - インタフェースの配列
  - `routes`[optional]: _Array\<Route\>_
    - ノードに設定する静的経路
    - type `host`, `router` のときのみ有効
  - `svc_procs`[optional]: _Array\<String\>_
    - ノード作成時に実行するコマンド
    - 常時実行するプロセスはバックグラウンド実行するコマンド文字列で与えること (e.g.`"command &"`)
    - type `host`, `router` のときのみ有効
  - `stp`[optional]: _Boolean_
    - STP (802.1D) の有効化
    - type `switch` のときのみ有効
  - `stp_priority`[optional]: _Integer_
    - STP (802.1D) bridge priority (0=primary root, 4096(0×1000)=secondary root, default=32768(0×8000))
    - type `switch` のときのみ有効
- _Interface_:
  - `type` : _String_ in[`l3`, `l2`]
    - インタフェースを持つノードが type `switch` の場合、インタフェースの type は `l2` を指定すること。(`switch` に対して `l3` 指定した場合は未実装)
  - `name`: _String_
    - インタフェース名 = オブジェクト識別子
    - mininet 的には全てのノードの名前が見えるので、`hostanme-ethX` の形で指定するのを推奨
    - __:warning: veth については使えない文字・最大長(15 文字)制限があります__
  - `mac_addr`[optional]: _String_ MAC address (e.g. `00:00:5e:00:53:00`)
    - MAC アドレス
    - インタフェースを持つノードが type `switch` **以外**の場合に有効
    - インタフェースのタイプは `l2`/`l3` いずれに対しても設定可能。指定されない場合 (default) はランダムに MAC アドレスを設定
  - `ip_addr`[optional]: _String_ IPv4/prefix-length (e.g. `192.168.0.1/24`)
    - IP アドレス
    - インタフェースの type が `l3` のときは必須、`l2` のときは無視
  - `access_vlan`[optional]: _Integer_
    - アクセスポートの VLAN ID
    - インタフェースを持つノードが type `switch` のときのみ有効
  - `trunk_vlans`[optional]: _Array\<Integer\>_
    - トランクポートの VLAN ID リスト
    - インタフェースを持つノードが type `switch` のときのみ有効
    - `3-5` などの範囲指定は使えません
  - `sub_interfaces`[optional]: _Array\<SubInterface\>_
    - サブインタフェースのリスト : Linux node むけの vlan 設定は親インタフェースに対する子インタフェース(sub interface)指定となるため、入れ子にしてある。
    - インタフェースを持つノードが type `host`, `router` のときのみ有効
  - 補足: vlan 設定はノード種別に応じて使い分ける
    - for `switch` : `access_vlan` or `trunk_vlans`
    - for `host` and `router` : `sub_interfaces`
- _SubInterface_:
  - ノードが `host` または `router` の場合に使用する。親インタフェースは `l2`/`l3` どちらでもよい。
  - `name`[optional]: String
    - サブインタフェース名。省略時は "親インタフェース名.vlan" 形式になる
  - `ip_addr` : _String_ IPv4/prefix-length
    - IP アドレス
  - `mac_addr`[optional]: _String_ MAC address
    - MAC アドレス
  - `vlan`: _Integer_
    - VLAN ID
- _Route_:
  - `dst_net`: _String_ IPv4/prefix-length or `default`
    - 対象とする宛先の範囲
  - `next_hop` : _String_ IPv4 or `blackhole`
    - 転送先 IP アドレス
  - `note`[optional]: _String_
    - コメント (json 使用時のコメント欄)
- _Link_:
  - __:warning: リンク端点 (tp: termination-point) に sub-interface は指定できない__
  - `node1` : _String_
    - リンク端点 1 のノード名
  - `intf1` : _String_
    - リンク端点 1 のインタフェース名
  - `node2` : _String_
    - リンク端点 2 のノード名
  - `intf2` : _String_
    - リンク端点 2 のインタフェース名
  - `down`[optional]: _Boolean_
    - 初期起動時にリンクを up にするか (省略時は false = up)

## TODO

- :warning: IPv6 には今の所対応していません

<!-- FOOTER -->

---

[Previous](../common/setup.md) << [README](/README.md) >> Next
<!-- /FOOTER -->
