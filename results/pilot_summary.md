# Pilot summary (50 items × 4 variants × 2 orders)

| judge | variant | n | invalid | acc | pos_cons | first_pos | flip | Δacc | McNemar p | flip 95% CI | Δacc 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-4-5 | en | 100 | 0.000 | 0.710 | 0.860 | 0.530 | — | — | — | — | — |
| claude-haiku-4-5 | hi_deva | 100 | 0.000 | 0.750 | 0.740 | 0.530 | 0.220 | 0.040 | 0.5235 | 0.153–0.283 | -0.034–0.109 |
| claude-haiku-4-5 | hi_roman | 100 | 0.000 | 0.670 | 0.740 | 0.570 | 0.200 | -0.040 | 0.5034 | 0.133–0.265 | -0.113–0.031 |
| claude-haiku-4-5 | hi_cm | 100 | 0.000 | 0.740 | 0.800 | 0.540 | 0.170 | 0.030 | 0.6291 | 0.109–0.226 | -0.033–0.091 |
| gemma-4-26b | en | 100 | 0.000 | 0.850 | 0.860 | 0.570 | — | — | — | — | — |
| gemma-4-26b | hi_deva | 100 | 0.000 | 0.820 | 0.880 | 0.530 | 0.110 | -0.030 | 0.5488 | 0.061–0.155 | -0.081–0.018 |
| gemma-4-26b | hi_roman | 100 | 0.000 | 0.750 | 0.980 | 0.520 | 0.160 | -0.100 | 0.0213 | 0.086–0.227 | -0.171–-0.017 |
| gemma-4-26b | hi_cm | 100 | 0.000 | 0.860 | 0.960 | 0.510 | 0.090 | 0.010 | 1.0000 | 0.045–0.133 | -0.031–0.048 |
| gpt-oss-120b | en | 100 | 0.000 | 0.840 | 0.960 | 0.520 | — | — | — | — | — |
| gpt-oss-120b | hi_deva | 100 | 0.000 | 0.760 | 0.840 | 0.520 | 0.140 | -0.080 | 0.0574 | 0.081–0.194 | -0.141–-0.016 |
| gpt-oss-120b | hi_roman | 100 | 0.000 | 0.680 | 0.840 | 0.500 | 0.200 | -0.160 | 0.0004 | 0.129–0.267 | -0.233–-0.083 |
| gpt-oss-120b | hi_cm | 100 | 0.000 | 0.770 | 0.940 | 0.530 | 0.130 | -0.070 | 0.0923 | 0.061–0.194 | -0.138–0.000 |
| llama-3.1-8b | en | 100 | 0.000 | 0.610 | 0.740 | 0.630 | — | — | — | — | — |
| llama-3.1-8b | hi_deva | 100 | 0.000 | 0.560 | 0.600 | 0.660 | 0.130 | -0.050 | 0.2668 | 0.083–0.177 | -0.103–0.000 |
| llama-3.1-8b | hi_roman | 100 | 0.000 | 0.470 | 0.580 | 0.650 | 0.280 | -0.140 | 0.0125 | 0.206–0.348 | -0.233–-0.048 |
| llama-3.1-8b | hi_cm | 100 | 0.000 | 0.570 | 0.660 | 0.650 | 0.120 | -0.040 | 0.3877 | 0.074–0.167 | -0.091–0.016 |
| llama-3.3-70b | en | 100 | 0.000 | 0.810 | 0.900 | 0.550 | — | — | — | — | — |
| llama-3.3-70b | hi_deva | 100 | 0.000 | 0.740 | 0.840 | 0.580 | 0.110 | -0.070 | 0.0654 | 0.061–0.156 | -0.121–-0.016 |
| llama-3.3-70b | hi_roman | 100 | 0.000 | 0.680 | 0.840 | 0.580 | 0.150 | -0.130 | 0.0010 | 0.091–0.210 | -0.188–-0.067 |
| llama-3.3-70b | hi_cm | 100 | 0.000 | 0.730 | 0.780 | 0.570 | 0.120 | -0.080 | 0.0386 | 0.069–0.167 | -0.133–-0.030 |
| qwen3-30b | en | 100 | 0.000 | 0.790 | 0.820 | 0.510 | — | — | — | — | — |
| qwen3-30b | hi_deva | 100 | 0.010 | 0.778 | 0.760 | 0.545 | 0.111 | -0.012 | 1.0000 | 0.065–0.154 | -0.064–0.036 |
| qwen3-30b | hi_roman | 100 | 0.000 | 0.710 | 0.820 | 0.490 | 0.200 | -0.080 | 0.1153 | 0.133–0.266 | -0.155–0.000 |
| qwen3-30b | hi_cm | 100 | 0.000 | 0.780 | 0.840 | 0.510 | 0.110 | -0.010 | 1.0000 | 0.059–0.156 | -0.052–0.034 |

## Cost
API calls: 5100 (0 errors)
Estimated total cost: **$2.7296** (token-based; Workers AI actually bills in neurons — raw `neurons` logged per call)

PRICES used:
```json
{
 "workers-ai/@cf/meta/llama-3.3-70b-instruct-fp8-fast": {
  "in": 0.293,
  "out": 2.253,
  "src": "https://developers.cloudflare.com/workers-ai/platform/pricing/"
 },
 "workers-ai/@cf/openai/gpt-oss-120b": {
  "in": 0.35,
  "out": 0.75,
  "src": "https://developers.cloudflare.com/workers-ai/platform/pricing/"
 },
 "workers-ai/@cf/qwen/qwen3-30b-a3b-fp8": {
  "in": 0.2,
  "out": 0.6,
  "src": "https://developers.cloudflare.com/workers-ai/platform/pricing/"
 },
 "workers-ai/@cf/google/gemma-4-26b-a4b-it": {
  "in": 0.3,
  "out": 0.9,
  "src": "estimate \u2014 not listed; gemma-class assumed"
 },
 "workers-ai/@cf/meta/llama-3.1-8b-instruct-fp8": {
  "in": 0.045,
  "out": 0.384,
  "src": "https://developers.cloudflare.com/workers-ai/platform/pricing/"
 },
 "google-ai-studio/gemini-2.5-pro": {
  "in": 1.25,
  "out": 10.0,
  "src": "https://ai.google.dev/gemini-api/docs/pricing"
 },
 "google-ai-studio/gemini-2.5-flash": {
  "in": 0.3,
  "out": 2.5,
  "src": "https://ai.google.dev/gemini-api/docs/pricing"
 }
}
```