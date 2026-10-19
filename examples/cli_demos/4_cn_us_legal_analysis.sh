#!/usr/bin/env bash
# Demo 4: one legal question, analysed under Chinese and US law with cases,
# written up as a consulting report.
set -euo pipefail
cd "$(dirname "$0")" && source _common.sh
REPORT=report_cn_us_data_compliance.md
Q="一家中国跨境电商公司计划在美国开展业务，会收集美国用户的个人信息，并希望把数据传回国内总部做分析"

step "问题：$Q"

step "1. 中国法规：数据出境条件"
run deepxiv fa search law "个人信息出境 数据出境安全评估" -k 5

step "2. 美国法规：加州 CCPA 与联邦对外国对手的数据转移禁令"
run deepxiv fa search us_law "consumer data privacy notice sale of personal information" -F jurisdiction=ca -k 5
run deepxiv fa search us_law "foreign adversary sensitive personal data transfer" -k 3

step "3. 中国判例：违规提供个人信息"
run deepxiv fa search cases "个人信息 向境外提供 侵权" -F country=cn -k 5

step "4. 美国判例：TikTok 案、BIPA 集体诉讼"
run deepxiv fa search cases "TikTok foreign adversary controlled application data national security" -F country=us -k 3
run deepxiv fa search cases "biometric information privacy act consent class action" -F country=us -F court_level=state_supreme -k 3
run deepxiv fa read cases us:10316651 -l brief
run deepxiv fa read cases us:4658484 -l brief

step "5. 生成咨询报告 → $REPORT"
{
  echo "# 中国跨境电商赴美业务的数据合规咨询报告"
  echo
  echo "**问题**：$Q。"
  echo
  echo "## 一、中国法律：数据出境"
  echo
} > "$REPORT"
run deepxiv fa ask "$Q。从中国法律角度：数据出境需要满足哪些条件、走什么程序、违规有什么后果？" \
  -d law -p scope=both >> "$REPORT"
printf '\n## 二、美国法律：联邦与加州\n\n' >> "$REPORT"
run deepxiv fa ask "$Q. Under US federal and state law (e.g. California), what obligations and restrictions apply, including rules on transferring Americans' sensitive data to China? Answer in Chinese." \
  -d us_law >> "$REPORT"
printf '\n## 三、中国判例：法院如何认定\n\n' >> "$REPORT"
run deepxiv fa ask "企业违规收集、向境外提供个人信息被处罚或判刑的典型案例有哪些？法院如何认定？" \
  -d cases >> "$REPORT"

step "完成：$REPORT"
