from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


# Import faker lazily inside functions when possible to avoid hard dependency at import time.

DATA_DIR = Path(__file__).resolve().parent / "data"


def _get_faker() -> "Any":
    """Return a seeded Faker instance (seed=12345). Import only when needed."""
    try:
        from faker import Faker  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dep
        raise RuntimeError(
            "Dataset generation requires 'faker'. Install with: pip install faker"
        ) from exc
    Faker.seed(12345)
    return Faker()


def generate_analytics_data(days: int, start_date: str = "2025-01-01") -> Dict[str, Any]:
    """Generate reproducible daily analytics metrics.

    Fields per metric:
    - date: ISO date string (YYYY-MM-DD)
    - views: int (base 5000 with weekend multiplier and variation)
    - clicks: 2-8% of views
    - conversions: 5-15% of clicks
    - revenue: conversions * AOV (49.99-299.99)
    - bounceRate: float (0.2 - 0.8)
    """
    fk = _get_faker()
    base_views = 5000
    start = datetime.fromisoformat(start_date)
    metrics: List[Dict[str, Any]] = []
    for i in range(days):
        d = start + timedelta(days=i)
        # Weekend multiplier
        weekend_mult = 0.7 if d.weekday() >= 5 else 1.0
        # Variation ~ +/- 15%
        variation = 1.0 + fk.random.uniform(-0.15, 0.15)
        views = max(0, int(base_views * weekend_mult * variation))

        ctr = fk.random.uniform(0.02, 0.08)
        clicks = max(0, int(round(views * ctr)))

        conv_rate = fk.random.uniform(0.05, 0.15)
        conversions = max(0, int(round(clicks * conv_rate)))

        aov = fk.random.uniform(49.99, 299.99)
        revenue = round(conversions * aov, 2)

        bounce_rate = round(fk.random.uniform(0.2, 0.8), 2)

        metrics.append(
            {
                "date": d.strftime("%Y-%m-%d"),
                "views": views,
                "clicks": clicks,
                "conversions": conversions,
                "revenue": revenue,
                "bounceRate": bounce_rate,
            }
        )

    return {"metrics": metrics}


def generate_tabular_dataset() -> Dict[str, Any]:
    """Generate 100 uniform employee records."""
    fk = _get_faker()
    departments = ["Engineering", "Sales", "Marketing", "HR", "Operations", "Finance"]
    employees: List[Dict[str, Any]] = []
    for i in range(100):
        name = fk.name()
        email = fk.unique.email()
        dept = departments[i % len(departments)]
        salary = int(round(fk.random.uniform(45_000, 150_000)))
        years = int(round(fk.random.uniform(1, 20)))
        active = fk.random.random() < 0.8
        employees.append(
            {
                "id": i + 1,
                "name": name,
                "email": email,
                "department": dept,
                "salary": salary,
                "yearsExperience": years,
                "active": active,
            }
        )
    return {"employees": employees}


def generate_nested_dataset() -> Dict[str, Any]:
    """Generate 50 nested e-commerce orders with items and customers."""
    fk = _get_faker()
    products = [
        "Wireless Mouse",
        "USB Cable",
        "Laptop Stand",
        "Keyboard",
        "Webcam",
        "Headphones",
        "Monitor",
        "Desk Lamp",
    ]
    statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]

    orders: List[Dict[str, Any]] = []
    for _ in range(50):
        cust_id = fk.random_int(min=1000, max=9999)
        order_items: List[Dict[str, Any]] = []
        for _j in range(fk.random_int(min=1, max=4)):
            pname = fk.random_element(elements=products)
            quantity = fk.random_int(min=1, max=5)
            price = round(fk.random.uniform(5.0, 499.0), 2)
            order_items.append(
                {
                    "sku": fk.bothify(text="SKU-####-????").upper(),
                    "name": pname,
                    "quantity": quantity,
                    "price": price,
                }
            )
        total = round(sum(it["price"] * it["quantity"] for it in order_items), 2)
        orders.append(
            {
                "orderId": fk.uuid4(),
                "customer": {
                    "id": cust_id,
                    "name": fk.name(),
                    "email": fk.unique.email(),
                },
                "items": order_items,
                "total": total,
                "status": fk.random_element(elements=statuses),
                "orderDate": fk.date_between_dates(
                    date_start=datetime(2024, 1, 1), date_end=datetime(2025, 10, 1)
                ).isoformat(),
            }
        )
    return {"orders": orders}


def load_github_dataset() -> Dict[str, Any]:
    """Load GitHub repositories data from benchmarks/data/github-repos.json.

    Returns a dict with key "repositories" (list). If file is not found, returns an empty list.
    """
    path = DATA_DIR / "github-repos.json"
    if not path.exists():
        # Graceful fallback
        return {"repositories": []}
    import json
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # Expect a JSON array at root
    if isinstance(data, list):
        return {"repositories": data}
    return {"repositories": []}


def get_all_datasets() -> List[Tuple[str, str, str, Dict[str, Any]]]:
    """Return list of (name, emoji, description, data) for all datasets."""
    datasets: List[Tuple[str, str, str, Dict[str, Any]]] = []

    # GitHub Repositories (reference data)
    gh = load_github_dataset()
    datasets.append(
        (
            "GitHub Repositories",
            "📚",
            "100 top GitHub repositories as uniform tabular records.",
            gh,
        )
    )

    # Daily Analytics (180 days)
    analytics = generate_analytics_data(180)
    datasets.append(
        (
            "Daily Analytics (180 days)",
            "📈",
            "Synthetic daily web analytics metrics for 180 days.",
            analytics,
        )
    )

    # E-Commerce Orders (nested)
    nested = generate_nested_dataset()
    datasets.append(
        (
            "E-Commerce Orders",
            "🛒",
            "50 nested e-commerce orders with customers and items.",
            nested,
        )
    )

    # Employee Records (tabular)
    employees = generate_tabular_dataset()
    datasets.append(
        (
            "Employee Records",
            "👥",
            "100 uniform employee records (tabular optimal).",
            employees,
        )
    )

    return datasets
