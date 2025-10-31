# Real-World API Response Samples

This directory contains real-world API response examples used for TOON format compatibility and token efficiency benchmarking.

## Sample Categories

### GitHub API (`github_*.json`)
- **github_repo_list.json**: Repository search results
- **github_user_profile.json**: User profile with repositories
- **github_issue_detail.json**: Issue with comments and reactions
- **github_pull_request.json**: Pull request with reviews and commits
- **github_commit_history.json**: Commit history with file changes

Source: GitHub REST API v3 (https://docs.github.com/en/rest)

### OpenAPI Specifications (`openapi_*.json`)
- **openapi_petstore.json**: Classic Petstore API spec
- **openapi_stripe.json**: Stripe API specification (subset)
- **openapi_github.json**: GitHub API OpenAPI spec (subset)

Source: OpenAPI Specification examples (https://github.com/OAI/OpenAPI-Specification/tree/main/examples)

### GraphQL Responses (`graphql_*.json`)
- **graphql_nested_query.json**: Deeply nested query with fragments
- **graphql_union_types.json**: Response with union types
- **graphql_pagination.json**: Paginated connection with edges/nodes

Source: GraphQL public APIs (GitHub GraphQL API, SpaceX API)

### REST Pagination (`rest_pagination_*.json`)
- **rest_pagination_offset.json**: Offset-based pagination
- **rest_pagination_cursor.json**: Cursor-based pagination
- **rest_pagination_link_header.json**: Link header pagination (RFC 5988)

Source: Various public REST APIs

### JSON-LD (`jsonld_*.json`)
- **jsonld_schema_org.json**: Schema.org structured data
- **jsonld_activity_streams.json**: Activity Streams 2.0 example
- **jsonld_product_catalog.json**: E-commerce product with rich metadata

Source: JSON-LD examples (https://json-ld.org/playground/)

### Recipes Dataset
- **recipes_json.json**: Large-scale recipe dataset (64,000+ recipes, 320+ categories)
  - Structure: Uniform array of recipe objects
  - Fields: title, category, subcategory, ingredients (list), directions (list), ingredient count, step count
  - Size: ~82MB (ideal for testing TOON's tabular format optimization)
  - Use case: Tests TOON performance on large uniform datasets

Source: Public recipe dataset (cleaned and structured)

### Time-Series Data (`nasdaq_*.json`, `timeseries_*.json`)
- **nasdaq_timeseries_1h.json**: E-mini Nasdaq-100 Futures (NQ) OHLCV data
  - Structure: Uniform array of time-series records
  - Fields: datetime, symbol, open, high, low, close, volume
  - Records: 10,504 hourly candles (Jan 2024 - Oct 2025)
  - Size: ~2MB
  - Use case: Tests TOON with temporal/numeric data patterns (financial, IoT, sensor data)

Source: CME E-mini Nasdaq-100 Futures data from TradingView (cleaned and aggregated)

### Scientific Articles (`articles_*.json`)
- **articles_classification_dataset.json**: Academic/scientific article metadata
  - Structure: Uniform array of article objects
  - Fields: id, title, abstract, keywords (array), authors (array), venue, date, teams (array)
  - Records: 22,134 articles
  - Size: ~38MB
  - Use case: Tests TOON with text-heavy data and nested string arrays

Source: Scientific article classification dataset (academic metadata)

**Note on Large Datasets:** The benchmark automatically samples large files (>10MB) by taking the first 1,000 records for validation. This provides representative results while maintaining reasonable runtime. The full dataset demonstrates TOON's scalability for production use cases.

## Data Collection

All samples are **manually curated** from public APIs and open-source examples. The benchmark uses these static JSON files rather than fetching data dynamically. No authentication tokens or sensitive data are included.

**Note:** Automatic data collectors are intentionally **not implemented**. Samples are curated offline to ensure:
- Reproducibility across benchmark runs
- No dependency on external API availability or rate limits
- Consistent test data for regression testing
- Privacy and security (no API keys or credentials needed)

If you need to add new samples, manually download or construct representative API responses and save them as JSON files in this directory.

## Licensing

Samples are used for benchmarking purposes under fair use. Original API providers retain all rights to their data formats and specifications.

## Adding New Samples

1. Collect response from public API (remove sensitive data)
2. Validate JSON format: `python -m json.tool < sample.json`
3. Name file with pattern prefix: `{pattern}_{description}.json`
4. Update this README with source and description
5. Run benchmark to verify compatibility: `python -m benchmarks --realworld`
