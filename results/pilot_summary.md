# Pilot summary (50 items × 4 variants × 2 orders)

| judge | variant | n | invalid | acc | pos_cons | first_pos | flip | Δacc | McNemar p | flip 95% CI | Δacc 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gemini-2.5-flash | en | 100 | 0.000 | 0.840 | 0.960 | 0.520 | — | — | — | — | — |
| gemini-2.5-flash | hi_deva | 100 | 0.000 | 0.810 | 0.940 | 0.510 | 0.050 | -0.030 | 0.3750 | 0.014–0.083 | -0.065–0.015 |
| gemini-2.5-flash | hi_roman | 100 | 0.000 | 0.810 | 0.940 | 0.510 | 0.050 | -0.030 | 0.3750 | 0.015–0.083 | -0.067–0.015 |
| gemini-2.5-flash | hi_cm | 100 | 0.000 | 0.860 | 0.960 | 0.520 | 0.040 | 0.020 | 0.6250 | 0.015–0.067 | -0.016–0.048 |
| gemma-4-26b | en | 100 | 0.000 | 0.860 | 0.920 | 0.530 | — | — | — | — | — |
| gemma-4-26b | hi_deva | 100 | 0.000 | 0.830 | 0.900 | 0.480 | 0.110 | -0.030 | 0.5488 | 0.059–0.156 | -0.083–0.017 |
| gemma-4-26b | hi_roman | 100 | 0.000 | 0.780 | 0.880 | 0.510 | 0.100 | -0.080 | 0.0215 | 0.037–0.150 | -0.133–-0.016 |
| gemma-4-26b | hi_cm | 100 | 0.000 | 0.820 | 0.840 | 0.530 | 0.100 | -0.040 | 0.3438 | 0.050–0.145 | -0.091–0.016 |
| gpt-oss-120b | en | 100 | 0.000 | 0.850 | 0.980 | 0.510 | — | — | — | — | — |
| gpt-oss-120b | hi_deva | 100 | 0.000 | 0.720 | 0.880 | 0.520 | 0.150 | -0.130 | 0.0010 | 0.081–0.212 | -0.194–-0.059 |
| gpt-oss-120b | hi_roman | 100 | 0.000 | 0.700 | 0.880 | 0.480 | 0.170 | -0.150 | 0.0003 | 0.100–0.234 | -0.217–-0.078 |
| gpt-oss-120b | hi_cm | 100 | 0.000 | 0.760 | 0.840 | 0.540 | 0.150 | -0.090 | 0.0352 | 0.083–0.212 | -0.157–-0.017 |
| llama-3.1-8b | en | 100 | 0.000 | 0.610 | 0.740 | 0.630 | — | — | — | — | — |
| llama-3.1-8b | hi_deva | 100 | 0.000 | 0.540 | 0.680 | 0.660 | 0.170 | -0.070 | 0.1435 | 0.107–0.226 | -0.136–0.000 |
| llama-3.1-8b | hi_roman | 100 | 0.000 | 0.500 | 0.600 | 0.640 | 0.210 | -0.110 | 0.0266 | 0.145–0.266 | -0.183–-0.034 |
| llama-3.1-8b | hi_cm | 100 | 0.000 | 0.570 | 0.620 | 0.670 | 0.120 | -0.040 | 0.3877 | 0.071–0.167 | -0.089–0.015 |
| llama-3.3-70b | en | 100 | 0.000 | 0.810 | 0.900 | 0.550 | — | — | — | — | — |
| llama-3.3-70b | hi_deva | 100 | 0.000 | 0.760 | 0.840 | 0.560 | 0.090 | -0.050 | 0.1797 | 0.048–0.129 | -0.094–0.000 |
| llama-3.3-70b | hi_roman | 100 | 0.000 | 0.710 | 0.860 | 0.570 | 0.120 | -0.100 | 0.0063 | 0.062–0.177 | -0.156–-0.043 |
| llama-3.3-70b | hi_cm | 100 | 0.000 | 0.710 | 0.820 | 0.550 | 0.160 | -0.100 | 0.0213 | 0.100–0.222 | -0.161–-0.044 |
| qwen3-30b | en | 100 | 0.000 | 0.810 | 0.940 | 0.510 | — | — | — | — | — |
| qwen3-30b | hi_deva | 100 | 0.000 | 0.760 | 0.880 | 0.550 | 0.210 | -0.050 | 0.3833 | 0.129–0.281 | -0.136–0.032 |
| qwen3-30b | hi_roman | 100 | 0.000 | 0.730 | 0.820 | 0.600 | 0.200 | -0.080 | 0.1153 | 0.129–0.268 | -0.156–0.000 |
| qwen3-30b | hi_cm | 100 | 0.000 | 0.780 | 0.760 | 0.580 | 0.130 | -0.030 | 0.5811 | 0.083–0.177 | -0.083–0.029 |

## Cost
API calls: 2550 (0 errors)
Estimated total cost: **$1.3964** (token-based; Workers AI actually bills in neurons — raw `neurons` logged per call)

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