# Setup Editorial Control Plan

Updated: 2026-03-28

## 目的

本書の全 `.qmd` について、setup 周辺の記述を章ごとの差ではなく、意図した例外だけが残る状態まで統制する。

## 適用範囲

- 冒頭の `required_packages`
- `pacman` のブートストラップ
- hidden / visible setup チャンク
- setup 見出し
- パッケージの役割説明
- 追加前提の説明
- fold 表示ラベル
- 衝突しやすい関数名の namespace 方針
- `theme_set()` と図の既定テーマ
- `library()` の使用方針
- `eval` オプションの明示方針
- Quarto chunk option 記法
- コードコメントの言語方針
- `echo` / `include` の使い分け
- ラベル / 注釈の可読性
- 静的表 / 計算表 / 探索表の出力方針
- `Markdown` / `gt` / `DT` / `knitr::kable()` の役割分担

## 正規化ルール

1. 全 `.qmd` に冒頭の `required_packages` チャンクを置く。
2. visible setup より前にパッケージが必要な章だけ hidden `pre-setup` を置いてよい。
3. `pacman` の確認は必ず次の形に統一する。  
   `if (!requireNamespace("pacman", quietly = TRUE)) install.packages("pacman", repos = "https://cloud.r-project.org")`
4. `require("pacman")` は使わない。
5. `install.packages("pacman", ...)` では CRAN mirror を省略しない。
6. `pacman::p_load(...)` の中に役割説明コメントを埋め込まない。
7. パッケージの役割は本文で明示する。
8. パッケージの役割説明は、インストール元ではなく機能別のフラットな箇条書きで書く。
9. core dependency と optional / external dependency は分けて書く。
10. setup 節の見出しは原則 `## セットアップ` に統一する。
11. hidden package bootstrap のチャンク名は原則 `pre-setup` に統一する。
12. 主たる package loading チャンク名は原則 `setup` に統一する。
13. 後段の局所 helper chunk は `setup` 命名規則の対象外とする。
14. fold 付きコードの既定ラベルは `code-summary: "コード"` に統一する。
15. 教育上の意図が明確な例外だけ、別ラベルを許容する。
16. ツールチェーン要件は必要時のみ明記する。  
    例: Windows の `Rtools`、macOS の Command Line Tools、Praat、GitHub パッケージ。
17. `select()` / `filter()` のような衝突しやすい関数は、コード側で `dplyr::` を明示する。
18. 本書標準の ggplot テーマは `theme_bw(base_size = 12, base_family = "HiraginoSans-W3")` と `theme_update(legend.position = "bottom")` の組み合わせとする。
19. `theme_book()` / `theme_geo()` / `theme_speech()` のような章固有テーマは、関数でも事前生成オブジェクトでもよいが、上記標準テーマを土台にした派生形として使う。
20. hidden `pre-setup` と visible `setup` が別々に存在する章では、単独実行性のために同じ `theme_set()` を重ねてよい。
21. `library()` は原則として分析章の実行コードでは使わず、setup の `pacman::p_load()` か `pkg::fun()` に寄せる。
22. `library()` を残してよいのは、パッケージ読み込みそのものを説明する教材コード、または競合の再現を見せる教育目的の例だけとする。
23. 全ての R コードチャンクで `eval` を明示する。
24. 実行するチャンクは `#| eval: true`、実行しない例示チャンクは `#| eval: false` に統一する。
25. 条件付き実行が必要な場合だけ `#| eval: !expr ...` を使う。
26. 旧式の chunk header option である `eval=TRUE` / `eval=FALSE` は使わない。
27. `message=FALSE`、`warning=FALSE`、`fig.height=`、`fig.width=` などの旧式 chunk header option は使わず、`#|` 形式に統一する。
28. `echo: false` は本文では不要な中間コードだけを隠す目的に限定し、依存関係の初期化や重要な分析コードの隠蔽には使わない。
29. `include: false` は bootstrap や補助計算など、出力自体を本文に出さない preparatory chunk に限定する。
30. コードコメントは原則として日本語で書き、API 名・関数名・外部用語を除いて英語コメントを新規に増やさない。
31. 連続量の順序尺度には、特別な理由がない限り `scale_*_viridis_c(option = "C")` を優先する。
32. 0 や基準値を中心に正負が分かれる発散尺度には、章内で一貫した青白赤系の `scale_*_gradient2()` を使う。
33. カテゴリ尺度には章内で一貫した palette を使い、`color` は `Dark2` 系、`fill` は `Set2` 系、または章ローカルの named palette に揃える。
34. 散布図・ネットワーク図・バイプロットなど、自由配置ラベルが3件以上ある図では、`ggrepel::geom_text_repel()` または `repel = TRUE` を優先する。
35. ヒートマップのセル中央、棒上端、固定位置の短い注記など、位置が構造的に決まっているラベルは `geom_text()` を維持し、必要最小限の `nudge_*` や `vjust` で調整する。
36. 固定注釈はデータラベルと役割を分け、四隅・帯・象限など端部に寄せて主データの可読性を優先する。
37. 概念比較、用語整理、手順確認、参照一覧のような固定的な教育用表は、原則として Markdown 表で書く。
38. ふつうの計算結果表・要約表・係数表は、まず `knitr::kable()` を使って簡潔に出す。
39. 列グループ、脚注、条件付きハイライトなど、`kable` では読みにくくなる高度な整形が本当に必要なときだけ `gt` を使う。
40. 並べ替え、検索、フィルタ、横スクロールが読解そのものに必要な探索表だけ、`DT::datatable()` を使う。
41. 章ローカルの表ラッパーは増やさず、可能な限り標準の Markdown / `knitr::kable()` / `gt` / `DT` に寄せる。
42. 同じ役割の表について章ごとに別の出力手段を採らない。表の選択基準は章の好みではなく、表の役割で決める。
43. 本文中でその場で読み切れる小さな固定表は、できる限り Markdown を優先し、不要な HTML widget や CSS 依存を増やさない。

## 標準パターン

1. 冒頭に `required_packages`
2. 必要時のみ hidden `pre-setup`
3. 章前半に `## セットアップ`
4. `### 主なパッケージの役割`
5. 必要な章のみ `### 追加の前提`
6. 固定の概念表・比較表・用語表は Markdown 表
7. 計算済みの要約表・推定結果表・整形済み報告表は原則 `knitr::kable()`、必要時のみ `gt`
8. 行数が多い探索表・データ閲覧表は `DT::datatable()`

## 意図的な例外

- `Rの基本的な使い方.qmd` の演習解答 fold は `解答例を表示` を維持する。
- 外部ソフトや toolchain の説明が中心になる章でも、setup 見出し自体は `## セットアップ` を使う。
- 後段の局所 helper chunk は `setup` 命名規則の対象外とする。
- `Rの基本的な使い方.qmd` では、`library()` 自体を説明対象にするコード例を維持する。
- `Rの基本的な使い方.qmd` のように、`gt` / `DT` / `kable` 自体の使い方を教える節では、その機能を示すための例示表を維持してよい。
- 章の主目的が表整形手法の比較である場合だけ、固定表であっても比較対象として `gt` や `knitr::kable()` を残してよい。

## 実施順

1. setup 層の構造統一  
   `required_packages`、`pacman` bootstrap、setup 見出し、chunk label、package-role prose、fold label
2. namespace 方針の統一  
   まず `dplyr::select()` と `dplyr::filter()` を優先
3. 描画 / 教材スタイルの統一  
   `theme_set()`、フォント、`library()` 方針を章横断で統一する
4. 実行オプションの統一  
   全 R コードチャンクの `eval` を明示し、Quarto pipe option に統一する
5. Quarto chunk option 記法の統一  
   旧式 header option を `#|` 形式へ移し、`echo` / `include` の役割を明文化する
6. コメント言語の統一  
   冗長な英語コメントを削減し、必要な説明コメントは日本語へ寄せる
7. 可視化テーマの再監査  
    `base_family` の欠落、`sans` 固定、章固有テーマの派生関係を再点検し、図テーマの一貫性を優先して整える
8. 色スケールの意味づけ統一  
    連続・発散・カテゴリで使う配色の役割を固定し、章内の outlier palette を減らす
9. ラベル可読性の改善  
   自由配置ラベルを `ggrepel` / `repel = TRUE` へ寄せ、ヒートマップ等の固定ラベルとは運用を分ける
10. 表出力ポリシーの統一  
   静的概念表は Markdown、標準的な計算結果表は `knitr::kable()`、高度整形が必要な結果表だけ `gt`、探索表は `DT` に寄せる
11. 章別の表移行  
   まず静的表を `gt` で出している章から順に、表の役割を崩さず Markdown 表へ移す

## 現在の状態

- フェーズ 1: 完了  
  setup 見出し、chunk label、package-role prose、fold label の標準化を反映済み
- フェーズ 2: 完了  
  `.qmd` の R コードチャンク内にある bare `select()` / `filter()` は `dplyr::select()` / `dplyr::filter()` へ置換済み
- フェーズ 3: 完了  
  `theme_set()` の標準化と、非教材コードの `library()` 排除を反映済み
- フェーズ 4: 完了  
  全 R コードチャンクで `eval` を明示し、旧式 `eval=...` 記法を除去済み
- フェーズ 5: 完了  
  旧式 chunk header option は除去済み。hidden bootstrap は `pre-setup` / `include: false`、visible setup は `setup` に整理済み
- フェーズ 6: 保留  
  コメント言語は二次優先とし、可視化の一貫性と可読性の改善を先行する
- フェーズ 7: 実施中  
  `theme_set()` の方針と実際の図テーマ運用を再監査中。まず `base_family` の欠落と `sans` 固定を整理する
- フェーズ 8: 実施中  
  色スケールの意味づけを統一中。まず発散尺度の青白赤系と、カテゴリ尺度の outlier palette を整理する
- フェーズ 9: 実施中  
  重なりやすい自由配置ラベルを優先して `ggrepel` / `repel = TRUE` に置き換え、注釈とデータラベルの役割を分ける
- フェーズ 10: 着手  
  表の出力ルールを計画に固定。次手で静的表を `gt` / `knitr::kable()` から Markdown へ章別に移行する
- フェーズ 11: 実施中  
  章ごとの表移行は、方針明文化後に代表的なズレのある章から順次実施する。2026-03-27 の 10 視点クロスチェックで、役割分担だけでなく backend / freeze 整合も別軸で監査する必要があると確認

## 完了基準（表ポリシー移行）

各章の状態は、少なくとも次の 4 条件で判定する。

- `role split done`: 静的な概念表・比較表・チェックリスト・ガイド・参照表は Markdown、標準的な計算結果・要約・パラメータ表は `knitr::kable()`、高度整形が必要な表だけ `gt`、探索表は `DT` に概ね分かれている
- `backend done`: 表出力が章ローカルの過剰なラッパーではなく、Markdown / `knitr::kable()` / `gt` / `DT` の標準手段で素直に出ている
- `artifact done`: `_freeze/.../html.json` と `_book/...html` が現行ソースと整合し、古い pipe table や壊れた `libs/...` 参照を引きずっていない
- `exception documented`: 教材章などで意図的に一般方針を外す場合、その理由が本文か計画書のどちらかに明記されている

`完了` は 4 条件が揃ったときだけ使う。途中状態は `役割分担完了`, `backend 未解消`, `artifact 要再確認`, `説明文のみ整合` のように分けて書く。

## 修正優先キュー（2026-03-28 再点検後）

### 直近バッチで解消した高優先負債

- 現在のバッチで [`2_ANOVAとカテゴリカル変数のコーディング.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/2_ANOVAとカテゴリカル変数のコーディング.qmd) の `book_gt()` は撤去済み  
  13 件の呼び出しを `knitr::kable()` に置き換え、`gt` への一律ラップを外した
- 現在のバッチで [`19_クラスタリング.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/19_クラスタリング.qmd) の `gt_light` alias は撤去済み  
  `gt_light <- gt::gt` とその呼び出しを外し、bare `gt()` 側へ戻した
- 現在のバッチで本文の表ポリシー説明と `actual gt` / `bare call` 系コメントは大半を除去済み  
  `13c`, `17`, `5`, `6`, `7`, `9`, `16`, `20`, `4`, `12`, `18`, `19` を優先処理した
- 現在のバッチで [`3_MANOVA_判別分析.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/3_MANOVA_判別分析.qmd), [`5_一般化線形モデル_一般化加法モデル.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/5_一般化線形モデル_一般化加法モデル.qmd), [`6_混合効果モデル_2値ロジスティック回帰.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/6_混合効果モデル_2値ロジスティック回帰.qmd), [`11_項目応答理論とラッシュモデル.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/11_項目応答理論とラッシュモデル.qmd), [`20_欠測データ解析とロバスト統計.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/20_欠測データ解析とロバスト統計.qmd) の `book_kable()` は撤去済み  
  136 件の呼び出しを素の `knitr::kable()` へ展開し、章ローカルの `kable` wrapper は source 上で 0 件になった
- 文字化けコメントの第一弾除去も完了  
  [`7_ベイズ推定.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/7_ベイズ推定.qmd), [`9_潜在変数モデリングと次元縮約.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/9_潜在変数モデリングと次元縮約.qmd), [`12_拡張ラッシュモデル.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/12_拡張ラッシュモデル.qmd), [`14_地理空間データ分析_入門.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/14_地理空間データ分析_入門.qmd) から 106 行を削除し、`モデル` のような残留 typo も補修した

### 現在の残件

- 通常章の主整理はほぼ完了  
  `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `13`, `13b`, `13c`, `14`, `15`, `16`, `18`, `20` は `gt=0 / DT=0` に整理済みで、本文側の表ポリシー説明もほぼ撤去した。表出力の論点は通常章から、例外章の最終固定へ移っている
- 例外章の扱いを固定する  
  `Rの基本的な使い方` は教材として `gt` チュートリアルと `DT` 実演を保持し、`12` は診断表 2 件、`17` はリーグテーブル 1 件、`19` は探索用途の `DT` 11 件を維持する。ここから先は「さらに削る」より「なぜ残すかを計画書側で固定する」段階である
- 公開品質の細部を保守する  
  文字化けコメント、読者に不要な実装メモ、placeholder の再流入を防ぐ。2026-03-28 時点では `????` 系の reader-visible コメントは source 上で 0 件まで除去済みで、残件は再発監視が中心である
- `_scripts/audit_table_policy.sh` を回帰防止に使う  
  code fence 内のみを数える形に補修済みで、`book_gt` / `book_kable` / `gt_light` の再発と、例外 helper の `rma_summary_tbl` / `compare_models_tbl` を分けて集計できる。次の用途は移行作業そのものより、継続的な監査である

### 例外として残すもの

- [`Rの基本的な使い方.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/Rの基本的な使い方.qmd)  
  `gt()` と `DT::datatable()` 自体を教える教材章なので、通常章と同じ縮小基準では扱わない。重複する応用表は `knitr::kable()` に戻したうえで、現時点では `gt` の tutorial block と `DT` の代表例 2 件だけを教材上の例外として維持する
- [`17_メタ分析.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/17_メタ分析.qmd) の `rma_summary_tbl()`  
  `rma_summary_tbl()` への分離は完了。今後はこの helper を tibble 抽出専用として維持し、描画は call site 側で明示する。表本体では NMA のリーグテーブル 1 件だけ `gt` を残す
- [`6_混合効果モデル_2値ロジスティック回帰.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/6_混合効果モデル_2値ロジスティック回帰.qmd) の `compare_models_tbl()`  
  `compare_models_tbl()` と描画レイヤへの分離は完了。今後は比較表の抽出と強調表示を分けて維持する
- [`12_拡張ラッシュモデル.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/12_拡張ラッシュモデル.qmd) の診断表 2 件  
  `Threshold Ordering Check (PCM)` と `PCM Item Fit Statistics (eRm: CML)` は、順序性や不適合項目を色・行強調で読む意味が残るため `gt` を維持する
- [`19_クラスタリング.qmd`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/19_クラスタリング.qmd) の `DT::datatable()` 群  
  試行ログ、クラスタ割当、テキストコーパス一覧の探索閲覧が主目的なので、意図的な `DT` 例外として維持する。ただし PCA負荷量や小さな集計表は縮小対象とし、現時点では探索用途の 11 件まで圧縮済み

## 自動棚卸し

- 追加スクリプト [`_scripts/audit_table_policy.sh`](/Users/tohokusla/Dropbox/ELE_Website_Statistics_Book/_scripts/audit_table_policy.sh) を使い、章ごとの `gt` / `DT` / `kable` / shim / Markdown 表 / freeze 痕跡を機械的に集計する
- 優先キューの更新前に、少なくとも一度このスクリプトを通して「説明」「実装」「freeze」の 3 つが揃っているかを確認する
- 特に `book_gt`, `book_kable`, `gt_light`, `rma_summary_tbl`, `compare_models_tbl` のような wrapper / helper / alias を警告信号として数えるように改修する  
  2026-03-28 の現行 source では `book_gt`, `book_kable`, `gt_light` は 0 件であることを前提に、再発検知に使う
- `libs/` や `Table:` の freeze 検出は誤警報が出やすいので、実害のある htmlwidget 参照と stale pipe table を分けて判定する
- 2026-03-28 時点の repo では、`knitr::kable()` への回帰と wrapper 撤去の主工程は完了した。したがって次フェーズは「公開品質補修」「例外章の固定」「監査スクリプトを使った回帰防止」を並行して進める

## 監査観点

- setup の説明と実際の package usage が一致しているか
- optional dependency と core dependency が混在していないか
- 教育上の例外が未記録のまま残っていないか
- 同じ機能を別の書き方で説明していないか
- 衝突しやすい関数が bare call のまま残っていないか
- 図の既定テーマが章ごとに不必要に分岐していないか
- 分析章の runtime code に不要な `library()` が残っていないか
- 実行するチャンクに `#| eval: true` が明示されているか
- `eval=...` の旧式 header option が残っていないか
- `message=FALSE` / `warning=FALSE` / `fig.height=` などの旧式 header option が残っていないか
- `echo: false` と `include: false` が役割どおりに使い分けられているか
- コメントが日本語本文と不整合な英語だらけになっていないか
- 章固有テーマが本書標準テーマから不必要に逸脱していないか
- `base_family` の欠落や `sans` 固定により、日本語図ラベルの見た目が章ごとにぶれていないか
- 連続尺度・発散尺度・カテゴリ尺度で、色の意味づけが章内でぶれていないか
- 自由配置ラベルが点やノードと重なって読みにくくなっていないか
- 補助注釈が主データを隠していないか
- 固定的な教育用表が `gt` や `DT` に流れていないか
- 計算結果表なのに Markdown 表へ潰して、脚注・整形・可読性を失っていないか
- 探索不要の小表に `DT::datatable()` を使っていないか
- `knitr::kable()` で十分な表に、不要に `gt` や `DT` を使っていないか
- 同じ役割の表が章ごとに別の出力手段で揺れていないか
