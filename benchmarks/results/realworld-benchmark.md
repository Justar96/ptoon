# Real-World API Response Benchmark

Generated: 2025-11-01 02:32:02
Samples: 19/19 compatible | Avg token savings: 27.4%

## Overview

| Sample | Pattern | Compatible | JSON Tokens | TOON Tokens | Savings % | Status |
|---|---|---|---:|---:|---:|---|
| github_commit_history.json | GitHub API | ✓ | 2,987 | 2,540 | 15.0% | ✓ Pass |
| github_issue_detail.json | GitHub API | ✓ | 1,563 | 1,303 | 16.6% | ✓ Pass |
| github_pull_request.json | GitHub API | ✓ | 2,736 | 2,298 | 16.0% | ✓ Pass |
| github_repo_list.json | GitHub API | ✓ | 1,268 | 1,037 | 18.2% | ✓ Pass |
| github_user_profile.json | GitHub API | ✓ | 989 | 813 | 17.8% | ✓ Pass |
| graphql_nested_query.json | GraphQL | ✓ | 888 | 660 | 25.7% | ✓ Pass |
| graphql_pagination.json | GraphQL | ✓ | 1,544 | 1,131 | 26.7% | ✓ Pass |
| graphql_union_types.json | GraphQL | ✓ | 797 | 591 | 25.8% | ✓ Pass |
| jsonld_activity_streams.json | JSON-LD | ✓ | 974 | 782 | 19.7% | ✓ Pass |
| jsonld_product_catalog.json | JSON-LD | ✓ | 1,617 | 1,173 | 27.5% | ✓ Pass |
| jsonld_schema_org.json | JSON-LD | ✓ | 1,177 | 897 | 23.8% | ✓ Pass |
| openapi_github.json | OpenAPI Specs | ✓ | 1,723 | 1,098 | 36.3% | ✓ Pass |
| openapi_petstore.json | OpenAPI Specs | ✓ | 2,011 | 1,336 | 33.6% | ✓ Pass |
| openapi_stripe.json | OpenAPI Specs | ✓ | 1,593 | 1,035 | 35.0% | ✓ Pass |
| rest_pagination_cursor.json | REST Pagination | ✓ | 1,191 | 645 | 45.8% | ✓ Pass |
| rest_pagination_link_header.json | REST Pagination | ✓ | 1,699 | 1,396 | 17.8% | ✓ Pass |
| rest_pagination_offset.json | REST Pagination | ✓ | 1,625 | 639 | 60.7% | ✓ Pass |
| articles_classification_dataset.json | Scientific Articles | ✓ | 404,090 | 363,378 | 10.1% | ✓ Pass |
| nasdaq_timeseries_1h.json | Time-Series Data | ✓ | 892,827 | 459,551 | 48.5% | ✓ Pass |

## Analysis by Pattern

### GitHub API

- Samples: 5
- Compatibility: 5/5 (100.0%)
- Avg token savings: 16.7%
- Best performer: github_repo_list.json (18.2% savings)

**Individual Results:**
- github_commit_history.json: ✓ Compatible, 2,987 → 2,540 tokens (15.0% savings)
- github_issue_detail.json: ✓ Compatible, 1,563 → 1,303 tokens (16.6% savings)
- github_pull_request.json: ✓ Compatible, 2,736 → 2,298 tokens (16.0% savings)
- github_repo_list.json: ✓ Compatible, 1,268 → 1,037 tokens (18.2% savings)
- github_user_profile.json: ✓ Compatible, 989 → 813 tokens (17.8% savings)

### GraphQL

- Samples: 3
- Compatibility: 3/3 (100.0%)
- Avg token savings: 26.1%
- Best performer: graphql_pagination.json (26.7% savings)

**Individual Results:**
- graphql_nested_query.json: ✓ Compatible, 888 → 660 tokens (25.7% savings)
- graphql_pagination.json: ✓ Compatible, 1,544 → 1,131 tokens (26.7% savings)
- graphql_union_types.json: ✓ Compatible, 797 → 591 tokens (25.8% savings)

### JSON-LD

- Samples: 3
- Compatibility: 3/3 (100.0%)
- Avg token savings: 23.7%
- Best performer: jsonld_product_catalog.json (27.5% savings)

**Individual Results:**
- jsonld_activity_streams.json: ✓ Compatible, 974 → 782 tokens (19.7% savings)
- jsonld_product_catalog.json: ✓ Compatible, 1,617 → 1,173 tokens (27.5% savings)
- jsonld_schema_org.json: ✓ Compatible, 1,177 → 897 tokens (23.8% savings)

### OpenAPI Specs

- Samples: 3
- Compatibility: 3/3 (100.0%)
- Avg token savings: 35.0%
- Best performer: openapi_github.json (36.3% savings)

**Individual Results:**
- openapi_github.json: ✓ Compatible, 1,723 → 1,098 tokens (36.3% savings)
- openapi_petstore.json: ✓ Compatible, 2,011 → 1,336 tokens (33.6% savings)
- openapi_stripe.json: ✓ Compatible, 1,593 → 1,035 tokens (35.0% savings)

### REST Pagination

- Samples: 3
- Compatibility: 3/3 (100.0%)
- Avg token savings: 41.5%
- Best performer: rest_pagination_offset.json (60.7% savings)

**Individual Results:**
- rest_pagination_cursor.json: ✓ Compatible, 1,191 → 645 tokens (45.8% savings)
- rest_pagination_link_header.json: ✓ Compatible, 1,699 → 1,396 tokens (17.8% savings)
- rest_pagination_offset.json: ✓ Compatible, 1,625 → 639 tokens (60.7% savings)

### Scientific Articles

- Samples: 1
- Compatibility: 1/1 (100.0%)
- Avg token savings: 10.1%
- Best performer: articles_classification_dataset.json (10.1% savings)

**Individual Results:**
- articles_classification_dataset.json: ✓ Compatible, 404,090 → 363,378 tokens (10.1% savings)

### Time-Series Data

- Samples: 1
- Compatibility: 1/1 (100.0%)
- Avg token savings: 48.5%
- Best performer: nasdaq_timeseries_1h.json (48.5% savings)

**Individual Results:**
- nasdaq_timeseries_1h.json: ✓ Compatible, 892,827 → 459,551 tokens (48.5% savings)

## Token Efficiency Summary

- GitHub API: █████████████████████░░░░ 16.7% saved
- GraphQL: ██████████████████░░░░░░░ 26.1% saved
- JSON-LD: ███████████████████░░░░░░ 23.7% saved
- OpenAPI Specs: ████████████████░░░░░░░░░ 35.0% saved
- REST Pagination: ███████████████░░░░░░░░░░ 41.5% saved
- Scientific Articles: ██████████████████████░░░ 10.1% saved
- Time-Series Data: █████████████░░░░░░░░░░░░ 48.5% saved

## Sample Details

<details><summary>github_commit_history.json — 15.0% saved</summary>

**JSON (truncated):**
```json
[
  {
    "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
    "node_id": "MDY6Q29tbWl0NmRjYjA5YjViNTc4NzVmMzM0ZjYxYWViZWQ2OTVlMmU0MTkzZGI1ZQ==",
    "commit": {
      "author": {
        "name": "The Octocat",
        "email": "octocat@github.com",
        "date": "2024-01-15T14:20:15Z"
      },
      "committer": {
        "name": "The Octocat",
        "email": "octocat@github.com",
        "date": "2024-01-15T14:20:15Z"
      },
      "message": "Fix critical security vulnerability in auth
...
```

**TOON (truncated):**
```
[3]:
  - sha: 6dcb09b5b57875f334f61aebed695e2e4193db5e
    node_id: MDY6Q29tbWl0NmRjYjA5YjViNTc4NzVmMzM0ZjYxYWViZWQ2OTVlMmU0MTkzZGI1ZQ==
    commit:
      author:
        name: The Octocat
        email: octocat@github.com
        date: "2024-01-15T14:20:15Z"
      committer:
        name: The Octocat
        email: octocat@github.com
        date: "2024-01-15T14:20:15Z"
      message: Fix critical security vulnerability in authentication
      tree:
        sha: f9d2a07e9488b91af2641b26b9407fe2
...
```

</details>

<details><summary>github_issue_detail.json — 16.6% saved</summary>

**JSON (truncated):**
```json
{
  "id": 1,
  "node_id": "MDU6SXNzdWUx",
  "url": "https://api.github.com/repos/octocat/Hello-World/issues/1347",
  "repository_url": "https://api.github.com/repos/octocat/Hello-World",
  "labels_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347/labels{/name}",
  "comments_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347/comments",
  "events_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347/events",
  "html_url": "https://github.com/octocat
...
```

**TOON (truncated):**
```
id: 1
node_id: MDU6SXNzdWUx
url: "https://api.github.com/repos/octocat/Hello-World/issues/1347"
repository_url: "https://api.github.com/repos/octocat/Hello-World"
labels_url: "https://api.github.com/repos/octocat/Hello-World/issues/1347/labels{/name}"
comments_url: "https://api.github.com/repos/octocat/Hello-World/issues/1347/comments"
events_url: "https://api.github.com/repos/octocat/Hello-World/issues/1347/events"
html_url: "https://github.com/octocat/Hello-World/issues/1347"
number: 1347
stat
...
```

</details>

<details><summary>github_pull_request.json — 16.0% saved</summary>

**JSON (truncated):**
```json
{
  "id": 1,
  "node_id": "MDExOlB1bGxSZXF1ZXN0MQ==",
  "url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347",
  "html_url": "https://github.com/octocat/Hello-World/pull/1347",
  "diff_url": "https://github.com/octocat/Hello-World/pull/1347.diff",
  "patch_url": "https://github.com/octocat/Hello-World/pull/1347.patch",
  "issue_url": "https://api.github.com/repos/octocat/Hello-World/issues/1347",
  "commits_url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits
...
```

**TOON (truncated):**
```
id: 1
node_id: MDExOlB1bGxSZXF1ZXN0MQ==
url: "https://api.github.com/repos/octocat/Hello-World/pulls/1347"
html_url: "https://github.com/octocat/Hello-World/pull/1347"
diff_url: "https://github.com/octocat/Hello-World/pull/1347.diff"
patch_url: "https://github.com/octocat/Hello-World/pull/1347.patch"
issue_url: "https://api.github.com/repos/octocat/Hello-World/issues/1347"
commits_url: "https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits"
review_comments_url: "https://api.github.
...
```

</details>

<details><summary>github_repo_list.json — 18.2% saved</summary>

**JSON (truncated):**
```json
[
  {
    "id": 123456789,
    "name": "awesome-python",
    "full_name": "vinta/awesome-python",
    "owner": {
      "login": "vinta",
      "id": 652070,
      "avatar_url": "https://avatars.githubusercontent.com/u/652070?v=4",
      "type": "User",
      "site_admin": false
    },
    "description": "A curated list of awesome Python frameworks, libraries, software and resources",
    "html_url": "https://github.com/vinta/awesome-python",
    "fork": false,
    "stargazers_count": 185234,
   
...
```

**TOON (truncated):**
```
[5]:
  - id: 123456789
    name: awesome-python
    full_name: vinta/awesome-python
    owner:
      login: vinta
      id: 652070
      avatar_url: "https://avatars.githubusercontent.com/u/652070?v=4"
      type: User
      site_admin: false
    description: "A curated list of awesome Python frameworks, libraries, software and resources"
    html_url: "https://github.com/vinta/awesome-python"
    fork: false
    stargazers_count: 185234
    watchers_count: 185234
    forks_count: 24567
    lang
...
```

</details>

<details><summary>github_user_profile.json — 17.8% saved</summary>

**JSON (truncated):**
```json
{
  "login": "octocat",
  "id": 1,
  "node_id": "MDQ6VXNlcjE=",
  "avatar_url": "https://github.com/images/error/octocat_happy.gif",
  "gravatar_id": "",
  "url": "https://api.github.com/users/octocat",
  "html_url": "https://github.com/octocat",
  "type": "User",
  "site_admin": false,
  "name": "The Octocat",
  "company": "@github",
  "blog": "https://github.blog",
  "location": "San Francisco",
  "email": "octocat@github.com",
  "hireable": null,
  "bio": "There once was...",
  "twitter_usern
...
```

**TOON (truncated):**
```
login: octocat
id: 1
node_id: MDQ6VXNlcjE=
avatar_url: "https://github.com/images/error/octocat_happy.gif"
gravatar_id: ""
url: "https://api.github.com/users/octocat"
html_url: "https://github.com/octocat"
type: User
site_admin: false
name: The Octocat
company: @github
blog: "https://github.blog"
location: San Francisco
email: octocat@github.com
hireable: null
bio: There once was...
twitter_username: github
public_repos: 8
public_gists: 8
followers: 9001
following: 9
created_at: "2008-01-14T04:3
...
```

</details>

<details><summary>graphql_nested_query.json — 25.7% saved</summary>

**JSON (truncated):**
```json
{
  "data": {
    "repository": {
      "name": "react",
      "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces",
      "stargazerCount": 215678,
      "forkCount": 44567,
      "owner": {
        "login": "facebook",
        "avatarUrl": "https://avatars.githubusercontent.com/u/69631?v=4",
        "repositories": {
          "totalCount": 153,
          "edges": [
            {
              "node": {
                "name": "react",
       
...
```

**TOON (truncated):**
```
data:
  repository:
    name: react
    description: "A declarative, efficient, and flexible JavaScript library for building user interfaces"
    stargazerCount: 215678
    forkCount: 44567
    owner:
      login: facebook
      avatarUrl: "https://avatars.githubusercontent.com/u/69631?v=4"
      repositories:
        totalCount: 153
        edges[2]:
          - node:
              name: react
              description: "A declarative, efficient, and flexible JavaScript library"
              s
...
```

</details>

<details><summary>graphql_pagination.json — 26.7% saved</summary>

**JSON (truncated):**
```json
{
  "data": {
    "repository": {
      "name": "typescript",
      "owner": {
        "login": "microsoft"
      },
      "issues": {
        "totalCount": 5847,
        "pageInfo": {
          "hasNextPage": true,
          "hasPreviousPage": false,
          "startCursor": "Y3Vyc29yOnYyOpHOABc7gA==",
          "endCursor": "Y3Vyc29yOnYyOpHOABdCIA=="
        },
        "edges": [
          {
            "cursor": "Y3Vyc29yOnYyOpHOABc7gA==",
            "node": {
              "id": "I_kwDOADtD
...
```

**TOON (truncated):**
```
data:
  repository:
    name: typescript
    owner:
      login: microsoft
    issues:
      totalCount: 5847
      pageInfo:
        hasNextPage: true
        hasPreviousPage: false
        startCursor: Y3Vyc29yOnYyOpHOABc7gA==
        endCursor: Y3Vyc29yOnYyOpHOABdCIA==
      edges[5]:
        - cursor: Y3Vyc29yOnYyOpHOABc7gA==
          node:
            id: I_kwDOADtDG85ZxOgA
            number: 54321
            title: Type inference fails for generic constrained types
            state: OP
...
```

</details>

<details><summary>graphql_union_types.json — 25.8% saved</summary>

**JSON (truncated):**
```json
{
  "data": {
    "search": {
      "issueCount": 3,
      "edges": [
        {
          "node": {
            "__typename": "Repository",
            "name": "react",
            "owner": {
              "login": "facebook"
            },
            "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
            "stargazerCount": 218000,
            "forkCount": 45123,
            "primaryLanguage": {
              "name": "JavaScript",
  
...
```

**TOON (truncated):**
```
data:
  search:
    issueCount: 3
    edges[5]:
      - node:
          __typename: Repository
          name: react
          owner:
            login: facebook
          description: "A declarative, efficient, and flexible JavaScript library for building user interfaces."
          stargazerCount: 218000
          forkCount: 45123
          primaryLanguage:
            name: JavaScript
            color: #f1e05a
          url: "https://github.com/facebook/react"
      - node:
          __typen
...
```

</details>

<details><summary>jsonld_activity_streams.json — 19.7% saved</summary>

**JSON (truncated):**
```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "OrderedCollection",
  "totalItems": 3,
  "orderedItems": [
    {
      "@context": "https://www.w3.org/ns/activitystreams",
      "type": "Create",
      "id": "https://social.example/activities/123",
      "actor": {
        "type": "Person",
        "id": "https://social.example/users/alice",
        "name": "Alice Johnson",
        "preferredUsername": "alice",
        "summary": "Software engineer and open source enthusiast"
...
```

**TOON (truncated):**
```
"@context": "https://www.w3.org/ns/activitystreams"
type: OrderedCollection
totalItems: 3
orderedItems[3]:
  - "@context": "https://www.w3.org/ns/activitystreams"
    type: Create
    id: "https://social.example/activities/123"
    actor:
      type: Person
      id: "https://social.example/users/alice"
      name: Alice Johnson
      preferredUsername: alice
      summary: Software engineer and open source enthusiast
      url: "https://social.example/@alice"
      icon:
        type: Image
   
...
```

</details>

<details><summary>jsonld_product_catalog.json — 27.5% saved</summary>

**JSON (truncated):**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "https://shop.example.com/products/laptop-pro-15",
  "name": "Professional Laptop Pro 15",
  "description": "High-performance laptop designed for professionals and creators with cutting-edge specifications",
  "image": [
    "https://shop.example.com/images/laptop-pro-15-front.jpg",
    "https://shop.example.com/images/laptop-pro-15-side.jpg",
    "https://shop.example.com/images/laptop-pro-15-keyboard.jpg"
  ],
  "brand": {
  
...
```

**TOON (truncated):**
```
"@context": "https://schema.org"
"@type": Product
"@id": "https://shop.example.com/products/laptop-pro-15"
name: Professional Laptop Pro 15
description: High-performance laptop designed for professionals and creators with cutting-edge specifications
image[3]: "https://shop.example.com/images/laptop-pro-15-front.jpg","https://shop.example.com/images/laptop-pro-15-side.jpg","https://shop.example.com/images/laptop-pro-15-keyboard.jpg"
brand:
  "@type": Brand
  name: TechCorp
  logo: "https://shop.e
...
```

</details>

<details><summary>jsonld_schema_org.json — 23.8% saved</summary>

**JSON (truncated):**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "https://example.com/products/wireless-headphones-pro",
  "name": "Wireless Headphones Pro",
  "description": "Premium wireless headphones with active noise cancellation, 30-hour battery life, and superior sound quality",
  "image": [
    "https://example.com/images/headphones-front.jpg",
    "https://example.com/images/headphones-side.jpg",
    "https://example.com/images/headphones-case.jpg"
  ],
  "sku": "WHP-2024-BLK",
  "m
...
```

**TOON (truncated):**
```
"@context": "https://schema.org"
"@type": Product
"@id": "https://example.com/products/wireless-headphones-pro"
name: Wireless Headphones Pro
description: "Premium wireless headphones with active noise cancellation, 30-hour battery life, and superior sound quality"
image[3]: "https://example.com/images/headphones-front.jpg","https://example.com/images/headphones-side.jpg","https://example.com/images/headphones-case.jpg"
sku: WHP-2024-BLK
mpn: 12345-ABCDE
brand:
  "@type": Brand
  name: AudioTech
...
```

</details>

<details><summary>openapi_github.json — 36.3% saved</summary>

**JSON (truncated):**
```json
{
  "openapi": "3.0.3",
  "info": {
    "title": "GitHub REST API",
    "description": "GitHub's REST API (subset)",
    "version": "1.1.4",
    "contact": {
      "name": "GitHub Support",
      "url": "https://support.github.com/contact"
    },
    "license": {
      "name": "MIT",
      "url": "https://spdx.org/licenses/MIT"
    }
  },
  "servers": [
    {
      "url": "https://api.github.com"
    }
  ],
  "paths": {
    "/repos/{owner}/{repo}": {
      "get": {
        "summary": "Get a repo
...
```

**TOON (truncated):**
```
openapi: 3.0.3
info:
  title: GitHub REST API
  description: GitHub's REST API (subset)
  version: 1.1.4
  contact:
    name: GitHub Support
    url: "https://support.github.com/contact"
  license:
    name: MIT
    url: "https://spdx.org/licenses/MIT"
servers[1]:
  - url: "https://api.github.com"
paths:
  "/repos/{owner}/{repo}":
    get:
      summary: Get a repository
      description: Get details for a specific repository
      operationId: repos/get
      parameters[2]:
        - name: own
...
```

</details>

<details><summary>openapi_petstore.json — 33.6% saved</summary>

**JSON (truncated):**
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Petstore API",
    "description": "A sample Pet Store Server based on the OpenAPI 3.0 specification",
    "version": "1.0.0",
    "contact": {
      "email": "api@example.com"
    },
    "license": {
      "name": "Apache 2.0",
      "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
    }
  },
  "servers": [
    {
      "url": "https://api.petstore.example.com/v1",
      "description": "Production server"
    },
    {
      "url": "https:/
...
```

**TOON (truncated):**
```
openapi: 3.0.0
info:
  title: Petstore API
  description: A sample Pet Store Server based on the OpenAPI 3.0 specification
  version: 1.0.0
  contact:
    email: api@example.com
  license:
    name: Apache 2.0
    url: "http://www.apache.org/licenses/LICENSE-2.0.html"
servers[2]{url,description}:
  "https://api.petstore.example.com/v1",Production server
  "https://staging-api.petstore.example.com/v1",Staging server
paths:
  "/pets":
    get:
      summary: List all pets
      description: Return
...
```

</details>

<details><summary>openapi_stripe.json — 35.0% saved</summary>

**JSON (truncated):**
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Stripe API",
    "description": "The Stripe REST API. Please see https://stripe.com/docs/api for more details.",
    "version": "2024-01-15",
    "contact": {
      "email": "dev-platform@stripe.com",
      "name": "Stripe Dev Platform Team",
      "url": "https://stripe.com/docs/support"
    }
  },
  "servers": [
    {
      "url": "https://api.stripe.com/v1"
    }
  ],
  "paths": {
    "/charges": {
      "get": {
        "summary": "List charg
...
```

**TOON (truncated):**
```
openapi: 3.0.0
info:
  title: Stripe API
  description: "The Stripe REST API. Please see https://stripe.com/docs/api for more details."
  version: 2024-01-15
  contact:
    email: dev-platform@stripe.com
    name: Stripe Dev Platform Team
    url: "https://stripe.com/docs/support"
servers[1]:
  - url: "https://api.stripe.com/v1"
paths:
  "/charges":
    get:
      summary: List charges
      description: "Returns a list of charges you've previously created. The charges are returned in sorted ord
...
```

</details>

<details><summary>rest_pagination_cursor.json — 45.8% saved</summary>

**JSON (truncated):**
```json
{
  "data": [
    {
      "id": "order_1",
      "customer_id": "cust_abc123",
      "total": 15999,
      "currency": "USD",
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "order_2",
      "customer_id": "cust_def456",
      "total": 8499,
      "currency": "USD",
      "status": "pending",
      "created_at": "2024-01-15T09:45:22Z"
    },
    {
      "id": "order_3",
      "customer_id": "cust_ghi789",
      "total": 32500,
      "currency": "U
...
```

**TOON (truncated):**
```
data[15]{id,customer_id,total,currency,status,created_at}:
  order_1,cust_abc123,15999,USD,completed,"2024-01-15T10:30:00Z"
  order_2,cust_def456,8499,USD,pending,"2024-01-15T09:45:22Z"
  order_3,cust_ghi789,32500,USD,completed,"2024-01-15T08:12:45Z"
  order_4,cust_jkl012,12750,USD,shipped,"2024-01-15T07:33:11Z"
  order_5,cust_mno345,5999,USD,completed,"2024-01-15T06:22:33Z"
  order_6,cust_pqr678,19999,USD,processing,"2024-01-15T05:11:44Z"
  order_7,cust_stu901,7250,USD,completed,"2024-01-15T04:
...
```

</details>

<details><summary>rest_pagination_link_header.json — 17.8% saved</summary>

**JSON (truncated):**
```json
{
  "data": [
    {
      "id": "user_2aB3C4d5E6",
      "email": "alice.johnson@example.com",
      "name": "Alice Johnson",
      "username": "alicej",
      "created_at": "2023-06-15T10:30:00Z",
      "updated_at": "2024-01-10T14:22:15Z",
      "status": "active",
      "role": "admin",
      "profile": {
        "avatar_url": "https://api.example.com/avatars/alicej.jpg",
        "bio": "Software engineer passionate about web technologies",
        "location": "San Francisco, CA",
        "we
...
```

**TOON (truncated):**
```
data[8]:
  - id: user_2aB3C4d5E6
    email: alice.johnson@example.com
    name: Alice Johnson
    username: alicej
    created_at: "2023-06-15T10:30:00Z"
    updated_at: "2024-01-10T14:22:15Z"
    status: active
    role: admin
    profile:
      avatar_url: "https://api.example.com/avatars/alicej.jpg"
      bio: Software engineer passionate about web technologies
      location: "San Francisco, CA"
      website: "https://alicejohnson.dev"
    settings:
      email_notifications: true
      two
...
```

</details>

<details><summary>rest_pagination_offset.json — 60.7% saved</summary>

**JSON (truncated):**
```json
{
  "total": 247,
  "limit": 20,
  "offset": 40,
  "results": [
    {
      "id": 41,
      "name": "Product Alpha",
      "description": "High-quality product with excellent features",
      "price": 299.99,
      "currency": "USD",
      "category": "Electronics",
      "in_stock": true,
      "rating": 4.5,
      "reviews_count": 128
    },
    {
      "id": 42,
      "name": "Product Beta",
      "description": "Innovative solution for modern needs",
      "price": 149.99,
      "currency": 
...
```

**TOON (truncated):**
```
total: 247
limit: 20
offset: 40
results[20]{id,name,description,price,currency,category,in_stock,rating,reviews_count}:
  41,Product Alpha,High-quality product with excellent features,299.99,USD,Electronics,true,4.5,128
  42,Product Beta,Innovative solution for modern needs,149.99,USD,Accessories,true,4.2,87
  43,Product Gamma,Premium quality at an affordable price,79.99,USD,Home & Garden,false,4.8,234
  44,Product Delta,Essential item for daily use,24.99,USD,Personal Care,true,4.1,56
  45,Produ
...
```

</details>

<details><summary>articles_classification_dataset.json — 10.1% saved</summary>

**JSON (truncated):**
```json
[
  {
    "id": "5096000",
    "title": "Diffusion-based spectral super-resolution of third octave acoustic sensor data: is privacy at risk ?",
    "abstract": "Third octave spectral recording of acoustic sensor data is an effective way of measuring the environment. While there is strong evidence that slow (1s frame, 1 Hz rate) and fast (125ms frame, 8Hz rate) versions lead by-design to unintelligible speech if reconstructed, the advent of high quality reconstruction methods based on diffusion m
...
```

**TOON (truncated):**
```
[22134]:
  - id: "5096000"
    title: "Diffusion-based spectral super-resolution of third octave acoustic sensor data: is privacy at risk ?"
    abstract: "Third octave spectral recording of acoustic sensor data is an effective way of measuring the environment. While there is strong evidence that slow (1s frame, 1 Hz rate) and fast (125ms frame, 8Hz rate) versions lead by-design to unintelligible speech if reconstructed, the advent of high quality reconstruction methods based on diffusion may po
...
```

</details>

<details><summary>nasdaq_timeseries_1h.json — 48.5% saved</summary>

**JSON (truncated):**
```json
[
  {
    "datetime": "2024-01-01 23:00:00",
    "symbol": "CME_MINI:NQ1!",
    "open": 17019.0,
    "high": 17037.0,
    "low": 17013.75,
    "close": 17029.5,
    "volume": 4582.0
  },
  {
    "datetime": "2024-01-02 00:00:00",
    "symbol": "CME_MINI:NQ1!",
    "open": 17030.0,
    "high": 17030.75,
    "low": 17018.5,
    "close": 17027.0,
    "volume": 2270.0
  },
  {
    "datetime": "2024-01-02 01:00:00",
    "symbol": "CME_MINI:NQ1!",
    "open": 17026.75,
    "high": 17038.5,
    "low": 
...
```

**TOON (truncated):**
```
[10504]{datetime,symbol,open,high,low,close,volume}:
  "2024-01-01 23:00:00","CME_MINI:NQ1!",17019,17037,17013.75,17029.5,4582
  "2024-01-02 00:00:00","CME_MINI:NQ1!",17030,17030.75,17018.5,17027,2270
  "2024-01-02 01:00:00","CME_MINI:NQ1!",17026.75,17038.5,17010.75,17014.5,5255
  "2024-01-02 02:00:00","CME_MINI:NQ1!",17014.5,17019,17001,17008.25,3541
  "2024-01-02 03:00:00","CME_MINI:NQ1!",17008.25,17013,17002.25,17007.5,2024
  "2024-01-02 04:00:00","CME_MINI:NQ1!",17007.25,17013,17003.25,17007
...
```

</details>
