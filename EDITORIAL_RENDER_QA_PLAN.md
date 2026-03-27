# Render QA Plan

Updated: 2026-03-27

## 目的

全 `.qmd` を一括ではなく単章ごとに render し、HTML 出力の実行可否と表示品質を章単位で確認する。

## 前提

- render は原則 `quarto render "<chapter>.qmd" --to html` で行う。
- Dropbox 同期は一時停止してから実行する。
- `_book`、`.quarto`、対象 HTML を RStudio / Positron / ブラウザ / Explorer で開きっぱなしにしない。
- `freeze: auto` と `cache: true` を前提に、問題が出た章だけ局所的に再実行する。

## 確認観点

1. render が完走し、対応する HTML が `_book` に生成されるか。
2. package / toolchain / 外部ソフト不足がある場合、必須欠落か任意節の graceful skip かを切り分けられるか。
3. 左 sidebar、右目次、本文幅、ページ下ナビ、コード fold、コピー、横スクロールが崩れていないか。
4. 図でラベル・注釈・凡例・facet・軸ラベル・色分けが読みやすいか。
5. `gt` / `DT` / 長い表が横にはみ出さず、caption と参照が一致しているか。
6. `plotly` / `leaflet` などの HTML widget が空白化せず、操作可能か。
7. 図番号・表番号・節番号・クロスリファレンスが壊れていないか。

## 章の優先順

### Phase 0: 事前確認

- Quarto / 出力先 / `_book` の状態確認
- ロック回避前提の確認

### Phase 1: ベースライン章

- `index.qmd`
- `Rの基本的な使い方.qmd`
- `1_T検定と効果量.qmd`
- `5_一般化線形モデル_一般化加法モデル.qmd`

### Phase 2: 可視化重点章

- `4_重回帰分析と交互作用.qmd`
- `9_潜在変数モデリングと次元縮約.qmd`
- `10_一般化可能性理論.qmd`
- `11_項目応答理論とラッシュモデル.qmd`
- `12_拡張ラッシュモデル.qmd`
- `16_ネットワーク分析.qmd`

### Phase 3: 時系列・音声・空間

- `13_時系列データ分析_基礎.qmd`
- `13b_時系列データ分析_発展.qmd`
- `13c_音声時系列分析_Praat.qmd`
- `14_地理空間データ分析_入門.qmd`
- `15_地理空間データ分析_応用.qmd`

### Phase 4: 重依存章

- `7_ベイズ推定.qmd`
- `8_予測分析_ROC曲線とツリーモデル.qmd`
- `17_メタ分析.qmd`

### Phase 5: 残り章

- `2_ANOVAとカテゴリカル変数のコーディング.qmd`
- `3_MANOVA_判別分析.qmd`
- `6_混合効果モデル_2値ロジスティック回帰.qmd`
- `18_統計的因果推論.qmd`
- `19_クラスタリング.qmd`
- `20_欠測データ解析とロバスト統計.qmd`
- `統計モデルについての概略.qmd`
- `参考文献_推薦書籍.qmd`

## 1章ごとの標準手順

1. 対象章を単独 render する。
2. render ログを `error` / `warning` / `optional skip` に分類する。
3. 生成 HTML の冒頭・中盤・末尾を確認する。
4. 章内で最も密な図を 3〜5 個確認する。
5. widget を含む章では実際に操作する。
6. `blocking` が出たら次章へ進まず、その章で修正する。

## 判定ラベル

- `OK`: render・表示ともに問題なし
- `minor fix`: render は通るが体裁や文言に小修正あり
- `blocking`: render 失敗、または主要な表示崩れあり

## 記録テンプレート

- Chapter:
- Render:
- Warnings:
- Layout:
- Figures:
- Tables:
- Widgets:
- Dependencies:
- Follow-up:
- Verdict:
