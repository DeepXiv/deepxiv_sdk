#!/usr/bin/env bash
# Demo 3: for one author's five top papers, find what academicians and fellows said
# when they cited them, and write a report (answers go to stdout, sources to stderr).
set -euo pipefail
cd "$(dirname "$0")" && source _common.sh
REPORT=report_kaiming_he.md

step "1. 找到作者，看代表作"
run deepxiv fa search talent "Kaiming He" -k 3
run deepxiv fa read talent 901 -l brief

# Top 5 papers from the profile above:
# ResNet, Faster R-CNN, Mask R-CNN, Focal Loss (RetinaNet), FPN
PAPERS=(
  "1512.03385|Deep Residual Learning for Image Recognition (ResNet)"
  "1506.01497|Faster R-CNN"
  "1703.06870|Mask R-CNN"
  "1708.02002|Focal Loss for Dense Object Detection (RetinaNet)"
  "1612.03144|Feature Pyramid Networks (FPN)"
)

step "2. 每篇被多少院士 / Fellow 引用，正面 / 中性 / 负面各多少"
for p in "${PAPERS[@]}"; do
  run deepxiv fa read appraise "arxiv:${p%%|*}" -l brief
done

step "3. 看一篇的正面评价原句（只看中科院、工程院院士）"
run deepxiv fa read appraise arxiv:1512.03385 -p stance=positive -p org=CAS,CAE

step "4. 逐篇生成评价报告 → $REPORT"
{
  echo "# 何恺明（Kaiming He）五项代表工作的院士 / Fellow 评价"
  echo
  echo "数据：deepxiv fa appraise（院士与会士署名论文中的引用原句，引用态度由模型标注，原句可核）"
} > "$REPORT"
for p in "${PAPERS[@]}"; do
  id=${p%%|*}; title=${p#*|}
  printf '\n## %s（arXiv:%s）\n\n' "$title" "$id" >> "$REPORT"
  run deepxiv fa ask "这篇论文得到了哪些院士和 Fellow 的正面评价？按人列出评价人、身份、单位和原话" \
    -d appraise -p paper="arxiv:$id" >> "$REPORT"
done

step "完成：$REPORT"
