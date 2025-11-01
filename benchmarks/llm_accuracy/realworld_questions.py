"""Question generation for real-world LLM scenarios.

Generates questions that test LLM performance on production use cases:
- RAG: Information extraction from documentation
- Code Generation: Understanding requirements and context
- Customer Support: Multi-turn context maintenance
- Data Analysis: Complex analytical reasoning
- Multi-document: Cross-reference and synthesis
"""

import logging

from .realworld_datasets import (
    generate_code_generation_dataset,
    generate_customer_support_dataset,
    generate_data_analysis_dataset,
    generate_multidoc_reasoning_dataset,
    generate_rag_documentation_dataset,
)
from .types import Question


logger = logging.getLogger(__name__)


def generate_realworld_questions() -> list[Question]:
    """Generate all real-world scenario questions.

    Returns:
        List of Question objects for real-world LLM use cases.
    """
    questions: list[Question] = []
    id_counter = 1

    # Load datasets
    try:
        rag_data = generate_rag_documentation_dataset()
        code_data = generate_code_generation_dataset()
        support_data = generate_customer_support_dataset()
        analysis_data = generate_data_analysis_dataset()
        multidoc_data = generate_multidoc_reasoning_dataset()
    except RuntimeError as e:
        logger.error(f"Failed to generate real-world datasets: {e}")
        raise

    # ========================================
    # RAG DOCUMENTATION QUESTIONS (~20 questions)
    # ========================================

    docs = rag_data.get("documents", [])

    # Information extraction questions
    if docs:
        # API-specific questions
        auth_doc = next((d for d in docs if d["id"] == "api-auth-001"), None)
        if auth_doc:
            questions.extend(
                [
                    {
                        "id": f"rag{id_counter}",
                        "prompt": "What is the rate limit for the Authentication API?",
                        "ground_truth": "100 requests per minute per IP address",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 1}",
                        "prompt": "How long is the access token valid in the Authentication API?",
                        "ground_truth": "3600 seconds",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 2}",
                        "prompt": "What authentication method does the API use?",
                        "ground_truth": "OAuth 2.0",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                ]
            )
            id_counter += 3

        # User management questions
        users_doc = next((d for d in docs if d["id"] == "api-users-002"), None)
        if users_doc:
            questions.extend(
                [
                    {
                        "id": f"rag{id_counter}",
                        "prompt": "What role is required to create a new user?",
                        "ground_truth": "admin role",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 1}",
                        "prompt": "What is the maximum payload size for User Management API?",
                        "ground_truth": "5MB",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                ]
            )
            id_counter += 2

        # Setup guide questions
        setup_doc = next((d for d in docs if d["id"] == "guide-setup-003"), None)
        if setup_doc:
            questions.extend(
                [
                    {
                        "id": f"rag{id_counter}",
                        "prompt": "What is the minimum Node.js version supported by the SDK?",
                        "ground_truth": "18",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 1}",
                        "prompt": "What is the recommended timeout for production use?",
                        "ground_truth": "30 seconds",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                ]
            )
            id_counter += 2

        # Error handling questions
        errors_doc = next((d for d in docs if d["id"] == "guide-errors-004"), None)
        if errors_doc:
            questions.extend(
                [
                    {
                        "id": f"rag{id_counter}",
                        "prompt": "What HTTP status code indicates rate limit exceeded?",
                        "ground_truth": "429",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 1}",
                        "prompt": "How long should you wait before retrying after hitting rate limit?",
                        "ground_truth": "60 seconds",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 2}",
                        "prompt": "What does HTTP status code 403 mean?",
                        "ground_truth": "Forbidden - Insufficient permissions for the requested resource",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                ]
            )
            id_counter += 3

        # Database spec questions
        db_doc = next((d for d in docs if d["id"] == "spec-database-005"), None)
        if db_doc:
            questions.extend(
                [
                    {
                        "id": f"rag{id_counter}",
                        "prompt": "What is the maximum number of database connections in the pool?",
                        "ground_truth": "100",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 1}",
                        "prompt": "What is the query timeout setting?",
                        "ground_truth": "30 seconds",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 2}",
                        "prompt": "What PostgreSQL version is used?",
                        "ground_truth": "15.2",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                ]
            )
            id_counter += 3

        # Security questions
        security_doc = next((d for d in docs if d["id"] == "spec-security-006"), None)
        if security_doc:
            questions.extend(
                [
                    {
                        "id": f"rag{id_counter}",
                        "prompt": "What is the bcrypt cost factor for password hashing?",
                        "ground_truth": "12",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 1}",
                        "prompt": "How often should API keys be rotated?",
                        "ground_truth": "every 90 days",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                    {
                        "id": f"rag{id_counter + 2}",
                        "prompt": "What is the rate limit for authenticated users per hour?",
                        "ground_truth": "1000",
                        "type": "rag-extraction",
                        "dataset": "rag-documentation",
                    },
                ]
            )
            id_counter += 3

    # ========================================
    # CODE GENERATION QUESTIONS (~15 questions)
    # ========================================

    tasks = code_data.get("tasks", [])

    if tasks:
        # Understanding requirements
        for task in tasks:
            questions.extend(
                [
                    {
                        "id": f"code{id_counter}",
                        "prompt": f"What programming language is required for task '{task['title']}'?",
                        "ground_truth": task["language"],
                        "type": "code-understanding",
                        "dataset": "code-generation",
                    },
                    {
                        "id": f"code{id_counter + 1}",
                        "prompt": f"What is the difficulty level of '{task['title']}'?",
                        "ground_truth": task["difficulty"],
                        "type": "code-understanding",
                        "dataset": "code-generation",
                    },
                ]
            )
            id_counter += 2

        # Specific task questions
        auth_task = next((t for t in tasks if t["id"] == "code-001"), None)
        if auth_task:
            questions.extend(
                [
                    {
                        "id": f"code{id_counter}",
                        "prompt": "What framework is used in the User Authentication Middleware task?",
                        "ground_truth": "FastAPI",
                        "type": "code-context",
                        "dataset": "code-generation",
                    },
                    {
                        "id": f"code{id_counter + 1}",
                        "prompt": "What HTTP status code should be returned for invalid tokens?",
                        "ground_truth": "401",
                        "type": "code-requirements",
                        "dataset": "code-generation",
                    },
                ]
            )
            id_counter += 2

        pool_task = next((t for t in tasks if t["id"] == "code-002"), None)
        if pool_task:
            questions.extend(
                [
                    {
                        "id": f"code{id_counter}",
                        "prompt": "How many retries should the Database Connection Pool Manager attempt?",
                        "ground_truth": "3",
                        "type": "code-requirements",
                        "dataset": "code-generation",
                    },
                ]
            )
            id_counter += 1

        limiter_task = next((t for t in tasks if t["id"] == "code-003"), None)
        if limiter_task:
            questions.extend(
                [
                    {
                        "id": f"code{id_counter}",
                        "prompt": "What algorithm should the Rate Limiter use?",
                        "ground_truth": "token bucket",
                        "type": "code-requirements",
                        "dataset": "code-generation",
                    },
                    {
                        "id": f"code{id_counter + 1}",
                        "prompt": "What database is used for distributed rate limiting?",
                        "ground_truth": "Redis",
                        "type": "code-context",
                        "dataset": "code-generation",
                    },
                ]
            )
            id_counter += 2

    # ========================================
    # CUSTOMER SUPPORT QUESTIONS (~15 questions)
    # ========================================

    conversations = support_data.get("conversations", [])

    if conversations:
        # Context understanding
        order_conv = next((c for c in conversations if c["id"] == "support-001"), None)
        if order_conv:
            questions.extend(
                [
                    {
                        "id": f"support{id_counter}",
                        "prompt": "What is the order number in the first customer support conversation?",
                        "ground_truth": "ORD-2025-10-15-7834",
                        "type": "support-context",
                        "dataset": "customer-support",
                    },
                    {
                        "id": f"support{id_counter + 1}",
                        "prompt": "What is the current status of order ORD-2025-10-15-7834?",
                        "ground_truth": "processing",
                        "type": "support-context",
                        "dataset": "customer-support",
                    },
                    {
                        "id": f"support{id_counter + 2}",
                        "prompt": "How many items are in order ORD-2025-10-15-7834?",
                        "ground_truth": "2",
                        "type": "support-reasoning",
                        "dataset": "customer-support",
                    },
                    {
                        "id": f"support{id_counter + 3}",
                        "prompt": "What is the total amount for order ORD-2025-10-15-7834?",
                        "ground_truth": "89.99",
                        "type": "support-context",
                        "dataset": "customer-support",
                    },
                    {
                        "id": f"support{id_counter + 4}",
                        "prompt": "What is the customer's main concern in conversation support-001?",
                        "ground_truth": "No shipping confirmation received",
                        "type": "support-intent",
                        "dataset": "customer-support",
                    },
                ]
            )
            id_counter += 5

        tech_conv = next((c for c in conversations if c["id"] == "support-002"), None)
        if tech_conv:
            questions.extend(
                [
                    {
                        "id": f"support{id_counter}",
                        "prompt": "What error code is the customer experiencing in conversation support-002?",
                        "ground_truth": "500",
                        "type": "support-context",
                        "dataset": "customer-support",
                    },
                    {
                        "id": f"support{id_counter + 1}",
                        "prompt": "What is the new file upload limit mentioned by the agent?",
                        "ground_truth": "5MB",
                        "type": "support-information",
                        "dataset": "customer-support",
                    },
                    {
                        "id": f"support{id_counter + 2}",
                        "prompt": "What API endpoint should be used for files larger than 5MB?",
                        "ground_truth": "/api/v2/uploads/chunked",
                        "type": "support-solution",
                        "dataset": "customer-support",
                    },
                    {
                        "id": f"support{id_counter + 3}",
                        "prompt": "What was the previous file upload limit?",
                        "ground_truth": "50MB",
                        "type": "support-context",
                        "dataset": "customer-support",
                    },
                ]
            )
            id_counter += 4

    # ========================================
    # DATA ANALYSIS QUESTIONS (~25 questions)
    # ========================================

    sales = analysis_data.get("sales", [])
    products = analysis_data.get("products", [])

    if sales and products:
        # Product information
        laptop = next((p for p in products if p["id"] == "P001"), None)
        if laptop:
            questions.extend(
                [
                    {
                        "id": f"analysis{id_counter}",
                        "prompt": "What is the price of the Premium Laptop?",
                        "ground_truth": "1299.99",
                        "type": "analysis-lookup",
                        "dataset": "data-analysis",
                    },
                    {
                        "id": f"analysis{id_counter + 1}",
                        "prompt": "What is the profit margin for product P001?",
                        "ground_truth": str(round((1299.99 - 800.00) / 1299.99 * 100, 2)),
                        "type": "analysis-calculation",
                        "dataset": "data-analysis",
                    },
                ]
            )
            id_counter += 2

        # Aggregation questions
        electronics = [p for p in products if p["category"] == "Electronics"]
        questions.extend(
            [
                {
                    "id": f"analysis{id_counter}",
                    "prompt": "How many products are in the Electronics category?",
                    "ground_truth": str(len(electronics)),
                    "type": "analysis-aggregation",
                    "dataset": "data-analysis",
                },
            ]
        )
        id_counter += 1

        # Sales analysis
        total_transactions = len(sales)
        questions.extend(
            [
                {
                    "id": f"analysis{id_counter}",
                    "prompt": "How many total sales transactions are in the dataset?",
                    "ground_truth": str(total_transactions),
                    "type": "analysis-count",
                    "dataset": "data-analysis",
                },
            ]
        )
        id_counter += 1

        # Region analysis
        regions = list({s["region"] for s in sales})
        questions.extend(
            [
                {
                    "id": f"analysis{id_counter}",
                    "prompt": "How many different sales regions are there?",
                    "ground_truth": str(len(regions)),
                    "type": "analysis-distinct",
                    "dataset": "data-analysis",
                },
            ]
        )
        id_counter += 1

        # Category analysis
        categories = list({p["category"] for p in products})
        questions.extend(
            [
                {
                    "id": f"analysis{id_counter}",
                    "prompt": "What product categories are available?",
                    "ground_truth": ", ".join(sorted(categories)),
                    "type": "analysis-list",
                    "dataset": "data-analysis",
                },
            ]
        )
        id_counter += 1

        # Specific product questions
        mouse = next((p for p in products if p["id"] == "P002"), None)
        if mouse:
            questions.extend(
                [
                    {
                        "id": f"analysis{id_counter}",
                        "prompt": "What is the cost of the Wireless Mouse?",
                        "ground_truth": "12.00",
                        "type": "analysis-lookup",
                        "dataset": "data-analysis",
                    },
                ]
            )
            id_counter += 1

    # ========================================
    # MULTI-DOCUMENT REASONING QUESTIONS (~25 questions)
    # ========================================

    scenario_docs = multidoc_data.get("documents", [])

    if scenario_docs:
        # Marketing metrics
        marketing_doc = next((d for d in scenario_docs if d["id"] == "doc-marketing-001"), None)
        if marketing_doc:
            marketing_doc["content"]["metrics"]
            questions.extend(
                [
                    {
                        "id": f"multidoc{id_counter}",
                        "prompt": "How many impressions did the marketing campaign reach?",
                        "ground_truth": "2500000",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 1}",
                        "prompt": "What was the total marketing spend?",
                        "ground_truth": "150000",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 2}",
                        "prompt": "What was the cost per signup?",
                        "ground_truth": "30.00",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 3}",
                        "prompt": "Which marketing channel generated the most signups?",
                        "ground_truth": "Search Ads",
                        "type": "multidoc-comparison",
                        "dataset": "multi-document",
                    },
                ]
            )
            id_counter += 4

        # Sales metrics
        sales_doc = next((d for d in scenario_docs if d["id"] == "doc-sales-002"), None)
        if sales_doc:
            sales_doc["content"]["metrics"]
            questions.extend(
                [
                    {
                        "id": f"multidoc{id_counter}",
                        "prompt": "How many sales were generated in the first month?",
                        "ground_truth": "3200",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 1}",
                        "prompt": "What was the average order value?",
                        "ground_truth": "299",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 2}",
                        "prompt": "What was the conversion rate from sign-ups to sales?",
                        "ground_truth": "64%",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 3}",
                        "prompt": "Which region had the highest sales?",
                        "ground_truth": "West",
                        "type": "multidoc-comparison",
                        "dataset": "multi-document",
                    },
                ]
            )
            id_counter += 4

        # Financial metrics
        finance_doc = next((d for d in scenario_docs if d["id"] == "doc-finance-003"), None)
        if finance_doc:
            finance_doc["content"]["metrics"]
            questions.extend(
                [
                    {
                        "id": f"multidoc{id_counter}",
                        "prompt": "What was the net profit from the product launch?",
                        "ground_truth": "506800",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 1}",
                        "prompt": "What was the ROI percentage?",
                        "ground_truth": "112.6%",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 2}",
                        "prompt": "What was the production cost?",
                        "ground_truth": "300000",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                ]
            )
            id_counter += 3

        # Cross-document reasoning
        if marketing_doc and sales_doc:
            questions.extend(
                [
                    {
                        "id": f"multidoc{id_counter}",
                        "prompt": "According to the marketing and sales reports, what was the conversion rate from signups to sales?",
                        "ground_truth": "64%",
                        "type": "multidoc-synthesis",
                        "dataset": "multi-document",
                    },
                ]
            )
            id_counter += 1

        if sales_doc and finance_doc:
            questions.extend(
                [
                    {
                        "id": f"multidoc{id_counter}",
                        "prompt": "Do the total revenue figures match between the sales and finance reports?",
                        "ground_truth": "Yes",
                        "type": "multidoc-verification",
                        "dataset": "multi-document",
                    },
                ]
            )
            id_counter += 1

        # Customer feedback
        customer_doc = next((d for d in scenario_docs if d["id"] == "doc-customer-004"), None)
        if customer_doc:
            customer_doc["content"]["metrics"]
            questions.extend(
                [
                    {
                        "id": f"multidoc{id_counter}",
                        "prompt": "What was the customer satisfaction score?",
                        "ground_truth": "4.2",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 1}",
                        "prompt": "What was the Net Promoter Score (NPS)?",
                        "ground_truth": "42",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                    {
                        "id": f"multidoc{id_counter + 2}",
                        "prompt": "What percentage of customers would recommend the product?",
                        "ground_truth": "85%",
                        "type": "multidoc-extraction",
                        "dataset": "multi-document",
                    },
                ]
            )
            id_counter += 3

    logger.info(f"Generated {len(questions)} real-world scenario questions")
    return questions
