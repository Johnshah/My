# AI Engine scaffold

This folder will coordinate models and agents. Planned subcomponents:
- runners/ — integrators for llama.cpp, vLLM, Ollama, LocalAI
- agents/ — LangChain/MetaGPT/Auto-GPT orchestrations
- vision/ — Stable Diffusion, CLIP helpers

Security: all API keys must be kept in local config and never committed.

TODO: wire example runners and a simple local LLM health check.
