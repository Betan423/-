# MCP × Wazuh Threat Analysis 作業說明

## 一、作業背景與目的
本次作業的核心目標是**結合 Wazuh SIEM 與 MCP（Model Context Protocol）架構**，展示如何透過對話式（Chat-based）方式，協助使用者快速理解目前環境中的資安狀況，並進行基礎的威脅分析與決策輔助。

相較於傳統直接操作 Wazuh Dashboard 或 API，本作業嘗試將 **Wazuh 的警示資料轉換為 LLM 可理解的上下文（Context）**，再由模型協助進行摘要、風險判斷與後續行動建議，模擬未來 SOC / Threat Hunting Copilot 的使用情境。

---

## 二、整體架構說明

本專案包含三個主要組件：

1. **Wazuh SIEM**
   - 負責收集與儲存端點、系統與網路相關的安全事件
   - Alert 資料存放於 Wazuh Indexer（OpenSearch）

2. **MCP Server for Wazuh（既有專案）**
   - 提供標準化的 MCP tool 介面
   - 使 LLM 能以 tool-calling 方式查詢 Wazuh 狀態與資料

3. **自製 Python MCP Client / 分析腳本（本作業重點）**
   - 直接透過 Indexer API 取得警示資料
   - 將事件整理後送交 LLM 進行語意分析

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

```
.
├── mcp.json
├── get_wazuh_alerts.py
├── analyze_wazuh_alerts.py
└── README.md
```

### 1. mcp.json
此檔案為 **MCP Server 設定檔**，用於串接既有的 `mcp-server-wazuh` 專案，內容包含：

- Wazuh API 連線資訊
- Wazuh Indexer 連線資訊
- MCP Server 啟動設定

此設定使 MCP Client（如 Claude Desktop 或其他支援 MCP 的 LLM）能直接以 tool 方式查詢 Wazuh 資料。

> ⚠️ 注意：實際使用時，帳號密碼應改為環境變數或秘密管理機制，本作業為實驗用途。

---

### 2. get_wazuh_alerts.py

此腳本為**最基本的資料擷取工具**，功能如下：

- 直接呼叫 Wazuh Indexer（OpenSearch）API
- 擷取最新 10 筆安全警示
- 顯示以下欄位：
  - Agent 名稱
  - Rule 描述
  - Rule 等級（level）
  - 時間戳記

#### 設計目的

此腳本用來驗證：
- Indexer API 是否可正常存取
- Wazuh 警示資料格式與內容

可視為後續分析流程的資料基礎。

---

### 3. analyze_wazuh_alerts.py

此腳本為本作業的**核心實作**，展示如何將 Wazuh 警示資料轉換為 LLM 可理解的分析輸入。

#### 執行流程說明

**Step 1：警示擷取**
- 查詢 rule.level ≥ 5 的高風險事件
- 依時間排序，取得最新 10 筆
- 將事件整理為簡潔的文字摘要

**Step 2：LLM 分析**
- 將整理後的事件列表送交語言模型
- 要求模型輸出：
  1. 潛在高風險事件
  2. 是否存在異常行為模式
  3. 建議的後續安全檢查或行動

#### 設計重點

- **不直接讓 LLM 存取原始 PCAP 或 Log**
- 僅提供結構化後的事件摘要
- 降低幻覺（hallucination）風險
- 強調「輔助分析」而非自動決策

---

## 四、MCP 與本作業的關係

在本次作業中：

- `mcp.json`：
  - 展示如何整合現有 MCP Server for Wazuh
  - 提供完整的 MCP 工具化介面

- Python 腳本：
  - 作為 MCP 架構的「簡化版本」與概念驗證
  - 模擬 MCP tool 回傳結果後，再交由 LLM 進行推理

此設計有助於理解：
> MCP 的價值不在於「聊天」，而在於 **將安全資料工具化，並確保 LLM 的推理建立在真實資料之上**。

---

## 五、使用情境示例

- SOC 人員想快速了解目前高風險事件概況
- 教學或展示對話式 Threat Hunting 概念
- 作為未來整合 pfSense、EDR 或其他 SIEM 的基礎

---

## 六、限制與改進方向

### 已知限制
- 尚未實作自動化回應（Active Response）
- LLM 僅作摘要與建議，未進行事件關聯
- 金鑰與認證資訊未完全安全化

### 未來可改進項目
- 改為完整 MCP tool 呼叫流程
- 加入事件關聯（correlation）與時間窗分析
- 與 pfSense / IDS / EDR 事件進行跨層關聯
- 加入 Human-in-the-loop 回應流程

---

## 七、結論

本作業展示了一種 **結合 Wazuh、MCP 與 LLM 的實務型資安分析架構**，強調：

- 以真實 SIEM 資料為基礎
- 透過工具化（MCP）降低分析門檻
- 由 LLM 提供可解釋的輔助判斷

此設計不以取代 SOC 分析師為目標，而是作為 **決策輔助與理解加速工具**，符合實務環境對安全性與可控性的需求。

