# Setup Editorial Control Plan

Updated: 2026-03-27

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

## 標準パターン

1. 冒頭に `required_packages`
2. 必要時のみ hidden `pre-setup`
3. 章前半に `## セットアップ`
4. `### 主なパッケージの役割`
5. 必要な章のみ `### 追加の前提`

## 意図的な例外

- `Rの基本的な使い方.qmd` の演習解答 fold は `解答例を表示` を維持する。
- 外部ソフトや toolchain の説明が中心になる章でも、setup 見出し自体は `## セットアップ` を使う。
- 後段の局所 helper chunk は `setup` 命名規則の対象外とする。
- `Rの基本的な使い方.qmd` では、`library()` 自体を説明対象にするコード例を維持する。

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
