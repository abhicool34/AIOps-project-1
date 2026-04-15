# 🚀 AIOps Platform: Kubernetes + ELK + MCP + AI

This project demonstrates how to build a **real-world AIOps system** using free tools:

- Kubernetes (k3s on VMware)
- Fluent Bit (log collection)
- Elasticsearch + Kibana (ELK stack)
- MCP Server (API layer)
- AI-based log analysis, alerting, and auto-remediation

---

## 🧠 Architecture

```
K3s (VMware)
│
├── Application Pods
├── Fluent Bit (DaemonSet)
├── Elasticsearch (Local VM)
│   ├── Kibana (Visualization)
│   └── MCP Server (AI + API)
│       ├── Anomaly Detection
│       ├── Alerts
│       ├── Root Cause Analysis (RCA)
│       └── Auto Remediation
```

---

## 📦 Phase 1: Deploy Real Application (Logs Source)

### Goal

Generate structured logs for analysis.

### Deployment

Create a Kubernetes deployment manifest (`ai-demo-app.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-demo-app
  namespace: dev-env
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-demo-app
  template:
    metadata:
      labels:
        app: ai-demo-app
    spec:
      containers:
      - name: app
        image: python:3.9-slim
        command: ["/bin/sh"]
        args:
          - -c
          - |
            while true; do
              echo '{"level":"INFO","message":"App running","service":"ai-demo-app"}'
              sleep 2
              echo '{"level":"ERROR","message":"Database connection failed","service":"ai-demo-app"}'
              sleep 3
              echo '{"level":"WARNING","message":"High memory usage","service":"ai-demo-app"}'
              sleep 4
            done
```

### Deploy

```bash
kubectl apply -f ai-demo-app.yaml
```
---

## 📊 Phase 2: Logs → ELK Pipeline

### Goal

Flow logs from Kubernetes → Elasticsearch → Kibana

### Fluent Bit Configuration

```yaml
config:
  service: |
    [SERVICE]
        Flush        1
        Log_Level    info
        HTTP_Server  On
        HTTP_Listen  0.0.0.0
        HTTP_Port    2020

  inputs: |
    [INPUT]
        Name              tail
        Path              /var/log/containers/*.log
        Tag               kube.*
        multiline.parser  docker, cri

  filters: |
    [FILTER]
        Name                kubernetes
        Match               kube.*
        Merge_Log           On
        Keep_Log            On
        K8S-Logging.Parser  On

  outputs: |
    [OUTPUT]
        Name               es
        Match              kube.*
        Host               <ELASTICSEARCH_IP>
        Port               9200
        Logstash_Format    On
        Logstash_Prefix    logstash
        Suppress_Type_Name On
        Replace_Dots       On
        Retry_Limit        False
```

### Verify Logs in Elasticsearch

```bash
curl localhost:9200/_search?q=ai-demo-app&pretty
```

### Verify Logs in Kibana

1. Create Data View: `logstash-*`
2. Run Query: `kubernetes.pod_name : "ai-demo-app"`

---

## 🤖 Phase 3: AI Log Analyzer (MCP)

### Goal

Detect anomalies from logs using AI-powered analysis.

### MCP Server Implementation

```python
from fastapi import FastAPI
from elasticsearch import Elasticsearch

app = FastAPI()
es = Elasticsearch("http://localhost:9200")

@app.get("/ai/analyze")
def analyze():
    res = es.search(index="logstash-*", size=100)
    logs = [hit["_source"].get("log", "") for hit in res["hits"]["hits"]]
    
    errors = [l for l in logs if "error" in l.lower()]
    warnings = [l for l in logs if "warning" in l.lower()]
    
    insights = []
    
    if len(errors) > 5:
        insights.append("🚨 High error rate detected")
    
    if len(warnings) > 5:
        insights.append("⚠️ High warning rate")
    
    return {
        "errors": len(errors),
        "warnings": len(warnings),
        "insights": insights
    }
```

---

## 🚨 Phase 4: Alerts (Slack / Email)

### Goal

Notify DevOps team automatically when issues are detected.

### Slack Integration

```python
import requests

SLACK_WEBHOOK = "https://hooks.slack.com/services/XXXX"

def send_alert(msg):
    requests.post(SLACK_WEBHOOK, json={"text": msg})

# Trigger alert
if len(errors) > 5:
    send_alert("🚨 High error rate in ai-demo-app")
```

---

## 🧠 Phase 5: Auto Root Cause Analysis (RCA)

### Goal

Automatically identify the root cause of issues.

### RCA Implementation

```python
@app.get("/ai/rca")
def rca():
    res = es.search(index="logstash-*", size=100)
    logs = [hit["_source"].get("log", "") for hit in res["hits"]["hits"]]
    
    if any("database" in l.lower() for l in logs):
        return {"root_cause": "Database connectivity issue"}
    
    if any("memory" in l.lower() for l in logs):
        return {"root_cause": "High memory usage"}
    
    return {"root_cause": "Unknown"}
```

---

## 🔁 Phase 6: Auto Remediation

### Goal

Automatically fix issues without manual intervention.

### Auto Remediation Implementation

```python
import os

def restart_app():
    os.system("kubectl rollout restart deployment ai-demo-app -n dev-env")

# Trigger auto-remediation
if len(errors) > 10:
    restart_app()
```
---

## ⚠️ Common Issues & Troubleshooting

### ❌ Logs not visible in Kibana

- Check index exists: `logstash-*`
- Increase time range in Kibana UI
- Verify Elasticsearch is receiving logs

### ❌ Fluent Bit retry errors

- Check Elasticsearch connectivity
- Ensure correct Elasticsearch Host IP
- Verify port 9200 is accessible

### ❌ Index mapping conflict

```bash
curl -X DELETE "localhost:9200/logstash-*"
```

### ❌ Logs being dropped

Ensure the following in Fluent Bit configuration:
- `Keep_Log On`
- Sufficient buffer capacity
- Proper retry limits


---

## 📚 Key Learnings

| Concept | Explanation |
|---------|-------------|
| **Structured Logging** | Required for AI analysis and pattern recognition |
| **Fluent Bit** | Lightweight log collector and processor |
| **Elasticsearch** | Distributed search and analytics engine for log storage |
| **Kibana** | Visualization and exploration platform for logs |
| **MCP Server** | API layer for AI-powered analysis and automation |
| **AIOps** | Combines automation and artificial intelligence for operations |

---

## 📝 Notes

- Ensure all services are properly networked and can communicate
- Use appropriate resource limits for Kubernetes deployments
- Regularly monitor Elasticsearch disk space and performance
- Implement proper authentication in production environments