[README](/README.md)

<!-- TOC -->

- [共通](#共通)
  - [表記](#表記)
  - [リファレンス](#リファレンス)
- [チュートリアル](#チュートリアル)
- [演習問題](#演習問題)
  - [基本 (Must)](#基本-must)
  - [応用 (Optional)](#応用-optional)

<!-- /TOC -->

---

# 共通

## 表記

| 絵文字             | 意味     |
|--------------------|----------|
| :warning:          | 注意事項 |
| :bulb:             | ヒント   |
| :white_check_mark: | 今回の演習の範囲からは外れる (演習には含めていない) 技術的な補足情報 |
| :customs:          | この演習固有の制約・条件設定・仕様・ルール |

**太字** : 技術用語または強調

<details>

<summary>マウスクリックで折りたたみ展開するテキスト</summary>

折り畳まれています。マウスクリックで展開されます。

</details>

## リファレンス

* [コマンドリスト](./common/command_list.md)
  * チュートリアルおよび演習問題中で使用することが想定されるコマンドの一覧 (リファレンス) です。
* [用語集](./common/glossary.md)
  * 座学・チュートリアル・ハンズオンで登場する各種用語の一覧です。
* [Windowsでドキュメントを読む際のフォント変更](./common/windows_code_font.md)
  * Windows ユーザ向け: ドキュメント中の一部表記が見づらい場合のフォント変更手順

# チュートリアル

演習問題の前にチュートリアルを実施してください。

* チュートリアル 0・チュートリアル 1 には演習環境の使い方・操作方法・使用上の注意事項等があります。

各チュートリアルでは、座学に含まれていた基本的なネットワークの考え方に対して、実際のネットワークではどのような動作をするのかを step-by-step で見ていきます。

| チュートリアル                             | テーマ |
|--------------------------------------------|--------|
| [チュートリアル0](./tutorial0/scenario.md) | 基本操作方法 |
| [チュートリアル1](./tutorial1/scenario.md) | 基本操作方法 |
| [チュートリアル2](./tutorial2/scenario.md) | L2 基礎 (1) |
| [チュートリアル3](./tutorial3/scenario.md) | L2 基礎 (2) |
| [チュートリアル4](./tutorial4/scenario.md) | L2 VLAN 基礎 |
| [チュートリアル5](./tutorial5/scenario.md) | L3 基礎 |
| [チュートリアル6](./tutorial6/scenario.md) | L2/L3 連携 |
| [チュートリアル7](./tutorial7/scenario.md) | L4 基礎 |

# 演習問題

演習問題の前に[チュートリアル](#チュートリアル)を実施してください。

"基本" の課題から先に取り組んでください。"応用" は発展課題です。

* 原則として、表の上から順 (No.の順) に着手してください。演習問題の順序に依存する内容 (前の演習問題で得ているであろう知識や理解を前提とする) があります。
* App-2 は机上検討のみです。それ以外は実際に操作可能です。

目的はネットワークの基本動作とその動作の考え方を、実際に手を動かしながら・動作を確認しながら理解することです。

* :bulb: 操作方法等がわからない場合は、各問題のヘッダ部にある「この問題で使用するコマンド」を参照してください。
  * 操作方法の詳細については、関連するチュートリアルや [コマンドリスト](./common/command_list.md) を参照してください。
  * **コマンドリストに記載がないツールでも、演習環境内で使用可能なものはすべて自由に使用してください。**
  * 各問題にある「この問題で使用するコマンド」は、あくまでも使うことが予想される主要なコマンド (コマンドのヒント) であって、それだけに限定するものではありません。
* :warning: 演習問題のデータとして、問題用のものと解説用のものが含まれています。問題用のファイル名は `question.*`・解説用のファイル名は `answer.*` になっています。

演習問題がわからない場合は解説を先に見てしまっても構いません。ただ答え合わせをして終わるのではなく、「なぜこうなるのか」「どうしてこうするのか」などを説明できるようにしてください。解説に沿って実際に設定し、動作とその原理・理由を確認してください。

## 基本 (Must)

|No.| シナリオ | 演習問題                    | 解説                      |
|---|----------|-----------------------------|---------------------------|
| 1 | L2NW-1   | [問題](./l2nw1/question.md) | [解説](./l2nw1/answer.md) |
| 2 | L2NW-2   | [問題](./l2nw2/question.md) | [解説](./l2nw2/answer.md) |
| 3 | L3NW-1   | [問題](./l3nw1/question.md) | [解説](./l3nw1/answer.md) |
| 4 | L3NW-2   | [問題](./l3nw2/question.md) | [解説](./l3nw2/answer.md) |
| 5 | L4NW-1   | [問題](./l4nw1/question.md) | [解説](./l4nw1/answer.md) |
| 6 | L4NW-2   | [問題](./l4nw2/question.md) | [解説](./l4nw2/answer.md) |

## 応用 (Optional)

| チュートリアル                              | テーマ |
|---------------------------------------------|--------|
| [チュートリアル 8](./tutorial8/scenario.md) | L2 STP 基礎 (L2NW-3 実施前に確認してください) |

|No.| シナリオ | 演習問題                    | 解説                      |
|---|----------|-----------------------------|---------------------------|
| 7 | L2NW-3   | [問題](./l2nw3/question.md) | [解説](./l2nw3/answer.md) |
| 8 | L4NW-3   | [問題](./l4nw3/question.md) | [解説](./l4nw3/answer.md) |
| 9 | App-1    | [問題](./app1/question.md)  | [解説](./app1/answer.md)  |
|10 | App-2    | [問題](./app2/question.md)  | [解説](./app2/answer.md)  |

<!--
http://xahlee.info/comp/unicode_circled_numbers.html
⓿
❶ ❷ ❸ ❹ ❺ ❻ ❼ ❽ ❾ ❿
⓫ ⓬ ⓭ ⓮ ⓯ ⓰ ⓱ ⓲ ⓳ ⓴
-->
