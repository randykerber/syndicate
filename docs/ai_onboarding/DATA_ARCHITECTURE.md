# Data Architecture: The Medallion Model & The `~/d/` Warehouse

This document explains the project's data storage philosophy. Understanding this is critical before reading or writing any data.

## The Guiding Principle

The `syndicate` project is the **engine** that operates on the user's data warehouse. The data warehouse lives at `~/d/`. The project directory should **never** contain persistent data; it only contains code, configs, and docs.

## The Medallion Architecture

We use the industry-standard Medallion Architecture to organize the data warehouse. It consists of three layers:

### 1. Bronze Layer: Raw Data
- **Location**: `~/d/downloads/`
- **Purpose**: An immutable, append-only archive of raw source data, exactly as it was received. This is the "source of truth."
- **Characteristics**: Data is never changed. We can always replay our pipelines from this layer.
- **Example**: Raw YouTube transcripts are stored at `~/d/downloads/youtube/transcripts/`.

### 2. Silver Layer: Cleaned & Structured Data
- **Location**: `~/d/prod/`
- **Purpose**: Stores validated, cleaned, and structured data products. This is the trustworthy layer for applications to consume.
- **Characteristics**: Data is machine-readable, often in formats like JSON or Parquet.
- **Example**: The structured JSON output from our `YouTubeTriageAgent` is saved to `~/d/prod/youtube/triage_summaries/`.

### 3. Gold Layer: Curated & Aggregated Views
- **Location**: `~/d/view/`
- **Purpose**: Stores highly refined, aggregated data tailored for final human consumption.
- **Characteristics**: Data is formatted for a specific application, like a report or a knowledge base entry.
- **Example**: Extracted "nuggets" for Obsidian will be saved as Markdown files in `~/d/view/youtube/extractions/`.

## Configuration

The application code finds these paths via the configuration file at `@python/config/sss/config.yaml`. This file uses variable substitution to build the full paths, and the loading is handled by the utility at `@python/src/shared/config.py`.
