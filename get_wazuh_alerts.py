import requests
from requests.auth import HTTPBasicAuth

# === 設定區 ===
INDEXER_URL = "https://localhost:9200/wazuh-alerts-*/_search"
USERNAME = "admin"   # Wazuh indexer 的帳號
PASSWORD = "Qs.D1Xw7.7rCJyfMSo1LEtm2RTqfZLV."  # 可從 /etc/wazuh-indexer/opensearch-security/internal_users.yml 取得
VERIFY_SSL = False    # 如果是測試環境，可先關閉 SSL 驗證

# === 查詢條件 ===
query = {
    "size": 10,  # 抓最新 10 筆
    "sort": [{"timestamp": {"order": "desc"}}],
    "_source": ["agent.name", "rule.description", "rule.level", "timestamp"]
}

# === 向 indexer 發送請求 ===
response = requests.get(
    INDEXER_URL,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    params={"pretty": "true"},
    json=query,
    verify=VERIFY_SSL
)

# === 處理回應 ===
if response.status_code == 200:
    data = response.json()
    hits = data.get("hits", {}).get("hits", [])
    print(f"共找到 {len(hits)} 筆警告：\n")

    for hit in hits:
        source = hit["_source"]
        agent = source.get("agent", {}).get("name", "N/A")
        rule = source.get("rule", {}).get("description", "N/A")
        level = source.get("rule", {}).get("level", "N/A")
        timestamp = source.get("timestamp", "N/A")

        print(f"[{timestamp}] ({agent}) 等級 {level}: {rule}")
else:
    print(f"API 錯誤 {response.status_code}: {response.text}")

