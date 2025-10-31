"""Real-world scenario datasets for LLM benchmarking.

This module provides datasets that mirror actual production LLM use cases:
1. RAG (Retrieval-Augmented Generation) - Technical documentation Q&A
2. Code Generation - Programming tasks with context
3. Customer Support - Multi-turn conversation scenarios
4. Data Analysis - Complex analytical queries on business data
5. Multi-document Reasoning - Cross-reference and synthesis tasks

All datasets use seeded randomness for reproducibility.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


def _get_faker() -> Any:
    """Return a seeded Faker instance (seed=54321 for real-world scenarios)."""
    try:
        from faker import Faker  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Dataset generation requires 'faker'. Install with: pip install faker"
        ) from exc
    Faker.seed(54321)  # Different seed from main benchmarks
    return Faker()


def generate_rag_documentation_dataset() -> dict[str, Any]:
    """Generate technical documentation for RAG Q&A scenarios.
    
    Simulates API documentation, user guides, and technical specs that would be
    used in a production RAG system. Tests LLM's ability to extract specific
    information from structured documentation.
    
    Returns:
        Dict with 'documents' list containing technical documentation entries.
    """
    documents = [
        {
            "id": "api-auth-001",
            "title": "Authentication API",
            "category": "API Reference",
            "content": "The Authentication API uses OAuth 2.0 for secure access. "
                      "To authenticate, send a POST request to /api/v2/auth/token with "
                      "client_id and client_secret in the request body. The API returns "
                      "an access_token valid for 3600 seconds and a refresh_token valid "
                      "for 30 days. Rate limit: 100 requests per minute per IP address.",
            "version": "2.0",
            "lastUpdated": "2025-10-15",
            "tags": ["authentication", "oauth", "security"],
        },
        {
            "id": "api-users-002",
            "title": "User Management API",
            "category": "API Reference",
            "content": "The User Management API allows CRUD operations on user accounts. "
                      "GET /api/v2/users/{id} retrieves user details. POST /api/v2/users "
                      "creates a new user (requires admin role). PUT /api/v2/users/{id} "
                      "updates user information. DELETE /api/v2/users/{id} soft-deletes "
                      "a user account. All endpoints require Bearer token authentication. "
                      "Maximum payload size: 5MB.",
            "version": "2.0",
            "lastUpdated": "2025-10-20",
            "tags": ["users", "crud", "management"],
        },
        {
            "id": "guide-setup-003",
            "title": "Quick Start Guide",
            "category": "User Guide",
            "content": "To get started: 1) Install the SDK using 'npm install @company/sdk' "
                      "or 'pip install company-sdk'. 2) Initialize with your API key: "
                      "const client = new Client({apiKey: 'your-key'}). 3) Make your first "
                      "API call: await client.users.list(). The SDK supports Node.js 18+, "
                      "Python 3.9+, and Java 11+. For production use, enable retry logic "
                      "and set timeout to 30 seconds.",
            "version": "1.0",
            "lastUpdated": "2025-09-30",
            "tags": ["getting-started", "sdk", "installation"],
        },
        {
            "id": "guide-errors-004",
            "title": "Error Handling Guide",
            "category": "User Guide",
            "content": "Common error codes: 400 (Bad Request) - Invalid input parameters. "
                      "401 (Unauthorized) - Missing or invalid authentication token. "
                      "403 (Forbidden) - Insufficient permissions for the requested resource. "
                      "404 (Not Found) - Resource does not exist. 429 (Too Many Requests) - "
                      "Rate limit exceeded, retry after 60 seconds. 500 (Internal Server Error) - "
                      "Server error, contact support if persists. All errors return JSON with "
                      "'error', 'message', and 'requestId' fields.",
            "version": "1.0",
            "lastUpdated": "2025-10-01",
            "tags": ["errors", "troubleshooting", "http-codes"],
        },
        {
            "id": "spec-database-005",
            "title": "Database Schema Specification",
            "category": "Technical Spec",
            "content": "The primary database uses PostgreSQL 15.2 with the following schema: "
                      "users table (id UUID primary key, email VARCHAR(255) unique, "
                      "created_at TIMESTAMP, role VARCHAR(50)). orders table (id UUID primary key, "
                      "user_id UUID foreign key, total DECIMAL(10,2), status VARCHAR(20), "
                      "created_at TIMESTAMP). Indexes: users.email (B-tree), orders.user_id (B-tree), "
                      "orders.created_at (B-tree). Connection pool: min 10, max 100 connections. "
                      "Query timeout: 30 seconds.",
            "version": "3.1",
            "lastUpdated": "2025-10-25",
            "tags": ["database", "schema", "postgresql"],
        },
        {
            "id": "spec-security-006",
            "title": "Security Best Practices",
            "category": "Technical Spec",
            "content": "Security requirements: All API endpoints must use HTTPS (TLS 1.3). "
                      "Passwords must be hashed using bcrypt with cost factor 12. API keys "
                      "must be at least 32 characters and rotated every 90 days. Enable CORS "
                      "only for whitelisted domains. Implement rate limiting: 1000 req/hour "
                      "for authenticated users, 100 req/hour for anonymous. Log all authentication "
                      "failures and API access. Enable SQL injection protection via parameterized "
                      "queries. Sanitize all user inputs.",
            "version": "2.5",
            "lastUpdated": "2025-10-18",
            "tags": ["security", "best-practices", "compliance"],
        },
    ]
    
    return {"documents": documents}


def generate_code_generation_dataset() -> dict[str, Any]:
    """Generate programming tasks for code generation benchmarks.
    
    Tests LLM's ability to generate correct code based on specifications,
    handle edge cases, and follow best practices. Includes context about
    existing codebase and requirements.
    
    Returns:
        Dict with 'tasks' list containing programming challenges.
    """
    tasks = [
        {
            "id": "code-001",
            "title": "Implement User Authentication Middleware",
            "language": "Python",
            "difficulty": "Medium",
            "description": "Create a FastAPI middleware that validates JWT tokens. "
                          "The middleware should extract the token from the Authorization "
                          "header, verify it using the SECRET_KEY, and attach user info to "
                          "the request. Return 401 if token is missing or invalid.",
            "context": {
                "framework": "FastAPI",
                "dependencies": ["PyJWT", "python-jose"],
                "existingCode": "SECRET_KEY = 'your-secret-key'\nALGORITHM = 'HS256'",
            },
            "expectedBehavior": "Middleware validates JWT, attaches user to request.state.user, "
                               "returns 401 for invalid tokens",
            "testCases": [
                {"input": "Valid JWT token", "output": "User authenticated"},
                {"input": "Missing token", "output": "401 Unauthorized"},
                {"input": "Expired token", "output": "401 Unauthorized"},
            ],
        },
        {
            "id": "code-002",
            "title": "Database Connection Pool Manager",
            "language": "TypeScript",
            "difficulty": "Hard",
            "description": "Implement a PostgreSQL connection pool manager with retry logic. "
                          "The class should maintain a pool of connections, handle connection "
                          "failures with exponential backoff (max 3 retries), and provide "
                          "methods for query execution with automatic connection management.",
            "context": {
                "framework": "Node.js",
                "dependencies": ["pg", "pg-pool"],
                "existingCode": "interface PoolConfig { min: number; max: number; timeout: number; }",
            },
            "expectedBehavior": "Pool manages connections, retries on failure, auto-releases connections",
            "testCases": [
                {"input": "Execute query with available connection", "output": "Query result"},
                {"input": "Connection failure", "output": "Retry 3 times with backoff"},
                {"input": "Pool exhausted", "output": "Wait for available connection"},
            ],
        },
        {
            "id": "code-003",
            "title": "Rate Limiter Implementation",
            "language": "Go",
            "difficulty": "Medium",
            "description": "Implement a token bucket rate limiter for API endpoints. "
                          "Support per-user and per-IP rate limiting with configurable "
                          "bucket size and refill rate. Use Redis for distributed rate limiting.",
            "context": {
                "framework": "Go",
                "dependencies": ["go-redis/redis"],
                "existingCode": "type RateLimiter struct { client *redis.Client }",
            },
            "expectedBehavior": "Limits requests based on token bucket algorithm, "
                               "returns true if allowed, false if rate limit exceeded",
            "testCases": [
                {"input": "10 requests within limit", "output": "All allowed"},
                {"input": "100 requests exceeding limit", "output": "Some rejected"},
                {"input": "Wait for refill", "output": "Tokens replenished"},
            ],
        },
    ]
    
    return {"tasks": tasks}


def generate_customer_support_dataset() -> dict[str, Any]:
    """Generate customer support conversation scenarios.
    
    Multi-turn conversations testing LLM's ability to maintain context,
    provide accurate information, and handle various customer intents.
    
    Returns:
        Dict with 'conversations' list containing support scenarios.
    """
    fk = _get_faker()
    
    conversations = [
        {
            "id": "support-001",
            "category": "Order Status",
            "priority": "Medium",
            "turns": [
                {
                    "speaker": "customer",
                    "message": "Hi, I placed an order 3 days ago but haven't received any shipping confirmation. "
                              "My order number is ORD-2025-10-15-7834.",
                    "timestamp": "2025-10-28T10:15:00Z",
                },
                {
                    "speaker": "agent",
                    "message": "I apologize for the delay. Let me check your order status. "
                              "Order ORD-2025-10-15-7834 is currently in processing. "
                              "It should ship within 24 hours. You'll receive tracking info via email.",
                    "timestamp": "2025-10-28T10:16:30Z",
                },
                {
                    "speaker": "customer",
                    "message": "Can I change the shipping address? I'll be traveling next week.",
                    "timestamp": "2025-10-28T10:17:00Z",
                },
            ],
            "context": {
                "orderId": "ORD-2025-10-15-7834",
                "orderDate": "2025-10-15",
                "status": "processing",
                "items": ["Laptop Stand", "Wireless Mouse"],
                "total": 89.99,
                "shippingAddress": "123 Main St, New York, NY 10001",
            },
            "expectedResolution": "Update shipping address if order hasn't shipped yet",
        },
        {
            "id": "support-002",
            "category": "Technical Issue",
            "priority": "High",
            "turns": [
                {
                    "speaker": "customer",
                    "message": "I'm getting a 500 error when trying to upload files larger than 10MB. "
                              "This worked fine last week.",
                    "timestamp": "2025-10-28T14:20:00Z",
                },
                {
                    "speaker": "agent",
                    "message": "I see the issue. We recently updated our file upload limits. "
                              "The new maximum is 5MB per file. For larger files, please use our "
                              "chunked upload API endpoint /api/v2/uploads/chunked.",
                    "timestamp": "2025-10-28T14:21:15Z",
                },
                {
                    "speaker": "customer",
                    "message": "How do I use the chunked upload API? Do you have documentation?",
                    "timestamp": "2025-10-28T14:22:00Z",
                },
            ],
            "context": {
                "userId": "user-9876",
                "apiVersion": "2.0",
                "errorCode": "500",
                "fileSize": "12MB",
                "previousLimit": "50MB",
                "newLimit": "5MB",
            },
            "expectedResolution": "Provide chunked upload API documentation and code example",
        },
    ]
    
    return {"conversations": conversations}


def generate_data_analysis_dataset() -> dict[str, Any]:
    """Generate business data for complex analytical queries.

    Tests LLM's ability to perform multi-step reasoning, aggregations,
    and derive insights from structured business data.

    Returns:
        Dict with 'sales' and 'products' data for analysis.
    """
    fk = _get_faker()

    # Generate product catalog
    products = [
        {"id": "P001", "name": "Premium Laptop", "category": "Electronics", "price": 1299.99, "cost": 800.00},
        {"id": "P002", "name": "Wireless Mouse", "category": "Electronics", "price": 29.99, "cost": 12.00},
        {"id": "P003", "name": "USB-C Cable", "category": "Accessories", "price": 19.99, "cost": 5.00},
        {"id": "P004", "name": "Desk Chair", "category": "Furniture", "price": 249.99, "cost": 120.00},
        {"id": "P005", "name": "Monitor Stand", "category": "Accessories", "price": 49.99, "cost": 20.00},
        {"id": "P006", "name": "Keyboard", "category": "Electronics", "price": 79.99, "cost": 35.00},
        {"id": "P007", "name": "Webcam", "category": "Electronics", "price": 89.99, "cost": 40.00},
        {"id": "P008", "name": "Desk Lamp", "category": "Furniture", "price": 39.99, "cost": 15.00},
    ]

    # Generate sales transactions
    sales = []
    start_date = datetime(2025, 1, 1)
    for i in range(200):
        sale_date = start_date + timedelta(days=fk.random_int(0, 300))
        product = fk.random_element(products)
        quantity = fk.random_int(1, 10)
        discount = fk.random.choice([0, 0.05, 0.10, 0.15, 0.20])

        sales.append({
            "transactionId": f"TXN-{i+1:05d}",
            "date": sale_date.strftime("%Y-%m-%d"),
            "productId": product["id"],
            "productName": product["name"],
            "category": product["category"],
            "quantity": quantity,
            "unitPrice": product["price"],
            "discount": discount,
            "totalAmount": round(quantity * product["price"] * (1 - discount), 2),
            "region": fk.random_element(["North", "South", "East", "West"]),
            "salesRep": fk.name(),
        })

    return {"sales": sales, "products": products}


def generate_multidoc_reasoning_dataset() -> dict[str, Any]:
    """Generate multi-document dataset for cross-reference tasks.

    Tests LLM's ability to synthesize information across multiple documents,
    identify contradictions, and perform complex reasoning.

    Returns:
        Dict with related documents requiring cross-referencing.
    """
    dataset = {
        "scenario": "Product Launch Analysis",
        "documents": [
            {
                "id": "doc-marketing-001",
                "type": "Marketing Report",
                "date": "2025-10-01",
                "content": {
                    "title": "Q3 2025 Marketing Campaign Results",
                    "summary": "The new product launch campaign reached 2.5M impressions "
                              "with a 3.2% click-through rate. Total marketing spend: $150,000. "
                              "Generated 80,000 website visits and 5,000 sign-ups.",
                    "metrics": {
                        "impressions": 2500000,
                        "clicks": 80000,
                        "ctr": 0.032,
                        "signups": 5000,
                        "spend": 150000,
                        "costPerSignup": 30.00,
                    },
                    "channels": [
                        {"name": "Social Media", "spend": 60000, "signups": 2000},
                        {"name": "Search Ads", "spend": 50000, "signups": 2500},
                        {"name": "Email", "spend": 40000, "signups": 500},
                    ],
                },
            },
            {
                "id": "doc-sales-002",
                "type": "Sales Report",
                "date": "2025-10-15",
                "content": {
                    "title": "Q3 2025 Sales Performance",
                    "summary": "Product launch generated 3,200 sales in the first month. "
                              "Average order value: $299. Total revenue: $956,800. "
                              "Conversion rate from sign-ups: 64%.",
                    "metrics": {
                        "totalSales": 3200,
                        "revenue": 956800,
                        "averageOrderValue": 299,
                        "conversionRate": 0.64,
                        "returningCustomers": 450,
                    },
                    "topRegions": [
                        {"region": "West", "sales": 1200, "revenue": 358800},
                        {"region": "East", "sales": 1000, "revenue": 299000},
                        {"region": "South", "sales": 600, "revenue": 179400},
                        {"region": "North", "sales": 400, "revenue": 119600},
                    ],
                },
            },
            {
                "id": "doc-finance-003",
                "type": "Financial Analysis",
                "date": "2025-10-20",
                "content": {
                    "title": "Q3 2025 Product Profitability Analysis",
                    "summary": "Product launch ROI analysis shows positive returns. "
                              "Total costs (marketing + production): $450,000. "
                              "Net profit: $506,800. ROI: 112.6%.",
                    "metrics": {
                        "totalRevenue": 956800,
                        "marketingCost": 150000,
                        "productionCost": 300000,
                        "totalCost": 450000,
                        "netProfit": 506800,
                        "roi": 1.126,
                        "breakEvenUnits": 1505,
                    },
                    "projections": {
                        "q4Sales": 4500,
                        "q4Revenue": 1345500,
                        "yearEndProfit": 895500,
                    },
                },
            },
            {
                "id": "doc-customer-004",
                "type": "Customer Feedback",
                "date": "2025-10-25",
                "content": {
                    "title": "Customer Satisfaction Survey Results",
                    "summary": "Survey of 500 customers shows 85% satisfaction rate. "
                              "Top features: ease of use (92%), design (88%), value (78%). "
                              "Main complaints: shipping time (45%), customer support (32%).",
                    "metrics": {
                        "responseRate": 0.156,
                        "satisfactionScore": 4.2,
                        "nps": 42,
                        "wouldRecommend": 0.85,
                    },
                    "feedback": {
                        "positive": ["Great design", "Easy to use", "Good value"],
                        "negative": ["Slow shipping", "Support response time", "Limited features"],
                        "suggestions": ["Add mobile app", "Faster shipping", "24/7 support"],
                    },
                },
            },
        ],
    }

    return dataset

