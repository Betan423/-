# MCP × Wazuh Threat Analysis 作業說明

## 一、作業背景與目的

本次作業的核心目標是**結合 Wazuh SIEM 與 MCP（Model Context Protocol）架構**，展示如何透過對話式（Chat-based）方式，協助使用者快速理解目前環境中的資安狀況，並進行基礎的威脅分析與決策輔助。

相較於傳統直接操作 Wazuh Dashboard 或 API，本作業嘗試將 **Wazuh 的警示資料轉換為 LLM 可理解的上下文（Context）**，再由模型協助進行摘要、風險判斷與後續行動建議，模擬未來 SOC / Threat Hunting Copilot 的使用情境。

---

## 二、整體架構說明

本專案包含三個主要組件：

1. **Wazuh SIEM**

   * 負責收集與儲存端點、系統與網路相關的安全事件
   * Alert 資料存放於 Wazuh Indexer（OpenSearch）

2. **MCP Server for Wazuh（既有專案）**

   * 提供標準化的 MCP tool 介面
   * 使 LLM 能以 tool-calling 方式查詢 Wazuh 狀態與資料

3. **自製 Python MCP Client / 分析腳本（本作業重點）**

   * 直接透過 Indexer API 取得警示資料
   * 將事件整理後送交 LLM 進行語意分析

```
[ Wazuh Agents ]
        ↓
[ Wazuh Manager / Indexer ]
        ↓
[ Python MCP Scripts ]
        ↓
[ LLM 分析與摘要 ]
```

---

## 三、檔案結構說明

> **重要說明（本作業設計重點）**
> 本專案刻意區分為「**既有 MCP Server 的實際配置**」與「**自行實作的 MCP 概念版本**」兩個部分，
> 目的在於對照 *現成 MCP 工具化方案* 與 *自行從零實作的學習成果*，
> 並展示對 MCP 架構的理解，而非僅使用現成工具。

```
.
├── mcp.json                      # 現有 Wazuh MCP Server 的設定檔（非自行實作）
├── get_wazuh_alerts.py           # 自行撰寫：學期初的 Wazuh MCP 概念實作（資料擷取）
├── analyze_wazuh_alerts.py       # 自行撰寫：學期初的 Wazuh MCP 概念實作（分析推理）
└── README.md
```

### 1. mcp.json（**現有 Wazuh MCP Server 的設定檔**）

此檔案**並非自行實作 MCP Server**，而是用於設定與啟動 **既有 GitHub 專案：Wazuh MCP Server** 的組態檔，
用來說明「**若直接採用現成 MCP Server，應如何正確配置 Wazuh 環境**」。

#### 本檔案的角色定位

* 作為 **現有 MCP Server for Wazuh 的實際設定範例**
* 說明 MCP Server 如何連線至：

  * Wazuh API
  * Wazuh Indexer（OpenSearch）
* 驗證 MCP 架構在真實環境中可行

#### 設定內容重點

* WAZUH_API_HOST / PORT：Wazuh Manager API
* WAZUH_INDEXER_HOST / PORT：Indexer 查詢來源
* WAZUH_VERIFY_SSL：測試環境中關閉 SSL 驗證
* RUST_LOG：MCP Server 執行時的除錯層級

> 📌 本檔案的用途在於「**理解與操作現成 MCP Server 的設定方式**」，
> 而非展示 MCP Server 的內部實作。

> ⚠️ 注意：實際使用時，帳號密碼應改為環境變數或秘密管理機制，本作業為實驗用途。

---

### 2. get_wazuh_alerts.py（**自行實作：MCP 概念版・資料擷取層**）

此 Python 腳本為**學期初自行撰寫的 MCP 概念實作版本**之一，
目的在於在尚未接觸正式 MCP Server 前，
自行理解並實作「**模型如何取得安全上下文（Context）**」的流程。

#### 設計背景

在本課程前期，尚未使用現成 MCP Server，
因此以 Python 直接存取 Wazuh Indexer API，
模擬 MCP tool 中「資料查詢」的角色。

#### 腳本功能

* 直接呼叫 OpenSearch API
* 擷取最新 10 筆 Wazuh Alerts
* 將原始 JSON 結果轉為人類可讀的摘要輸出

#### MCP 對應概念

| MCP 架構角色    | 本腳本對應功能        |
| ----------- | -------------- |
| Tool        | 查詢 Indexer API |
| Tool Output | 結構化事件摘要        |
| Context     | 提供後續分析使用       |

> 📌 此腳本不包含 AI 推理，
> 專注於「**正確取得與整理安全事件上下文**」。

---

### 3. analyze_wazuh_alerts.py（**自行實作：MCP 概念版・推理分析層**）

此腳本為另一個**完全自行撰寫的 MCP 概念實作元件**，
展示如何在不使用正式 MCP Server 的情況下，
自行完成「Context → Reasoning → Recommendation」的流程。

#### 與 get_wazuh_alerts.py 的關係

* `get_wazuh_alerts.py`：負責 **Context 取得**
* `analyze_wazuh_alerts.py`：負責 **Context 理解與分析**

此設計刻意拆分資料擷取與分析邏輯，
以符合 MCP 中「tool 與 model 解耦」的精神。

#### 腳本流程說明

**Step 1：高風險事件篩選**

* 查詢 rule.level ≥ 5
* 聚焦於可能需要人工關注的事件

**Step 2：上下文建構（Context Building）**

* 將事件轉換為簡潔、結構化的文字列表
* 避免直接餵給模型過多原始資料

**Step 3：語言模型分析（Reasoning）**

* 要求模型扮演資安分析師
* 輸出摘要、風險判斷與建議行動

#### MCP 對應概念

| MCP 架構角色 | 本腳本對應功能    |
| -------- | ---------- |
| Context  | Alert 摘要列表 |
| Model    | LLM 分析推理   |
| Output   | 人類可理解的報告   |

> 📌 此腳本的重點在於 **理解 MCP 的設計哲學**，
> 而非追求自動化回應或完整 SOC 系統。

---

## 四、MCP 與本作業的關係

在本次作業中：

* `mcp.json`：

  * 展示如何整合現有 MCP Server for Wazuh
  * 提供完整的 MCP 工具化介面

* Python 腳本：

  * 作為 MCP 架構的「簡化版本」與概念驗證
  * 模擬 MCP tool 回傳結果後，再交由 LLM 進行推理

此設計有助於理解：

> MCP 的價值不在於「聊天」，而在於 **將安全資料工具化，並確保 LLM 的推理建立在真實資料之上**。

---

## 五、使用情境示例

* SOC 人員想快速了解目前高風險事件概況
* 教學或展示對話式 Threat Hunting 概念
* 作為未來整合 pfSense、EDR 或其他 SIEM 的基礎

---

## 六、限制與改進方向

### 已知限制

* 尚未實作自動化回應（Active Response）
* LLM 僅作摘要與建議，未進行事件關聯
* 金鑰與認證資訊未完全安全化

### 未來可改進項目

* 改為完整 MCP tool 呼叫流程
* 加入事件關聯（correlation）與時間窗分析
* 與 pfSense / IDS / EDR 事件進行跨層關聯
* 加入 Human-in-the-loop 回應流程

---

## 七、結論

本作業展示了一種 **結合 Wazuh、MCP 與 LLM 的實務型資安分析架構**，強調：

* 以真實 SIEM 資料為基礎
* 透過工具化（MCP）降低分析門檻
* 由 LLM 提供可解釋的輔助判斷

此設計不以取代 SOC 分析師為目標，而是作為 **決策輔助與理解加速工具**，符合實務環境對安全性與可控性的需求。
