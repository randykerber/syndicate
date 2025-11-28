# AI Assistant Onboarding: START HERE

This document provides the essential context for any AI assistant working on the `syndicate` project.

## Current High-Level Objective

The primary goal is to develop a system of AI agents to assist with **YouTube content triage and extraction**. The user wants to quickly decide if a video is worth watching and, if so, extract valuable information for their knowledge base (Obsidian).

## Current Status

We are in the **requirements exploration phase**. We are not writing production code yet. Instead, we are using an interactive, conversational process to define what a "good" interaction looks like. We have completed one full use case.

## Key Decisions & Architecture

Before writing any code, you must understand these core decisions:

1.  **Code Architecture**: The old `SyndicateAgent` class is **DEPRECATED**. All new agents **must** inherit from the `SSSAgent` base class located at `@python/src/sss/agents/base.py`.
2.  **Data Architecture**: The project's data storage follows the **Medallion Architecture** (Bronze, Silver, Gold). This is the most critical concept to understand. All data is stored outside the project in the user's `~/d/` directory.
3.  **Development Process**: We use a **"Live Documentation"** method. We collaboratively create use case documents *before* implementing features.

## Path to Understanding

To get up to speed, please read the following documents in order:

1.  **`DATA_ARCHITECTURE.md`**: To understand where all data lives and why. This is non-negotiable.
2.  **`CODE_ARCHITECTURE.md`**: To understand the standards for writing agent code.
3.  **`DEVELOPMENT_PROCESS.md`**: To understand our current workflow and how to contribute.

After reading these, you will be fully briefed and ready to assist.
