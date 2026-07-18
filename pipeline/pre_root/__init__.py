"""
pipeline/pre_root/ — طبقة قرار ما قبل الجذر
Pre-Root Boundary Closure Layer (PRBCL)

Five axes:
  1. article_projection    — فصل أداة التعريف «الـ» قبل الإرسال إلى HR2S
  2. morphology_path       — تصنيف المسار الصرفي بناءً على الشواهد البنيوية
  3. structural_aggregation — تجميع الأحكام البنيوية (BLOCK > DEFER > ACCEPT)
  4. attachment_roles      — تصنيف أدوار اللواحق والسوابق
  5. host_routing          — إغلاق المشغلات المركبة وتحديد المسار

Entry point:
  from pipeline.pre_root.pre_root_decision import assess_pre_root, PreRootDecision
"""
