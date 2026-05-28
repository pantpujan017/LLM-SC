```text
RAW REVIEW TEXT
      │
      ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   LLM Parser    │────→│  JSON Output    │────→│  entities[]     │
│  (GPT/Claude)   │     │  per review     │     │  relations[]    │
└─────────────────┘     └─────────────────┘     │  sentiments[]   │
                                              └─────────────────┘
                                                      │
                              ┌─────────────────────┼─────────────────────┐
                              ▼                     ▼                     ▼
                        ┌─────────┐          ┌─────────┐          ┌─────────┐
                        │entities │          │relations│          │sentiments│
                        │ _table  │          │ _table  │          │ _table   │
                        │  .csv   │          │  .csv   │          │  .csv    │
                        └────┬────┘          └────┬────┘          └────┬────┘
                             │                    │                    │
                             └────────────────────┼────────────────────┘
                                                  ▼
                                        ┌─────────────────┐
                                        │  NODE MAPPING   │
                                        │ entity_type →   │
                                        │ V_attraction    │
                                        │ V_sentiment     │
                                        │ V_issue         │
                                        │ V_service       │
                                        └────────┬────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │  EDGE FILTERING │
                                        │ Keep only:      │
                                        │ co_occurrence   │
                                        │ causal          │
                                        └────────┬────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │ WEIGHT CALC     │
                                        │ w = 0.7·f_co +  │
                                        │     0.3·s_ca    │
                                        └────────┬────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │  NETWORK G(V,E) │
                                        │  300 nodes      │
                                        │  134 edges      │
                                        └────────┬────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │  CENTRALITY     │
                                        │ C(v)=deg/(n-1)  │
                                        │ Cross-category  │
                                        │ analysis        │
                                        └────────┬────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │ DECISION SUPPORT│
                                        │ • Guide services│
                                        │   are critical  │
                                        │ • Fix service   │
                                        │   issues first  │
                                        │ • Rituals drive │
                                        │   positive      │
                                        │   sentiment     │
                                        └─────────────────┘
```
