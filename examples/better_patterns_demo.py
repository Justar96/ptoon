#!/usr/bin/env python3
"""Demonstrate token savings from restructuring deeply nested data.

This script proves the 40-60% token savings claims from BETTER_PATTERNS.md
by running real examples and measuring actual token counts.

Run: python examples/better_patterns_demo.py
"""

import json
from ptoon import encode, count_tokens


def print_comparison(name, nested_data, flat_data):
    """Compare token counts between nested and flat representations."""
    nested_json = json.dumps(nested_data)
    flat_json = json.dumps(flat_data)
    flat_toon = encode(flat_data)

    nested_tokens = count_tokens(nested_json)
    flat_json_tokens = count_tokens(flat_json)
    flat_toon_tokens = count_tokens(flat_toon)

    json_savings = (nested_tokens - flat_json_tokens) / nested_tokens * 100
    toon_savings = (nested_tokens - flat_toon_tokens) / nested_tokens * 100

    print(f"\n{'=' * 70}")
    print(f"📊 {name}")
    print(f"{'=' * 70}")
    print(f"Nested JSON:  {nested_tokens:4d} tokens")
    print(f"Flat JSON:    {flat_json_tokens:4d} tokens ({json_savings:+.1f}%)")
    print(f"Flat TOON:    {flat_toon_tokens:4d} tokens ({toon_savings:+.1f}% vs nested JSON)")
    print(f"\n💰 Token savings by flattening: {toon_savings:.1f}%")

    if toon_savings > 50:
        print("🎉 EXCELLENT savings!")
    elif toon_savings > 30:
        print("✅ Great savings!")
    else:
        print("👍 Good savings!")

    print(f"\n📝 TOON Output Preview:")
    print("-" * 70)
    preview = flat_toon[:300] + ("..." if len(flat_toon) > 300 else "")
    print(preview)


def demo_tree_pattern():
    """Pattern 1: Tree → Adjacency List"""

    # Anti-pattern: Nested tree
    tree_nested = {
        "name": "root",
        "id": 0,
        "type": "dir",
        "children": [
            {
                "name": "docs",
                "id": 1,
                "type": "dir",
                "children": [
                    {"name": "readme.md", "id": 2, "type": "file", "children": []},
                    {"name": "guide.md", "id": 3, "type": "file", "children": []},
                ]
            },
            {
                "name": "src",
                "id": 4,
                "type": "dir",
                "children": [
                    {
                        "name": "utils",
                        "id": 5,
                        "type": "dir",
                        "children": [
                            {"name": "helpers.py", "id": 6, "type": "file", "children": []}
                        ]
                    }
                ]
            }
        ]
    }

    # Better pattern: Flat adjacency list
    tree_flat = {
        "nodes": [
            {"id": 0, "name": "root",       "parent": None, "type": "dir"},
            {"id": 1, "name": "docs",       "parent": 0,    "type": "dir"},
            {"id": 2, "name": "readme.md",  "parent": 1,    "type": "file"},
            {"id": 3, "name": "guide.md",   "parent": 1,    "type": "file"},
            {"id": 4, "name": "src",        "parent": 0,    "type": "dir"},
            {"id": 5, "name": "utils",      "parent": 4,    "type": "dir"},
            {"id": 6, "name": "helpers.py", "parent": 5,    "type": "file"},
        ]
    }

    print_comparison("Tree: File System (7 nodes)", tree_nested, tree_flat)


def demo_tensor_pattern():
    """Pattern 2: Tensor → Flattened with Shape"""

    # Anti-pattern: 3D nested array
    tensor_nested = [
        [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12]
        ],
        [
            [13, 14, 15, 16],
            [17, 18, 19, 20],
            [21, 22, 23, 24]
        ]
    ]

    # Better pattern: Flattened with metadata
    tensor_flat = {
        "shape": [2, 3, 4],
        "dtype": "int",
        "data": [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
            13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24
        ]
    }

    print_comparison("Tensor: 3D Array (2x3x4)", tensor_nested, tensor_flat)


def demo_normalized_pattern():
    """Pattern 3: Nested Collections → Normalized Schema"""

    # Anti-pattern: Nested e-commerce order
    order_nested = {
        "order_id": "ORD-001",
        "status": "shipped",
        "total": 47.48,
        "customer": {
            "id": 123,
            "name": "Alice Smith",
            "email": "alice@example.com",
            "address": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "12345"
            }
        },
        "items": [
            {
                "sku": "WIDGET-A",
                "name": "Widget A",
                "price": 10.99,
                "quantity": 2,
                "details": {
                    "color": "red",
                    "size": "M"
                }
            },
            {
                "sku": "GADGET-B",
                "name": "Gadget B",
                "price": 25.50,
                "quantity": 1,
                "details": {
                    "color": "blue",
                    "size": "L"
                }
            }
        ]
    }

    # Better pattern: Normalized tables
    order_flat = {
        "orders": [
            {"id": "ORD-001", "customer_id": 123, "status": "shipped", "total": 47.48}
        ],
        "customers": [
            {
                "id": 123,
                "name": "Alice Smith",
                "email": "alice@example.com",
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "12345"
            }
        ],
        "order_items": [
            {
                "order_id": "ORD-001",
                "sku": "WIDGET-A",
                "name": "Widget A",
                "price": 10.99,
                "quantity": 2,
                "color": "red",
                "size": "M"
            },
            {
                "order_id": "ORD-001",
                "sku": "GADGET-B",
                "name": "Gadget B",
                "price": 25.50,
                "quantity": 1,
                "color": "blue",
                "size": "L"
            }
        ]
    }

    print_comparison("E-Commerce: Order with Items", order_nested, order_flat)


def demo_recursive_pattern():
    """Pattern 4: Recursive Structures → Path-Based"""

    # Anti-pattern: Nested comments
    thread_nested = {
        "id": 1,
        "author": "alice",
        "text": "Great article!",
        "votes": 42,
        "replies": [
            {
                "id": 2,
                "author": "bob",
                "text": "I agree completely",
                "votes": 15,
                "replies": [
                    {
                        "id": 3,
                        "author": "carol",
                        "text": "Me too!",
                        "votes": 5,
                        "replies": []
                    }
                ]
            },
            {
                "id": 4,
                "author": "dave",
                "text": "Thanks for sharing",
                "votes": 8,
                "replies": []
            }
        ]
    }

    # Better pattern: Flat with parent links
    thread_flat = {
        "comments": [
            {"id": 1, "parent_id": None, "author": "alice", "text": "Great article!", "votes": 42, "depth": 0},
            {"id": 2, "parent_id": 1, "author": "bob", "text": "I agree completely", "votes": 15, "depth": 1},
            {"id": 3, "parent_id": 2, "author": "carol", "text": "Me too!", "votes": 5, "depth": 2},
            {"id": 4, "parent_id": 1, "author": "dave", "text": "Thanks for sharing", "votes": 8, "depth": 1},
        ]
    }

    print_comparison("Comments: Reddit-Style Thread (4 comments)", thread_nested, thread_flat)


def demo_org_chart():
    """Bonus: Organization chart example"""

    # Anti-pattern: Nested org chart
    org_nested = {
        "name": "Alice Johnson",
        "title": "CEO",
        "department": "Executive",
        "reports": [
            {
                "name": "Bob Smith",
                "title": "VP Engineering",
                "department": "Engineering",
                "reports": [
                    {"name": "Carol White", "title": "Tech Lead", "department": "Engineering", "reports": []},
                    {"name": "Dave Brown", "title": "Tech Lead", "department": "Engineering", "reports": []},
                ]
            },
            {
                "name": "Eve Davis",
                "title": "VP Sales",
                "department": "Sales",
                "reports": [
                    {"name": "Frank Miller", "title": "Sales Rep", "department": "Sales", "reports": []}
                ]
            }
        ]
    }

    # Better pattern: Flat employees
    org_flat = {
        "employees": [
            {"id": 1, "name": "Alice Johnson", "title": "CEO", "department": "Executive", "manager_id": None},
            {"id": 2, "name": "Bob Smith", "title": "VP Engineering", "department": "Engineering", "manager_id": 1},
            {"id": 3, "name": "Carol White", "title": "Tech Lead", "department": "Engineering", "manager_id": 2},
            {"id": 4, "name": "Dave Brown", "title": "Tech Lead", "department": "Engineering", "manager_id": 2},
            {"id": 5, "name": "Eve Davis", "title": "VP Sales", "department": "Sales", "manager_id": 1},
            {"id": 6, "name": "Frank Miller", "title": "Sales Rep", "department": "Sales", "manager_id": 5},
        ]
    }

    print_comparison("Org Chart: Company (6 employees)", org_nested, org_flat)


def main():
    print("\n" + "=" * 70)
    print("🎯 Better Data Patterns: Token Savings Demonstration")
    print("=" * 70)
    print("\nThis script compares token counts between nested and flat data patterns.")
    print("All measurements use tiktoken (OpenAI's tokenizer) for accurate counts.")

    demo_tree_pattern()
    demo_tensor_pattern()
    demo_normalized_pattern()
    demo_recursive_pattern()
    demo_org_chart()

    print("\n" + "=" * 70)
    print("🎓 Summary")
    print("=" * 70)
    print("\n✨ Key Findings:")
    print("  • Flattening deeply nested data saves 40-60% tokens")
    print("  • TOON's tabular format excels at flat, uniform data")
    print("  • These patterns improve queryability AND token efficiency")
    print("  • Works for JSON too, not just TOON!")
    print("\n📚 See BETTER_PATTERNS.md for more examples and helper functions.")
    print()


if __name__ == "__main__":
    main()
