# StevenAI Runtime

StevenAI is the identity-and-retrieval layer for the Genesis project. The underlying model is deliberately replaceable.

## Runtime contract

- Identity and canonical invariants live in `canon.py`.
- Public authored corpus is retrieved locally through `retrieval.py`.
- OpenAI inference is provided by the Agents SDK in `agent.py`.
- The provider key is read only from `OPENAI_API_KEY`.
- The default model is `gpt-5.6`; override with `STEVENAI_MODEL`.
- No API key belongs in Git, source files, prompts, or checked-in configuration.

## Epistemic boundary

StevenAI can work fluently with the Synthsara mythic/cosmological framework while keeping empirical claims distinct from symbolic or spiritual interpretation. Retrieved corpus never overrides the canonical invariants silently.

## Next retrieval upgrade

The local lexical retriever is intentionally small and inspectable. It can later be swapped for an OpenAI vector store / file-search backend without changing the StevenAI identity contract.
