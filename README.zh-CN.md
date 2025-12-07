# 🇨🇳 ECU Simulator —— 汽车诊断 ECU 模拟器

**ECU Simulator** 是一个基于 **Python** 构建的、可扩展的 **UDS（ISO 14229）诊断 ECU 模拟器**。
项目目前支持常见UDS 服务、会话管理、安全访问认证、DID/RID 配置化、以及虚拟 CAN通信。

---

## 🌐 语言 / Languages

[English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja.md)

---

# 🚗 概要

本项目旨在创造一个通用的ECU仿真平台，目的是实现以下核心特点：

- **可配置**：通过配置文件添加或删除DID/RID
- **易扩展**：可集成自定义功能
- **接近量产ECU**：模拟真实ECU逻辑
- **拥有易操作的联动能力**：提供一个拥有GUI的Tester方便诊断测试

适用于：

- ECU 开发工程师
- 诊断测试工程师（黑盒/白盒）
- Python 工具/脚本开发者
- UDS 领域学习者
- 自动化测试平台搭建

---

# ✨ 功能特点

### 🟦 诊断服务
支持以下常用服务：

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

SID 采用自动扫描和动态注册机制，只需按文件名约定即可新增服务。

---

### 🟩 配置驱动 DID/RID

DID/RID 配置基于 YAML/JSON文件驱动，支持一下多种类型：
- 静态DID: 固定返回配置中定义的值
- 函数DID：通过配置链接到对应的回调函数，用于实时生成或获取动态数据
- 复合DID：支持将多个静态或动态字段按字节范围组合打包返回，以支持复杂的 DID 结构

---

### 🟨 GUI 操作界面（Tkinter）

内置简单GUI界面
- 实时发送/接收消息
- Session、Security等ECU数据的可视化
- 通过 GUI 模拟唤醒/休眠、车辆状态等外部输入，可以驱动 ECU 进入不同状态。
- 动态 CAN 流日志显示
- GUI集成简易Tester，支持手动输入 CAN 报文或通过下拉菜单选择
---

### 🟪 虚拟 CAN 总线支持

- 基于 python-can VirtualBus
- 无需任何真实 CAN 设备
- 结果可复现、可回放

---

# 🧩 项目结构

---

# ⚙️ 安装方法

### 1️⃣ 克隆仓库
```
git clone https://github.com/JiaxiaoH/ecu-simulator.git
cd ecu-simulator-main
```

---

### 2️⃣ 安装依赖


---

# 🚀 使用方法

### 1️⃣ 启动 ECU 模拟器
```
python main.py
```

### 2️⃣ 调整 ECU 状态
```
启动电源，调整车辆运行条件，修改DTC
```

### 3️⃣ 发送报文
```
双击文本框选择或手动输入需要 Tester 发送的 CAN 报文
```

### 4️⃣ 确认结果
```
通过 GUI 确定 ECU 的响应
```
---

# 📄 示例（SID 10）

请求：
```
10 03
```

响应：
```
50 03 00 32 01 F4
```

---

# 🧑‍💻 开发说明

可扩展内容：

- 新增 SID
- 新增 DID/RID

---

# 📝 开源协议

MIT License
