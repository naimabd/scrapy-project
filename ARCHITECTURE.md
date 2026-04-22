# Architecture

## Overview
The solution is implemented as a two-stage pipeline using **Dagster** for orchestration and **Scrapy** for data extraction. The system maintains clear data-zone separation:
- **Landing Zone**: Raw metadata + raw files (PDF, DOC, HTML).
- **Processed Zone**: Cleaned HTML content + renamed files (identifier-based).

Storage services are containerized for reliability:
- **MongoDB**: Stores metadata and tracking information.
- **MinIO (S3)**: Stores binary document data.

## Orchestration
The pipeline is defined as **Software-Defined Assets** in Dagster, partitioned by **Legal Body** and **Month**. This allows for:
- Granular backfills of historical data.
- Automatic dependency management (Scrape -> Transform).
- Parallel execution of partitions.

## Scraping Strategy
The ingestion uses an asynchronous, non-blocking Scrapy spider:
- **Performance**: Uses `response.follow` to crawl detail pages without blocking the engine.
- **Politeness**: Implements `RotatingUserAgentMiddleware` and configurable delays.
- **Resilience**: Uses exponential backoff and Scrapy's built-in retry mechanisms.

## Partitioning Strategy
Monthly partitioning is used by default because it balances:
- **Throughput**: Avoids extremely large single-run windows.
- **Isolation**: Failed months can be retried independently without affecting others.
- **Observability**: Clear partition-level success/failure metrics.

## Deduplication and Idempotency
Each record has a deterministic `record_key`: `source_body|identifier|partition_date`.
- **Metadata**: MongoDB uses a unique index on `record_key` to ensure upsert safety.
- **Files**: Content-based hashing (SHA-256) ensures files are only uploaded if they are new or have changed.

## Scaling to 100+ Sources
To support many sources, the system is designed for extension:
- **Source-Specific Spiders**: New sources can be added by implementing the same metadata interface.
- **Dynamic Dispatch**: The orchestrator can dynamically launch appropriate spiders based on source configuration.
- **Distributed Workers**: For massive scale, Dagster can distribute partition execution across a cluster of workers (e.g., Kubernetes).

