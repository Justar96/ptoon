# Token Efficiency Benchmark

- 📚 GitHub Repositories: ██████████████░░░░░░░░░░░ 57.7% TOON — TOON 8,744 vs JSON 15,144 | 💰 42.3% saved
- 📈 Daily Analytics (180 days): ██████████░░░░░░░░░░░░░░░ 41.0% TOON — TOON 4,499 vs JSON 10,969 | 💰 59.0% saved
- 🛒 E-Commerce Orders: █████████████████░░░░░░░░ 66.1% TOON — TOON 7,046 vs JSON 10,654 | 💰 33.9% saved
- 👥 Employee Records: █████████░░░░░░░░░░░░░░░░ 36.1% TOON — TOON 2,162 vs JSON 5,992 | 💰 63.9% saved

---

Totals: TOON 22,451 vs JSON 42,759 — 💰 47.5% saved

## Details

<details><summary>📚 GitHub Repositories — 42.3% saved</summary>

100 top GitHub repositories as uniform tabular records.

#### JSON (truncated)

```json
{
  "repositories": [
    {
      "id": 28457823,
      "name": "freeCodeCamp",
      "repo": "freeCodeCamp/freeCodeCamp",
      "description": "freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming, and computer science for free.",
      "createdAt": "2014-12-24T17:49:19Z",
      "updatedAt": "2025-10-27T07:40:58Z",
      "pushedAt": "2025-10-26T11:31:08Z",
      "stars": 430828,
      "watchers": 8582,
      "forks": 42136,
      "defaultBranch": "main"
    },
    {
      "id": 132750724,
      "name": "build-your-own-x",
      "repo": "codecrafters-io/build-your-own-x",
      "description": "Master programming by recreating your favorite technologies from scratch.",
      "createdAt": "2018-05-09T12:03:18Z",
      "updatedAt": "2025-10-27T07:43:25Z",
      "pushedAt": "2025-10-10T18:45:01Z",
      "stars": 430102,
      "watchers": 6322,
      "forks": 40388,
      "defaultBranch": "master"
    },
    {
      "id": 21737465,
      "name": "awesome",
      "repo": "sindresorhus/awesome",
      "description": "😎 Awesome lists about all kinds of interesting topics",
      "createdAt": "2014-07-11T13:42:37Z",
      "updatedAt": "2025-10-27T07:44:27Z",
      "pushedAt": "2025-10-23T17:26:53Z",
      "stars": 409760,
      "watchers": 8016,
      "forks": 32015,
      "defaultBranch": "main"
    }
  ]
}
```

#### TOON (truncated)

```
repositories[3]{id,name,repo,description,createdAt,updatedAt,pushedAt,stars,watchers,forks,defaultBranch}:
  28457823,freeCodeCamp,freeCodeCamp/freeCodeCamp,"freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming, and computer science for free.","2014-12-24T17:49:19Z","2025-10-27T07:40:58Z","2025-10-26T11:31:08Z",430828,8582,42136,main
  132750724,build-your-own-x,codecrafters-io/build-your-own-x,Master programming by recreating your favorite technologies from scratch.,"2018-05-09T12:03:18Z","2025-10-27T07:43:25Z","2025-10-10T18:45:01Z",430102,6322,40388,master
  21737465,awesome,sindresorhus/awesome,😎 Awesome lists about all kinds of interesting topics,"2014-07-11T13:42:37Z","2025-10-27T07:44:27Z","2025-10-23T17:26:53Z",409760,8016,32015,main
```

</details>

<details><summary>📈 Daily Analytics (180 days) — 59.0% saved</summary>

Synthetic daily web analytics metrics for 180 days.

#### JSON (truncated)

```json
{
  "metrics": [
    {
      "date": "2025-01-01",
      "views": 4874,
      "clicks": 100,
      "conversions": 13,
      "revenue": 1620.45,
      "bounceRate": 0.42
    },
    {
      "date": "2025-01-02",
      "views": 4540,
      "clicks": 245,
      "conversions": 16,
      "revenue": 1296.91,
      "bounceRate": 0.46
    },
    {
      "date": "2025-01-03",
      "views": 5093,
      "clicks": 155,
      "conversions": 16,
      "revenue": 2219.45,
      "bounceRate": 0.77
    },
    {
      "date": "2025-01-04",
      "views": 3070,
      "clicks": 242,
      "conversions": 22,
      "revenue": 3871.42,
      "bounceRate": 0.29
    },
    {
      "date": "2025-01-05",
      "views": 3729,
      "clicks": 117,
      "conversions": 10,
      "revenue": 558.7,
      "bounceRate": 0.4
    }
  ]
}
```

#### TOON (truncated)

```
metrics[5]{date,views,clicks,conversions,revenue,bounceRate}:
  2025-01-01,4874,100,13,1620.45,0.42
  2025-01-02,4540,245,16,1296.91,0.46
  2025-01-03,5093,155,16,2219.45,0.77
  2025-01-04,3070,242,22,3871.42,0.29
  2025-01-05,3729,117,10,558.7,0.4
```

</details>

<details><summary>🛒 E-Commerce Orders — 33.9% saved</summary>

50 nested e-commerce orders with customers and items.

#### JSON (truncated)

```json
{
  "orders": [
    {
      "orderId": "9c9cea0c-2ca1-4789-a091-250e8fe46024",
      "customer": {
        "id": 7825,
        "name": "Heather Rubio",
        "email": "schmidtjill@example.net"
      },
      "items": [
        {
          "sku": "SKU-4962-XHBQ",
          "name": "Webcam",
          "quantity": 3,
          "price": 465.3
        }
      ],
      "total": 1395.9,
      "status": "cancelled",
      "orderDate": "2024-05-09"
    },
    {
      "orderId": "2e80dbd5-93fd-4234-ae71-1399e2b2848b",
      "customer": {
        "id": 3427,
        "name": "Crystal Mills",
        "email": "lindsay31@example.com"
      },
      "items": [
        {
          "sku": "SKU-5075-BGSV",
          "name": "USB Cable",
          "quantity": 2,
          "price": 418.51
        },
        {
          "sku": "SKU-2924-GPAG",
          "name": "Monitor",
          "quantity": 1,
          "price": 8.3
        }
      ],
      "total": 845.32,
      "status": "processing",
      "orderDate": "2025-07-26"
    }
  ]
}
```

#### TOON (truncated)

```
orders[2]:
  - orderId: 9c9cea0c-2ca1-4789-a091-250e8fe46024
    customer:
      id: 7825
      name: Heather Rubio
      email: schmidtjill@example.net
    items[1]:
      - sku: SKU-4962-XHBQ
        name: Webcam
        quantity: 3
        price: 465.3
    total: 1395.9
    status: cancelled
    orderDate: 2024-05-09
  - orderId: 2e80dbd5-93fd-4234-ae71-1399e2b2848b
    customer:
      id: 3427
      name: Crystal Mills
      email: lindsay31@example.com
    items[2]{sku,name,quantity,price}:
      SKU-5075-BGSV,USB Cable,2,418.51
      SKU-2924-GPAG,Monitor,1,8.3
    total: 845.32
    status: processing
    orderDate: 2025-07-26
```

</details>

<details><summary>👥 Employee Records — 63.9% saved</summary>

100 uniform employee records (tabular optimal).

#### JSON (truncated)

```json
{
  "employees": [
    {
      "id": 1,
      "name": "Adam Bryan",
      "email": "melissa34@example.net",
      "department": "Engineering",
      "salary": 90804,
      "yearsExperience": 8,
      "active": false
    },
    {
      "id": 2,
      "name": "Mark Carr",
      "email": "michaelrubio@example.org",
      "department": "Sales",
      "salary": 100759,
      "yearsExperience": 15,
      "active": true
    },
    {
      "id": 3,
      "name": "Daniel Miller",
      "email": "marc75@example.org",
      "department": "Marketing",
      "salary": 146586,
      "yearsExperience": 20,
      "active": true
    },
    {
      "id": 4,
      "name": "Todd Harrell",
      "email": "justindelgado@example.org",
      "department": "HR",
      "salary": 137981,
      "yearsExperience": 12,
      "active": true
    },
    {
      "id": 5,
      "name": "Joseph Fletcher",
      "email": "lindsay31@example.com",
      "department": "Operations",
      "salary": 67720,
      "yearsExperience": 16,
      "active": true
    }
  ]
}
```

#### TOON (truncated)

```
employees[5]{id,name,email,department,salary,yearsExperience,active}:
  1,Adam Bryan,melissa34@example.net,Engineering,90804,8,false
  2,Mark Carr,michaelrubio@example.org,Sales,100759,15,true
  3,Daniel Miller,marc75@example.org,Marketing,146586,20,true
  4,Todd Harrell,justindelgado@example.org,HR,137981,12,true
  5,Joseph Fletcher,lindsay31@example.com,Operations,67720,16,true
```

</details>