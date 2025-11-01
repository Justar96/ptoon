"""Question generation for TOON LLM accuracy benchmarks.

Generates ~160 questions across different types:
- Field retrieval (~50%): "What is X's Y?"
- Aggregation (~25%): "How many X have Y?"
- Filtering (~25%): "List/count X where Y"

Questions are generated dynamically based on actual data values.
"""

import logging
from typing import Any

from benchmarks.datasets import (
    generate_analytics_data,
    generate_nested_dataset,
    generate_tabular_dataset,
    load_github_dataset,
)

from .types import Question


logger = logging.getLogger(__name__)


def generate_questions() -> list[Question]:
    """Generate all benchmark questions from datasets.

    Returns:
        List of Question objects with prompts, ground truth answers, and metadata.

    Raises:
        RuntimeError: If required dataset generation dependencies are missing.
    """
    questions: list[Question] = []
    id_counter = 1

    # Load datasets
    try:
        tabular_data = generate_tabular_dataset()
        nested_data = generate_nested_dataset()
        analytics_data = generate_analytics_data(180)
        github_data = load_github_dataset()
    except RuntimeError as e:
        logger.error(f"Failed to generate datasets: {e}")
        raise

    # Extract arrays from dataset dictionaries
    tabular: list[dict[str, Any]] = tabular_data.get("employees", [])
    nested: list[dict[str, Any]] = nested_data.get("orders", [])
    analytics: list[dict[str, Any]] = analytics_data.get("metrics", [])
    github: list[dict[str, Any]] = github_data.get("repositories", [])

    # ========================================
    # TABULAR DATASET QUESTIONS (55 questions)
    # ========================================

    if tabular:
        # Field retrieval: specific employees (28 questions)
        for i in range(min(28, len(tabular))):
            emp = tabular[i * 2] if i * 2 < len(tabular) else tabular[i]

            # Alternate between different field types
            if i % 3 == 0:
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"What is the salary of {emp['name']}?",
                        "ground_truth": str(emp["salary"]),
                        "type": "field-retrieval",
                        "dataset": "tabular",
                    }
                )
                id_counter += 1
            elif i % 3 == 1:
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"What department does {emp['name']} work in?",
                        "ground_truth": emp["department"],
                        "type": "field-retrieval",
                        "dataset": "tabular",
                    }
                )
                id_counter += 1
            else:
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"What is the email address of {emp['name']}?",
                        "ground_truth": emp["email"],
                        "type": "field-retrieval",
                        "dataset": "tabular",
                    }
                )
                id_counter += 1

        # Aggregation: count by department (6 questions)
        departments = list({e["department"] for e in tabular})
        for dept in departments[:6]:
            count = len([e for e in tabular if e["department"] == dept])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many employees work in {dept}?",
                    "ground_truth": str(count),
                    "type": "aggregation",
                    "dataset": "tabular",
                }
            )
            id_counter += 1

        # Aggregation: salary ranges (4 questions)
        salary_thresholds = [60000, 80000, 100000, 120000]
        for threshold in salary_thresholds:
            count = len([e for e in tabular if e["salary"] > threshold])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many employees have a salary greater than {threshold}?",
                    "ground_truth": str(count),
                    "type": "aggregation",
                    "dataset": "tabular",
                }
            )
            id_counter += 1

        # Aggregation: department-level metrics (5 questions)
        # Average salary by department for top 3 departments
        for dept in departments[:3]:
            dept_employees = [e for e in tabular if e["department"] == dept]
            if dept_employees:
                avg_salary = sum(e["salary"] for e in dept_employees) / len(dept_employees)
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"What is the average salary in {dept}?",
                        "ground_truth": f"{avg_salary:.2f}",
                        "type": "aggregation",
                        "dataset": "tabular",
                    }
                )
                id_counter += 1

        # Total employees and average salary across all
        total_employees = len(tabular)
        avg_salary_all = sum(e["salary"] for e in tabular) / total_employees
        questions.extend(
            [
                {
                    "id": f"q{id_counter}",
                    "prompt": "What is the average salary across all employees?",
                    "ground_truth": f"{avg_salary_all:.2f}",
                    "type": "aggregation",
                    "dataset": "tabular",
                },
                {
                    "id": f"q{id_counter + 1}",
                    "prompt": "What is the total number of employees?",
                    "ground_truth": str(total_employees),
                    "type": "aggregation",
                    "dataset": "tabular",
                },
            ]
        )
        id_counter += 2

        # Filtering: active status (2 questions)
        active_count = len([e for e in tabular if e["active"]])
        inactive_count = len([e for e in tabular if not e["active"]])
        questions.extend(
            [
                {
                    "id": f"q{id_counter}",
                    "prompt": "How many employees are active?",
                    "ground_truth": str(active_count),
                    "type": "filtering",
                    "dataset": "tabular",
                },
                {
                    "id": f"q{id_counter + 1}",
                    "prompt": "How many employees are inactive?",
                    "ground_truth": str(inactive_count),
                    "type": "filtering",
                    "dataset": "tabular",
                },
            ]
        )
        id_counter += 2

        # Complex filtering: multi-condition department+salary (4 questions)
        for dept in departments[:4]:
            count = len([e for e in tabular if e["department"] == dept and e["salary"] > 80000])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many employees in {dept} have a salary greater than 80000?",
                    "ground_truth": str(count),
                    "type": "filtering",
                    "dataset": "tabular",
                }
            )
            id_counter += 1

        # Complex filtering: experience+active status (3 questions)
        for exp in [5, 10, 15]:
            count = len([e for e in tabular if e["yearsExperience"] > exp and e["active"]])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many active employees have more than {exp} years of experience?",
                    "ground_truth": str(count),
                    "type": "filtering",
                    "dataset": "tabular",
                }
            )
            id_counter += 1

        # Additional filtering questions (3 more to reach 12)
        high_salary_active = len([e for e in tabular if e["salary"] > 100000 and e["active"]])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many active employees have a salary greater than 100000?",
                "ground_truth": str(high_salary_active),
                "type": "filtering",
                "dataset": "tabular",
            }
        )
        id_counter += 1

        senior_inactive = len([e for e in tabular if e["yearsExperience"] > 10 and not e["active"]])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many inactive employees have more than 10 years of experience?",
                "ground_truth": str(senior_inactive),
                "type": "filtering",
                "dataset": "tabular",
            }
        )
        id_counter += 1

        low_salary_count = len([e for e in tabular if e["salary"] < 60000])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many employees have a salary less than 60000?",
                "ground_truth": str(low_salary_count),
                "type": "filtering",
                "dataset": "tabular",
            }
        )
        id_counter += 1

    # ========================================
    # NESTED DATASET QUESTIONS (40 questions)
    # ========================================

    if nested:
        # Field retrieval: order totals and status (12 questions)
        for i in range(min(12, len(nested))):
            order = nested[i * 2] if i * 2 < len(nested) else nested[i]

            if i % 2 == 0:
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"What is the total amount for order {order['orderId']}?",
                        "ground_truth": f"{order['total']:.2f}",
                        "type": "field-retrieval",
                        "dataset": "nested",
                    }
                )
                id_counter += 1
            else:
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"What is the status of order {order['orderId']}?",
                        "ground_truth": order["status"],
                        "type": "field-retrieval",
                        "dataset": "nested",
                    }
                )
                id_counter += 1

        # Field retrieval: customer names (8 questions)
        for i in range(min(8, len(nested))):
            order = nested[i * 3] if i * 3 < len(nested) else nested[i]
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"What is the customer name for order {order['orderId']}?",
                    "ground_truth": order["customer"]["name"],
                    "type": "field-retrieval",
                    "dataset": "nested",
                }
            )
            id_counter += 1

        # Aggregation: count by status
        statuses = list({o["status"] for o in nested})
        for status in statuses:
            count = len([o for o in nested if o["status"] == status])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f'How many orders have status "{status}"?',
                    "ground_truth": str(count),
                    "type": "aggregation",
                    "dataset": "nested",
                }
            )
            id_counter += 1

        # Aggregation: total and average revenue, order count
        total_revenue = sum(o["total"] for o in nested)
        avg_revenue = total_revenue / len(nested)
        total_items = sum(len(o["items"]) for o in nested)
        questions.extend(
            [
                {
                    "id": f"q{id_counter}",
                    "prompt": "What is the total revenue across all orders?",
                    "ground_truth": f"{total_revenue:.2f}",
                    "type": "aggregation",
                    "dataset": "nested",
                },
                {
                    "id": f"q{id_counter + 1}",
                    "prompt": "What is the average order value?",
                    "ground_truth": f"{avg_revenue:.2f}",
                    "type": "aggregation",
                    "dataset": "nested",
                },
                {
                    "id": f"q{id_counter + 2}",
                    "prompt": "What is the total number of items across all orders?",
                    "ground_truth": str(total_items),
                    "type": "aggregation",
                    "dataset": "nested",
                },
            ]
        )
        id_counter += 3

        # Filtering: high-value orders (3 questions)
        high_value_thresholds = [200, 400, 600]
        for threshold in high_value_thresholds:
            count = len([o for o in nested if o["total"] > threshold])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many orders have a total greater than {threshold}?",
                    "ground_truth": str(count),
                    "type": "filtering",
                    "dataset": "nested",
                }
            )
            id_counter += 1

        # Filtering: status-based with value threshold (3 questions)
        for status_filter in statuses[: min(3, len(statuses))]:
            high_value_status = len([o for o in nested if o["total"] > 300 and o["status"] == status_filter])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f'How many orders with status "{status_filter}" have a total greater than 300?',
                    "ground_truth": str(high_value_status),
                    "type": "filtering",
                    "dataset": "nested",
                }
            )
            id_counter += 1

        # Filtering: item count (2 questions)
        multi_item_orders = len([o for o in nested if len(o["items"]) > 2])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many orders have more than 2 items?",
                "ground_truth": str(multi_item_orders),
                "type": "filtering",
                "dataset": "nested",
            }
        )
        id_counter += 1

        single_item_orders = len([o for o in nested if len(o["items"]) == 1])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many orders have exactly 1 item?",
                "ground_truth": str(single_item_orders),
                "type": "filtering",
                "dataset": "nested",
            }
        )
        id_counter += 1

        # Filtering: value ranges (4 more to reach 12)
        mid_range_orders = len([o for o in nested if 100 <= o["total"] <= 500])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many orders have a total between 100 and 500 (inclusive)?",
                "ground_truth": str(mid_range_orders),
                "type": "filtering",
                "dataset": "nested",
            }
        )
        id_counter += 1

        low_value_orders = len([o for o in nested if o["total"] < 100])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many orders have a total less than 100?",
                "ground_truth": str(low_value_orders),
                "type": "filtering",
                "dataset": "nested",
            }
        )
        id_counter += 1

        high_quantity_orders = len([o for o in nested if sum(item["quantity"] for item in o["items"]) > 5])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many orders have a total quantity greater than 5 items?",
                "ground_truth": str(high_quantity_orders),
                "type": "filtering",
                "dataset": "nested",
            }
        )
        id_counter += 1

        very_high_value_orders = len([o for o in nested if o["total"] > 800])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many orders have a total greater than 800?",
                "ground_truth": str(very_high_value_orders),
                "type": "filtering",
                "dataset": "nested",
            }
        )
        id_counter += 1

    # ========================================
    # ANALYTICS DATASET QUESTIONS (37 questions)
    # ========================================

    if analytics:
        # Field retrieval: specific dates (17 questions)
        for i in range(min(17, len(analytics))):
            metric = analytics[i * 3] if i * 3 < len(analytics) else analytics[i]

            if i % 2 == 0:
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"How many views were recorded on {metric['date']}?",
                        "ground_truth": str(metric["views"]),
                        "type": "field-retrieval",
                        "dataset": "analytics",
                    }
                )
                id_counter += 1
            else:
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"What was the revenue on {metric['date']}?",
                        "ground_truth": f"{metric['revenue']:.2f}",
                        "type": "field-retrieval",
                        "dataset": "analytics",
                    }
                )
                id_counter += 1

        # Aggregation: totals and averages (10 questions)
        total_views = sum(m["views"] for m in analytics)
        total_revenue = sum(m["revenue"] for m in analytics)
        total_conversions = sum(m["conversions"] for m in analytics)
        total_clicks = sum(m["clicks"] for m in analytics)
        avg_views = total_views / len(analytics)
        avg_revenue = total_revenue / len(analytics)
        avg_conversions = total_conversions / len(analytics)
        avg_clicks = total_clicks / len(analytics)
        avg_bounce_rate = sum(m["bounceRate"] for m in analytics) / len(analytics)

        questions.extend(
            [
                {
                    "id": f"q{id_counter}",
                    "prompt": "What is the total number of views across all dates?",
                    "ground_truth": str(total_views),
                    "type": "aggregation",
                    "dataset": "analytics",
                },
                {
                    "id": f"q{id_counter + 1}",
                    "prompt": "What is the total revenue across all dates?",
                    "ground_truth": f"{total_revenue:.2f}",
                    "type": "aggregation",
                    "dataset": "analytics",
                },
                {
                    "id": f"q{id_counter + 2}",
                    "prompt": "What is the total number of conversions across all dates?",
                    "ground_truth": str(total_conversions),
                    "type": "aggregation",
                    "dataset": "analytics",
                },
                {
                    "id": f"q{id_counter + 3}",
                    "prompt": "What is the total number of clicks across all dates?",
                    "ground_truth": str(total_clicks),
                    "type": "aggregation",
                    "dataset": "analytics",
                },
                {
                    "id": f"q{id_counter + 4}",
                    "prompt": "What is the average number of views per day?",
                    "ground_truth": f"{avg_views:.2f}",
                    "type": "aggregation",
                    "dataset": "analytics",
                },
                {
                    "id": f"q{id_counter + 5}",
                    "prompt": "What is the average revenue per day?",
                    "ground_truth": f"{avg_revenue:.2f}",
                    "type": "aggregation",
                    "dataset": "analytics",
                },
                {
                    "id": f"q{id_counter + 6}",
                    "prompt": "What is the average number of conversions per day?",
                    "ground_truth": f"{avg_conversions:.2f}",
                    "type": "aggregation",
                    "dataset": "analytics",
                },
                {
                    "id": f"q{id_counter + 7}",
                    "prompt": "What is the average number of clicks per day?",
                    "ground_truth": f"{avg_clicks:.2f}",
                    "type": "aggregation",
                    "dataset": "analytics",
                },
                {
                    "id": f"q{id_counter + 8}",
                    "prompt": "What is the average bounce rate across all dates?",
                    "ground_truth": f"{avg_bounce_rate:.2f}",
                    "type": "aggregation",
                    "dataset": "analytics",
                },
                {
                    "id": f"q{id_counter + 9}",
                    "prompt": "How many days of data are in the dataset?",
                    "ground_truth": str(len(analytics)),
                    "type": "aggregation",
                    "dataset": "analytics",
                },
            ]
        )
        id_counter += 10

        # Filtering: high-performing days - views (3 questions)
        view_thresholds = [5000, 6000, 7000]
        for threshold in view_thresholds:
            count = len([m for m in analytics if m["views"] > threshold])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many days had more than {threshold} views?",
                    "ground_truth": str(count),
                    "type": "filtering",
                    "dataset": "analytics",
                }
            )
            id_counter += 1

        # Filtering: high-performing days - conversions (3 questions)
        conversion_thresholds = [10, 20, 30]
        for threshold in conversion_thresholds:
            count = len([m for m in analytics if m["conversions"] > threshold])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many days had more than {threshold} conversions?",
                    "ground_truth": str(count),
                    "type": "filtering",
                    "dataset": "analytics",
                }
            )
            id_counter += 1

        # Additional filtering questions (4 more to reach 10)
        high_revenue_days = len([m for m in analytics if m["revenue"] > 500])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many days had revenue greater than 500?",
                "ground_truth": str(high_revenue_days),
                "type": "filtering",
                "dataset": "analytics",
            }
        )
        id_counter += 1

        high_clicks_days = len([m for m in analytics if m["clicks"] > 300])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many days had more than 300 clicks?",
                "ground_truth": str(high_clicks_days),
                "type": "filtering",
                "dataset": "analytics",
            }
        )
        id_counter += 1

        low_bounce_days = len([m for m in analytics if m["bounceRate"] < 0.4])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many days had a bounce rate less than 0.4?",
                "ground_truth": str(low_bounce_days),
                "type": "filtering",
                "dataset": "analytics",
            }
        )
        id_counter += 1

        high_bounce_days = len([m for m in analytics if m["bounceRate"] > 0.6])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many days had a bounce rate greater than 0.6?",
                "ground_truth": str(high_bounce_days),
                "type": "filtering",
                "dataset": "analytics",
            }
        )
        id_counter += 1

    # ========================================
    # GITHUB DATASET QUESTIONS (30 questions)
    # ========================================

    if github:
        # Field retrieval: specific repos (15 questions)
        for i in range(min(15, len(github))):
            repo = github[i * 5] if i * 5 < len(github) else github[i]

            if i % 2 == 0:
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"How many stars does {repo['owner']}/{repo['name']} have?",
                        "ground_truth": str(repo["stars"]),
                        "type": "field-retrieval",
                        "dataset": "github",
                    }
                )
                id_counter += 1
            else:
                questions.append(
                    {
                        "id": f"q{id_counter}",
                        "prompt": f"How many forks does {repo['owner']}/{repo['name']} have?",
                        "ground_truth": str(repo["forks"]),
                        "type": "field-retrieval",
                        "dataset": "github",
                    }
                )
                id_counter += 1

        # Aggregation: count by owner (5 questions)
        owners = list({r["owner"] for r in github})
        for owner in owners[:5]:
            count = len([r for r in github if r["owner"] == owner])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many repositories does {owner} have in the dataset?",
                    "ground_truth": str(count),
                    "type": "aggregation",
                    "dataset": "github",
                }
            )
            id_counter += 1

        # Aggregation: total stars and average (2 questions)
        total_stars = sum(r["stars"] for r in github)
        avg_stars = total_stars / len(github)
        questions.extend(
            [
                {
                    "id": f"q{id_counter}",
                    "prompt": "What is the total number of stars across all repositories?",
                    "ground_truth": str(total_stars),
                    "type": "aggregation",
                    "dataset": "github",
                },
                {
                    "id": f"q{id_counter + 1}",
                    "prompt": "What is the average number of stars per repository?",
                    "ground_truth": f"{avg_stars:.2f}",
                    "type": "aggregation",
                    "dataset": "github",
                },
            ]
        )
        id_counter += 2

        # Filtering: popular repos by stars (3 questions)
        star_thresholds = [10000, 50000, 100000]
        for threshold in star_thresholds:
            count = len([r for r in github if r["stars"] > threshold])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many repositories have more than {threshold} stars?",
                    "ground_truth": str(count),
                    "type": "filtering",
                    "dataset": "github",
                }
            )
            id_counter += 1

        # Filtering: popular repos by forks (3 questions)
        fork_thresholds = [1000, 5000, 10000]
        for threshold in fork_thresholds:
            count = len([r for r in github if r["forks"] > threshold])
            questions.append(
                {
                    "id": f"q{id_counter}",
                    "prompt": f"How many repositories have more than {threshold} forks?",
                    "ground_truth": str(count),
                    "type": "filtering",
                    "dataset": "github",
                }
            )
            id_counter += 1

        # Additional filtering questions (2 more to reach 8)
        high_star_fork_ratio = len([r for r in github if r["stars"] > r["forks"] * 10])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many repositories have more than 10 times as many stars as forks?",
                "ground_truth": str(high_star_fork_ratio),
                "type": "filtering",
                "dataset": "github",
            }
        )
        id_counter += 1

        moderate_popularity = len([r for r in github if 5000 <= r["stars"] <= 50000])
        questions.append(
            {
                "id": f"q{id_counter}",
                "prompt": "How many repositories have between 5000 and 50000 stars (inclusive)?",
                "ground_truth": str(moderate_popularity),
                "type": "filtering",
                "dataset": "github",
            }
        )
        id_counter += 1

    # Log question breakdown
    tabular_count = len([q for q in questions if q["dataset"] == "tabular"])
    nested_count = len([q for q in questions if q["dataset"] == "nested"])
    analytics_count = len([q for q in questions if q["dataset"] == "analytics"])
    github_count = len([q for q in questions if q["dataset"] == "github"])

    field_retrieval_count = len([q for q in questions if q["type"] == "field-retrieval"])
    aggregation_count = len([q for q in questions if q["type"] == "aggregation"])
    filtering_count = len([q for q in questions if q["type"] == "filtering"])

    logger.info("Question breakdown:")
    logger.info("  By dataset:")
    logger.info(f"    Tabular: {tabular_count}")
    logger.info(f"    Nested: {nested_count}")
    logger.info(f"    Analytics: {analytics_count}")
    logger.info(f"    GitHub: {github_count}")
    logger.info("  By type:")
    logger.info(f"    Field retrieval: {field_retrieval_count}")
    logger.info(f"    Aggregation: {aggregation_count}")
    logger.info(f"    Filtering: {filtering_count}")
    logger.info(f"  Total: {len(questions)}")

    return questions
