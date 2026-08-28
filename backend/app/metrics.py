from prometheus_client import Counter, Histogram, make_asgi_app

REQUESTS = Counter("tracerag_http_requests_total", "HTTP requests", ["method", "path", "status"])
QUERY_LATENCY = Histogram("tracerag_query_latency_seconds", "RAG query latency")
INGESTIONS = Counter("tracerag_documents_ingested_total", "Documents ingested")

metrics_app = make_asgi_app()
