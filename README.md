# Monday.com Business Intelligence Agent

AI-powered Business Intelligence Agent that answers founder-level business questions using live monday.com data, with robust data cleaning, dynamic schema resolution, and cross-board financial insights.

## Overview

Founders need fast, reliable answers to questions like:

"How’s our pipeline looking for the mining sector?"

"What’s our outstanding receivable for manufacturing?"

"How is the energy sector performing this quarter?"

Manually extracting, cleaning, and analyzing monday.com data is slow and error-prone.

This project solves that by building an AI agent that:

*   Connects to monday.com in real time
*   Cleans messy business data
*   Interprets founder-level queries
*   Performs cross-board analysis
*   Produces structured executive summaries
*   Displays full tool-call trace transparency

## System Architecture

User -> Streamlit UI -> LLM (Groq) -> Tool Call -> Live Monday API
                                              |
                                        Data Cleaning
                                              |
                                       BI Engine Logic
                                              |
                                      Executive Summary

## Components

| Module | Responsibility |
| :--- | :--- |
| app.py | Conversational interface + tool-calling orchestration |
| monday_client.py | Live monday.com GraphQL integration |
| data_cleaning.py | Raw API -> Clean Pandas DataFrames |
| tools.py | Tool-call handler + dynamic column mapping |
| bi_engine.py | Core Business Intelligence logic |

## Assignment Requirements - Compliance Summary

### 1. Live Monday.com Integration

*   Uses official monday.com GraphQL API
*   Every query triggers fresh API calls
*   No caching or preloading
*   Boards fetched at runtime
*   Column metadata dynamically read

- Fully live
- No hardcoded schema dependency

### 2. Data Resilience (Messy Data Handling)

Real-world business data is messy. The system handles:

*   Missing/null values
*   Empty numeric fields
*   Currency symbols and commas
*   Inconsistent formats
*   Date parsing issues

Techniques used:

*   Regex numeric normalization
*   pd.to_numeric(..., errors='coerce')
*   Defensive column fallback logic
*   Data quality reporting in summary

Each response includes:

**Data Quality Commentary:**
Identified X deals with missing value information.

This ensures transparency for executive decisions.

### 3. Query Understanding

The agent supports:

*   Sector-based filtering
*   Quarter-based filtering:
    *   "this quarter"
    *   "last quarter"
    *   "Q2 2025"
*   Follow-up queries:
    *   "And for manufacturing?"
*   Context awareness
*   Clarification when sector missing

Example supported queries:

*   "How is our pipeline for mining?"
*   "Compare pipeline and collections for mining."
*   "How’s mining this quarter?"
*   "And for manufacturing?"

### 4. Business Intelligence Capabilities

The agent performs cross-board analysis across:

**Deals Board**
*   Total Open Deals
*   Pipeline Value
*   Average Deal Size
*   Probability distribution
*   Stage distribution (active only)

**Work Orders Board**
*   Total Billed
*   Total Collected
*   Outstanding Receivables

Pipeline logic excludes:
*   Lost deals
*   Completed projects
*   Not relevant
*   On hold

Ensuring metrics reflect true active pipeline health.

### 5. Agent Action Visibility

The UI displays full trace:
*   Board metadata
*   Column types
*   Sample rows
*   Resolved column mapping
*   Time filter application
*   Live API fetch confirmation

This ensures complete transparency in how answers are derived.

## Example Output

### Executive Summary: MINING SECTOR (THIS QUARTER)

**Pipeline Insights:**
*   Total Open Deals: 8
*   Total Pipeline Value: Rs 28,994,580.00
*   Average Deal Size: Rs 3,624,322.50
*   High Probability Deals: 50.0% (4 deals)
*   Stage Distribution: Sales Qualified Leads, Proposal, Negotiations

**Financial Health:**
*   Total Billed: Rs 30,613,415.27
*   Total Collected: Rs 17,369,515.69
*   Outstanding Receivable: Rs 13,244,228.74

**Data Quality Commentary:**
*   Identified 0 deals with missing value information.

## Key Engineering Decisions

### 1. Dynamic Column Resolution

Instead of hardcoding column IDs, the system:
*   Reads board metadata
*   Maps columns by title + type
*   Falls back safely when necessary

This makes the system robust to board schema changes.

### 2. Real Pipeline Semantics

Pipeline excludes:
*   Lost
*   Completed
*   Not Relevant
*   On Hold

Ensuring only revenue-relevant opportunities are included.

### 3. Time-Aware Filtering

Implements quarter parsing and dynamic filtering using:
*   Tentative Close Date (primary)
*   Close Date (fallback)

This directly supports the assignment example:
"How’s our pipeline for the energy sector this quarter?"

### 4. No Hallucination Design

All responses:
*   Derived strictly from tool output
*   No hardcoded numbers
*   No general knowledge responses
*   Fully data-driven

## Tech Stack

*   Python
*   Streamlit (UI)
*   Groq LLM (tool-calling)
*   monday.com GraphQL API
*   Pandas (data processing)

## Setup Instructions

1.  Clone repository
2.  Create .env file:
    ```
    GROQ_API_KEY=your_key
    MONDAY_API_KEY=your_key
    DEALS_BOARD_ID=your_board_id
    WORK_BOARD_ID=your_board_id
    ```
3.  Install dependencies:
    ```
    pip install -r requirements.txt
    ```
4.  Run:
    ```
    streamlit run app.py
    ```

## Testing Strategy

System tested against:
*   Missing numeric values
*   Currency-formatted values
*   Empty sectors
*   Nonexistent sectors
*   Follow-up queries
*   Quarter filters
*   Cross-board queries

All responses verified against live monday.com data.

## Why This Design

The goal was not just to "call an API and summarize". The system was designed to:
*   Mimic real executive BI workflows
*   Handle messy operational data
*   Be transparent in reasoning
*   Be resilient to schema changes
*   Avoid hallucinated responses

## Deliverables Included

*   Source code
*   README
*   Decision Log (separate)
*   Live monday.com board integration
*   Visible tool-call trace

## Final Notes

This project demonstrates:
*   AI tool-calling architecture
*   Live enterprise API integration
*   Data normalization
*   Cross-board BI computation
*   Conversational state handling
*   Executive-level reporting logic

It is designed to function as a real-world BI assistant for founders and operators.