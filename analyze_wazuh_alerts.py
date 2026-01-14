import requests
from requests.auth import HTTPBasicAuth
import json

# === 基本設定 ===
INDEXER_URL = "https://localhost:9200/wazuh-alerts-*/_search"
USERNAME = "admin"   # Wazuh indexer 的帳號
PASSWORD = "Qs.D1Xw7.7rCJyfMSo1LEtm2RTqfZLV."  # 可從 /etc/wazuh-indexer/opensearch-security/internal_users.yml 取得
VERIFY_SSL = False

# === AI 模型設定 ===
# ⚠️ 請在執行環境設定 OPENAI_API_KEY 環境變數，或直接填在這裡（測試用途）
OPENAI_API_KEY = "sk-"
OPENAI_URL = ""
MODEL = "gpt-4.1-mini"   # 或其他支援模型


# === Step 1: 從 Wazuh Indexer 取得最新 alerts ===
query = {
    "query": {
        "range": {
            "rule.level": {"gte": 5}
        }
    },
    "sort": [{"timestamp": {"order": "desc"}}],
    "size": 10,
    "_source": ["agent.name", "rule.description", "rule.level", "timestamp"]
}

response = requests.get(
    INDEXER_URL,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    params={"pretty": "true"},
    json=query,
    verify=VERIFY_SSL
)

if response.status_code != 200:
    print(f"[!] Indexer API error {response.status_code}: {response.text}")
    exit(1)

data = response.json()
hits = data.get("hits", {}).get("hits", [])

alerts_text = []
for hit in hits:
    src = hit["_source"]
    line = f"{src.get('timestamp')} | {src.get('agent', {}).get('name')} | Level {src.get('rule', {}).get('level')} | {src.get('rule', {}).get('description')}"
    alerts_text.append(line)

if not alerts_text:
    print("⚠️ 沒有找到任何警告事件。")
    exit(0)

print("\n📋 收集到的最近事件：")
print("\n".join(alerts_text))

# === Step 2: 將 alerts 傳送給 AI 模型做分析 ===
prompt = f"""
以下是最近從 Wazuh 收集的 10 筆安全事件：

{json.dumps(alerts_text, ensure_ascii=False, indent=2)}

請你幫我做一個安全事件摘要分析，包含：
1. 哪些事件看起來最危險？
2. 是否出現異常行為模式？
3. 建議的安全檢查或後續行動。
請用中文給出一份簡短報告。
"""

headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

ai_payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "你是一名資安分析師，熟悉 Wazuh、Windows 事件日誌與攻擊行為分析。"},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.5
}

print("\n🤖 正在分析中...\n")
ai_response = requests.post(OPENAI_URL, headers=headers, json=ai_payload)

if ai_response.status_code == 200:
    analysis = ai_response.json()["choices"][0]["message"]["content"]
    print("===== 🔎 AI 分析報告 =====")
    print(analysis)
else:
    print(f"[!] AI API error {ai_response.status_code}: {ai_response.text}")

