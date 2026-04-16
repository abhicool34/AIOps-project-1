from fastapi import FastAPI
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import requests

app = FastAPI()

# Connect to Elasticsearch (local VM)
es = Elasticsearch("http://localhost:9200")

# ✅ Health check
@app.get("/")
def home():
    return {"message": "MCP Server Running"}

# 🔹 Get recent logs
@app.get("/logs")
def get_logs():
    res = es.search(
        index="logstash-*",
        size=20,
        sort=[{"@timestamp": {"order": "desc"}}]
    )
    return [hit["_source"] for hit in res["hits"]["hits"]]


# 🔹 Get logs by pod
@app.get("/logs/{pod_name}")
def logs_by_pod(pod_name: str):
    query = {
        "query": {
            "match": {
                "kubernetes.pod_name": pod_name
            }
        }
    }

    res = es.search(index="logstash-*", body=query, size=20)
    return [hit["_source"] for hit in res["hits"]["hits"]]


# 🔹 Get errors (last 10 min)
@app.get("/errors")
def get_errors():
    now = datetime.utcnow()
    past = now - timedelta(minutes=10)

    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"log": "error"}},
                    {
                        "range": {
                            "@timestamp": {
                                "gte": past.isoformat(),
                                "lte": now.isoformat()
                            }
                        }
                    }
                ]
            }
        }
    }

    res = es.search(index="logstash-*", body=query, size=50)
    return [hit["_source"] for hit in res["hits"]["hits"]]


# 🔹 Top pods by log volume
@app.get("/top-pods")
def top_pods():
    query = {
        "size": 0,
        "aggs": {
            "pods": {
                "terms": {
                    "field": "kubernetes.pod_name.keyword",
                    "size": 5
                }
            }
        }
    }

    res = es.search(index="logstash-*", body=query)
    return res["aggregations"]["pods"]["buckets"]


# 🔹 Simple AI-like analysis
@app.get("/analyze")
def analyze():
    res = es.search(index="logstash-*", size=50)

    logs = [hit["_source"].get("log", "") for hit in res["hits"]["hits"]]

    errors = [l for l in logs if "error" in l.lower()]

    return {
        "total_logs": len(logs),
        "error_count": len(errors),
        "sample_errors": errors[:5]
    }

@app.get("/ai/analyze")
def ai_analyze():
    res = es.search(index="logstash-*", size=100)

    logs = [hit["_source"].get("log", "") for hit in res["hits"]["hits"]]

    error_count = sum(1 for l in logs if "error" in l.lower())
    warning_count = sum(1 for l in logs if "warning" in l.lower())

    insights = []

    if error_count > 5:
        insights.append("High error rate detected 🚨 Possible application failure")

    if warning_count > 5:
        insights.append("Frequent warnings ⚠️ Check resource usage")

    if error_count == 0:
        insights.append("System healthy ✅")

    return {
        "total_logs": len(logs),
        "errors": error_count,
        "warnings": warning_count,
        "insights": insights
    }

@app.get("/ai/rca")
def rca():
    res = es.search(index="logstash-*", size=100)

    logs = [hit["_source"].get("log", "") for hit in res["hits"]["hits"]]

    if any("database" in l.lower() for l in logs):
        return {"root_cause": "Database connectivity issue"}

    if any("memory" in l.lower() for l in logs):
        return {"root_cause": "High memory usage"}

    return {"root_cause": "Unknown"}

@app.get("/ai/analyze-advanced")
def analyze_advanced():
    res = es.search(index="logstash-*", size=200)

    logs = [hit["_source"] for hit in res["hits"]["hits"]]

    error_logs = []
    slow_logs = []

    for log in logs:
        message = log.get("log", "").lower()

        if "error" in message or "500" in message:
            error_logs.append(message)

        if "timeout" in message or "slow" in message:
            slow_logs.append(message)

    return {
        "total_logs": len(logs),
        "error_count": len(error_logs),
        "slow_issues": len(slow_logs),
        "insights": [
            "High 5xx errors detected" if len(error_logs) > 5 else "Healthy",
            "Performance degradation" if len(slow_logs) > 3 else "Normal"
        ]
    }

@app.get("/ai/anomaly")
def anomaly():
    res = es.search(index="logstash-*", size=500)

    logs = res["hits"]["hits"]

    error_count = sum(1 for l in logs if "error" in str(l).lower())

    if error_count > 20:
        return {"anomaly": "Spike in errors 🚨"}

    return {"anomaly": "Normal"}

@app.get("/ai/rca-advanced")
def rca_advanced():
    res = es.search(index="logstash-*", size=200)

    logs = [hit["_source"].get("log", "") for hit in res["hits"]["hits"]]

    causes = {}

    for log in logs:
        if "connection refused" in log.lower():
            causes["network"] = causes.get("network", 0) + 1

        if "timeout" in log.lower():
            causes["timeout"] = causes.get("timeout", 0) + 1

        if "memory" in log.lower():
            causes["memory"] = causes.get("memory", 0) + 1

    return {"root_causes": causes}

def ask_ai(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt}
    )
    return response.json()["response"]

@app.get("/ai/llm-analysis")
def llm_analysis():
    res = es.search(index="logstash-*", size=50)

    logs = [hit["_source"].get("log", "") for hit in res["hits"]["hits"]]

    prompt = f"""
    Analyze these logs and:
    - detect issues
    - find root cause
    - suggest fixes

    Logs:
    {logs}
    """

    return {"analysis": ask_ai(prompt)}