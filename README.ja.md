# 🇨🇳 ECU Simulator —— 車載診断 ECU シミュレーター

**ECU Simulator**は、**Python** で構築された拡張可能な**UDS（ISO 14229）ダイアグ ECU シミュレーター**。
本プロジェクトは現在、一般的な UDS サービス、セッション管理、セキュリティアクセス、DID/RID の設定、仮想 CAN 通信をサポートしている。

---

## 🌐 言語 / Languages

[English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja.md)

---

# 🚗 概要

本プロジェクトは、以下の特徴を備えた汎用 ECU シミュレーションプラットフォームを目指している。

- **設定可能**：DID/RID をコンフィグファイルで追加・削除可能
- **拡張可能**：独自機能の組み込みに対応
- **量産 ECU に近い挙動**：実 ECU ロジックのシミュレーション
- **高い操作性**：GUI によりテストを容易に実施可能

適用：

- ECU 開発エンジニア
- テストエンジニア（ブラックボックス/ホワイトボックス）
- Python ツール開発者
- UDS の勉強
- 自動テスト基盤の構築

---

# ✨ 特徴   

### 🟦 ダイアグサービス
以下の一般的なサービスIDをサポート：

- 0x10 Diagnostic Session Control
- 0x11 ECU Reset
- 0x14 Clear Diagnostic Information
- 0x19 Read DTC Information
- 0x22 Read Data By Identifier
- 0x27 Security Access
- 0x28 Communication Control
- 0x29 Authentication
- 0x2E Write Data By Identifier
- 0x31 Routine Control
- 0x3E Tester Present
- 0x85 Control DTC Setting

SID は自動スキャン・動的登録方式を採用しており、ファイル名の規約に従うだけでサービスを追加できる。

---

### 🟩 構成駆動型設計 DID/RID

DID/RID の定義は YAML/JSON の設定ファイルにより管理される。
以下のタイプに対応：
- スタティック DID: 固定値を返送
- ファンクション DID：コールバックファンクションで値を生成
- コンポジット DID：複数フィールドを結合し複雑な DID 形式に対応

---

### 🟨 GUI インターフェース（Tkinter）

簡易 GUI を実装し、以下をサポート：
- 送受信メッセージのリアルタイム表示
- セッション、セキュリティ、DTC など ECU 状態の可視化
- 電源 ON/OFF、車両状態、スリープ/ウェイクアップのシミュレーション
- CAN ログのリアルタイム表示
- マニュアル入力またはリスト選択可能な簡易テスター
---

### 🟪 仮想 CAN バス

- python-can VirtualBus を使用
- 物理 CAN デバイスは不要
- シミュレーションの再現性が高く、再実行も容易

---

# 🧩 システムアーキテクト

---

# ⚙️ インストール

### 1️⃣ クローン
```
git clone https://github.com/JiaxiaoH/ecu-simulator.git
cd ecu-simulator-main
```

---

### 2️⃣ 依存関係インストール
```
pip install -r requirements.txt
```

---

# 🚀 使い方

### 1️⃣ ECU シミュレータ開始
```
python main.py
```

### 2️⃣ ECU 状態調整
```
電源、車両走行状態、DTC などを GUI から調整
```

### 3️⃣ メッセージを送信
```
エントリーをダブルクリック、またはマニュアル入力して CAN メッセージを送信
```

### 4️⃣ 結果確認
```
GUI で ECU のレスポンスを確認
```
---

# 📄 例（SID 10）

リクエスト：
```
10 03
```

レスポンス：
```
50 03 00 32 01 F4
```

---

# 🧑‍💻 開発者向け

拡張可能な内容：

- SID の追加
- DID/RID の追加

---

# 📝 ライセンス

MIT License
