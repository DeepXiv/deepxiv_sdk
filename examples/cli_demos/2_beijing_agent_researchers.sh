#!/usr/bin/env bash
# Demo 2: find Beijing-based LLM agent researchers with ask, search and read.
set -euo pipefail
cd "$(dirname "$0")" && source _common.sh

step "1. 先问：北京有哪些做 LLM Agent 的学者"
run deepxiv fa ask "北京有哪些做 LLM Agent（智能体）方向的学者？分资深学者和在校学生列出，说明各自的单位和代表方向" -d talent

step "2. 用过滤条件精确检索：base 北京、h-index ≥ 30"
run deepxiv fa search talent "LLM agent 智能体" -F location=北京 -F "h_index>=30" -k 10

step "3. 换成在校学生"
run deepxiv fa search talent "LLM agent 智能体" -F location=北京 -F career_stage=student -k 10

step "4. 一次读多份档案卡片（brief）"
run deepxiv fa read talent 522 2841 7541 4749 -l brief

step "5. 读一个人的完整档案：简介、教育、履历、代表作、指标"
run deepxiv fa read talent 522
