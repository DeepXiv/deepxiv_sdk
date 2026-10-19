#!/usr/bin/env bash
# Demo 1: progressive reading. Each step costs about 10x more tokens than the last,
# so an agent stops as soon as it has what it needs.
set -euo pipefail
cd "$(dirname "$0")" && source _common.sh

step "1. 检索：只看标题和摘要，判断哪篇值得读"
run deepxiv search "speculative decoding diffusion drafter" --date-from 2025-01 --limit 5

step "2. Brief（~300 tokens）：TLDR、关键词、引用数，决定读不读"
run deepxiv paper 2512.15176 --brief

step "3. Head：章节列表和每节的 token 数，决定读哪一节"
run deepxiv paper 2512.15176 --head

step "4. Section：只读实验这一节，不加载全文"
run deepxiv paper 2512.15176 --section Experiment

step "5. 有具体问题时，直接问文献，答案带 arXiv 引用"
run deepxiv ask "DEER 在 HumanEval 上相比 EAGLE-3 的加速比是多少？草稿接受长度是多少？"
