#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline/p2_augmented/ — AugmentedHostRefinement (Forms II–X)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

طبقة تكتشف أفعال المزيد (Form II–X) من سطح المضيف المنقَّح
وتستخلص الجذر الثلاثي مباشرةً، متجاوزةً المحرك الثلاثي.

واجهة عامة:
    from pipeline.p2_augmented.augmented_host_refinement import analyze_augmented_host
"""

from pipeline.p2_augmented.augmented_host_refinement import analyze_augmented_host
from pipeline.p2_augmented.models import AugmentedRootAnalysis

__all__ = ['analyze_augmented_host', 'AugmentedRootAnalysis']
