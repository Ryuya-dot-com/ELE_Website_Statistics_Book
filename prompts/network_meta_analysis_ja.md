# ネットワークメタ分析（NMA）：プロンプトとステップ

## まず確認するヒアリング項目

- 介入の集合と基準群（reference）
- アウトカム型（連続=SMD/MD、二値=logOR/logRR）
- 試験構成（2群/3群などの多腕あり）と効果修飾因子（transitivity）
- 出力：ネットワーク図、基準群に対するforest、リーグ表、P-scores、整合性検定
  - 追加: comparison-adjusted funnel（小規模研究バイアス）, netheat（不整合ヒートマップ）

## コア・プロンプト（テンプレート）

```
Rのnetmetaで頻度論的NMAを行いたいです。CTRL, GLOSS, WRIT, SRS の4介入、連続アウトカム（SMD）です。

要件:
- データ: study×armのwide形式（最大3腕）から `pairwise()` → `netmeta()`
- 参照群: CTRL、tau推定: REML、random効果
- 図: `netgraph()`（英語ラベル）, `forest()`（vs CTRL）
- 表: `netleague()`（リーグ表）, `netrank()`（P-scores）
- 検定: `decomp.design()`（global）, `netsplit()`（local）

注意:
- 文字化け回避のため図表のラベルは英語、解説は本文に日本語で
- 多腕の相関は `pairwise()` に一任、欠損はNAのままでOK
```

## ステップ・チェックリスト

- データを wide に整える（study, treat1..k, mean1..k, sd1..k, n1..k）
- 二値の場合は `event1..k` と `n1..k` を用い、`sm = "OR"/"RR"` を選択
- `pairwise()` で効果量とSEを抽出（`sm = "SMD"/"MD"/"OR"/"RR"）
- `netmeta()` でNMAを適合（`reference.group`の指定）
- `netgraph()`/`forest()`/`netleague()`/`netrank()`/`decomp.design()`/`netsplit()` を作成
- 追加（任意）: `funnel(net)`（comparison-adjusted）、`netheat(net)`（整合性の可視化）
- 可視化の発展: P-score の棒グラフ（`ggplot2`）、node-splittingの散布図（direct vs indirect）
- 解釈：ランキング差の大小、整合性、リーグ表の方向（row vs column）
