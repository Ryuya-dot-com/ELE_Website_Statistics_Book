# t検定と効果量：プロンプトとステップ

## まず確認するヒアリング項目

- デザイン：独立2群／対応あり（同一参加者の前後）／一対比較
- 方向の定義：何が「有利（正）」か（本書は正=介入有利）
- 前提：正規性・等分散性（Welchの使用可否）、外れ値の有無
- 出力：検定表（gt）、効果量（d/g/Glass Δ/paired d）、図（箱ひげ/平均CI）

## コア・プロンプト（テンプレート）

```
Rでt検定と効果量を一括して出したいです。
条件:
- デザイン: <独立2群 / 対応あり>
- 目的: <例: Writing vs Glossing の比較 / Immediate vs Delayed の比較>
- 方向: 正=介入有利
- 出力: t検定の統計量と95%CI、Cohen's d（Hedges g/Glass Δも）、対応ありならpaired d

要望:
1) 前提チェック（正規性/等分散）とWelchへのフォールバック
2) effectsizeパッケージで d/g/Δ を算出（gt表で整形）
3) 箱ひげ図と平均+95%CIの図を作成
4) レポート書式の例（d = 値, 95% CI [lb, ub]）
```

## ステップ・チェックリスト

- データ整形：独立2群→`y ~ group`、対応あり→wideへ変換して `paired=TRUE`
- 検定：`t.test(..., var.equal=TRUE/FALSE)`（Welch併用）
- 効果量：`cohens_d()`、`hedges_g()`、`glass_delta()`、`cohens_d(..., paired=TRUE)`
- 表：`gt` で小数桁・CI・注記（方向の定義）を整える
- 図：外れ値や分布を併記し、誤読を防ぐ
- 接続：メタ分析用に `metafor::escalc(measure="SMDH")` でyi/viも保存

## よくある落とし穴

- 符号の逆転：基準群の取り方を固定（正=介入有利）
- 分散の違い：分散が大きく異なるならGlass Δ、検定はWelchへ
- 対応あり：差分のSDで標準化（`paired=TRUE`）にすること
