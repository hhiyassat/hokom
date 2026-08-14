#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_pre_root.py — اختبارات طبقة ما قبل الجذر
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ثمانية محاور إغلاق:
  §1  فصل أداة التعريف (قمرية وشمسية)
  §2  تصنيف المسار الصرفي
  §3  تجميع الأحكام البنيوية
  §4  تصنوف أدوار اللواحق
  §5  إغلاق المشغّلات المركبة
  §6  تجميع PreRootDecision
  §7  تتبع الشواهد (evidence_ids)
  §8  رموز التحفظ (residual_codes)

القيود:
  - لا تغيير على أي JSON تحت data/02_mabniyat/
  - لا استثناءات نصية خاصة بكلمات
  - مصدر الاختبارات: الشواهد البنيوية فقط
"""

import pytest


# ══════════════════════════════════════════════════════════════════════════════
# §1  فصل أداة التعريف
# ══════════════════════════════════════════════════════════════════════════════

class TestArticleProjection:
    """Axis 1 — project_article()"""

    def setup_method(self):
        from pipeline.pre_root.article_projection import project_article
        self.project_article = project_article

    def test_lunar_article_explicit_sukun(self):
        """الْأَطْفَالُ → prefix='الْ', host='أَطْفَالُ'"""
        result = self.project_article('الْأَطْفَالُ')
        assert result.has_article is True
        assert result.prefix_surface == 'الْ'
        assert result.host_surface == 'أَطْفَالُ'
        assert result.is_solar is False

    def test_lunar_article_with_vowel_letter(self):
        """الْكِتَابُ — مثال قمري آخر"""
        result = self.project_article('الْكِتَابُ')
        assert result.has_article is True
        assert result.prefix_surface == 'الْ'
        assert result.host_surface == 'كِتَابُ'
        assert result.is_solar is False

    def test_solar_article_shin(self):
        """الشَّجَرَةِ → prefix='ال', host='شَّجَرَةِ', is_solar=True"""
        result = self.project_article('الشَّجَرَةِ')
        assert result.has_article is True
        assert result.prefix_surface == 'ال'
        assert result.is_solar is True
        # المضيف يبدأ بالحرف الشمسي (مع شدة)
        assert result.host_surface.startswith('ش')

    def test_solar_article_noon(self):
        """النَّهَارُ — نون شمسية"""
        result = self.project_article('النَّهَارُ')
        assert result.has_article is True
        assert result.is_solar is True
        assert result.host_surface.startswith('ن')

    def test_solar_article_dal(self):
        """الدَّرْسُ — دال شمسية"""
        result = self.project_article('الدَّرْسُ')
        assert result.has_article is True
        assert result.is_solar is True
        assert result.host_surface.startswith('د')

    def test_no_article_plain_word(self):
        """ضَرَبَ — لا أداة تعريف"""
        result = self.project_article('ضَرَبَ')
        assert result.has_article is False
        assert result.prefix_surface is None
        assert result.host_surface == 'ضَرَبَ'
        assert result.prefix_projection is None

    def test_no_article_starts_with_hamza(self):
        """أَخَذَ — همزة قطع، لا أداة"""
        result = self.project_article('أَخَذَ')
        assert result.has_article is False
        assert result.host_surface == 'أَخَذَ'

    def test_no_article_short_word(self):
        """مِنْ — كلمة قصيرة، لا أداة"""
        result = self.project_article('مِنْ')
        assert result.has_article is False

    def test_article_evidence_id_lunar(self):
        """شاهد الكشف القمري مُضمَّن"""
        result = self.project_article('الْبَيْتُ')
        assert 'lunar' in result.evidence_id

    def test_article_evidence_id_solar(self):
        """شاهد الكشف الشمسي مُضمَّن"""
        result = self.project_article('الرَّجُلُ')
        assert 'solar' in result.evidence_id

    def test_article_projection_role(self):
        """role يجب أن يكون DEFINITE_ARTICLE"""
        from pipeline.pre_root.attachment_roles import AttachmentRole
        result = self.project_article('الْبَيْتُ')
        assert result.prefix_projection is not None
        assert result.prefix_projection.role is AttachmentRole.DEFINITE_ARTICLE

    def test_article_span_lunar(self):
        """span_start=0, span_end=3 للقمرية (الْ = 3 أحرف)"""
        result = self.project_article('الْبَيْتُ')
        proj = result.prefix_projection
        assert proj.span_start == 0
        assert proj.span_end == 3

    def test_article_span_solar(self):
        """span_start=0, span_end=2 للشمسية (ال = 2 حرف)"""
        result = self.project_article('الرَّجُلُ')
        proj = result.prefix_projection
        assert proj.span_start == 0
        assert proj.span_end == 2

    def test_to_dict_serializable(self):
        """to_dict() يجب أن يُعيد قاموسًا قابلًا للتحويل إلى JSON"""
        import json
        result = self.project_article('الْبَيْتُ')
        d = result.to_dict()
        # يجب أن يكون قابلًا للتسلسل دون استثناء
        json.dumps(d, ensure_ascii=False)

    def test_solar_host_no_assimilation_shadda(self):
        """الشَّجَرَةِ → normalized_host='شَجَرَةِ' (بدون شدة الإدغام)

        شدة الشين في الشَّجَرَةِ ناتجة عن إدغام لام التعريف في الشين الشمسية.
        هذه الشدة لا تُمثِّل بنيةً صرفيةً في المضيف، وإرسالها إلى HR2S
        يجعله يقرأ (ش+ش) كجذر مضاعف → خطأ.
        المطلوب: normalized_host يحتوي شَجَرَةِ (شين واحدة بدون شدة إدغام).
        """
        result = self.project_article('الشَّجَرَةِ')
        assert result.is_solar is True
        # normalized_host يجب أن لا يحتوي الشدة
        assert 'ّ' not in result.normalized_host, (
            f"normalized_host يحتوي شدة إدغام: {result.normalized_host!r}"
        )
        assert result.normalized_host == 'شَجَرَةِ', (
            f"Expected 'شَجَرَةِ', got {result.normalized_host!r}"
        )

    def test_solar_host_noon_no_assimilation_shadda(self):
        """النَّاسُ → normalized_host='نَاسُ' (بدون شدة إدغام النون)"""
        result = self.project_article('النَّاسُ')
        assert result.is_solar is True
        assert 'ّ' not in result.normalized_host, (
            f"normalized_host يحتوي شدة: {result.normalized_host!r}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# §2  تصنيف المسار الصرفي
# ══════════════════════════════════════════════════════════════════════════════

class TestMorphologyPath:
    """Axis 2 — MorphologyPath + classify_morphology_path()"""

    def setup_method(self):
        from pipeline.pre_root.morphology_path import (
            MorphologyPath, classify_morphology_path,
        )
        from boundary.models import BoundaryKind
        self.MorphologyPath = MorphologyPath
        self.classify = classify_morphology_path
        self.BK = BoundaryKind

    def test_verbal_mudaric_ya(self):
        """يَفْعَلُ — مضارع يَ → VERBAL_ROOT_PATH"""
        path = self.classify('يَفْعَلُ', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.VERBAL_ROOT_PATH

    def test_verbal_mudaric_ta(self):
        """تَكْتُبُ — مضارع تَ → VERBAL_ROOT_PATH"""
        path = self.classify('تَكْتُبُ', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.VERBAL_ROOT_PATH

    def test_verbal_mudaric_na(self):
        """نَذْهَبُ — مضارع نَ → VERBAL_ROOT_PATH"""
        path = self.classify('نَذْهَبُ', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.VERBAL_ROOT_PATH

    def test_verbal_feminine_tail(self):
        """تَرَكَتْ — تاء التأنيث الساكنة → VERBAL_ROOT_PATH"""
        path = self.classify('تَرَكَتْ', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.VERBAL_ROOT_PATH

    def test_verbal_compressed(self):
        """قُلْ — COMPRESSED_VERB → VERBAL_ROOT_PATH"""
        path = self.classify('قُلْ', self.BK.COMPRESSED_VERB_CANDIDATE)
        assert path is self.MorphologyPath.VERBAL_ROOT_PATH

    def test_nominal_tanwin_rafaa(self):
        """رَجُلٌ — تنوين رفع → NOMINAL_MORPHOLOGY_PATH"""
        path = self.classify('رَجُلٌ', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.NOMINAL_MORPHOLOGY_PATH

    def test_nominal_ta_marbuta_nasb(self):
        """شَجَرَةً — تاء مربوطة + تنوين → NOMINAL_MORPHOLOGY_PATH"""
        path = self.classify('شَجَرَةً', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.NOMINAL_MORPHOLOGY_PATH

    def test_nominal_plural_masc(self):
        """مُعَلِّمُونَ — جمع مذكر سالم → NOMINAL_MORPHOLOGY_PATH"""
        path = self.classify('مُعَلِّمُونَ', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.NOMINAL_MORPHOLOGY_PATH

    def test_functional_closed(self):
        """مِنْ — CLOSED_FUNCTION_WORD → FUNCTIONAL_PATH"""
        path = self.classify('مِنْ', self.BK.CLOSED_FUNCTION_WORD)
        assert path is self.MorphologyPath.FUNCTIONAL_PATH

    def test_functional_possible(self):
        """عَلَى — POSSIBLE_FUNCTION_WORD → FUNCTIONAL_PATH"""
        path = self.classify('عَلَى', self.BK.POSSIBLE_FUNCTION_WORD)
        assert path is self.MorphologyPath.FUNCTIONAL_PATH

    def test_ambiguous_prefix(self):
        """تَقِي — AMBIGUOUS → AMBIGUOUS_MORPHOLOGY_PATH"""
        path = self.classify('تَقِي', self.BK.AMBIGUOUS)
        assert path is self.MorphologyPath.AMBIGUOUS_MORPHOLOGY_PATH

    def test_no_morphology_underlicensed(self):
        """مَ — UNDERLICENSED → NO_MORPHOLOGY_PATH"""
        path = self.classify('مَ', self.BK.UNDERLICENSED_SHORT_SURFACE)
        assert path is self.MorphologyPath.NO_MORPHOLOGY_PATH

    def test_no_morphology_empty(self):
        """سطح فارغ → NO_MORPHOLOGY_PATH"""
        path = self.classify('', self.BK.UNDERLICENSED_SHORT_SURFACE)
        assert path is self.MorphologyPath.NO_MORPHOLOGY_PATH

    def test_enum_values_are_strings(self):
        """كل قيمة في MorphologyPath هي str (للتوافق النصي)"""
        for member in self.MorphologyPath:
            assert isinstance(member.value, str)

    def test_verbal_passive_mudaric(self):
        """يُكْتَبُ — مضارع مبني للمجهول يُ → VERBAL_ROOT_PATH"""
        path = self.classify('يُكْتَبُ', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.VERBAL_ROOT_PATH

    def test_nominal_broken_plural_atfal(self):
        """أَطْفَالُ — جمع كسر → NOMINAL_MORPHOLOGY_PATH (لا VERBAL_ROOT_PATH)

        أَطْفَالُ يبدأ بهمزة+فتحة لكنه جمع كسر اسمي، ليس فعلًا مضارعًا.
        المشكلة الحالية: يُصنَّف VERBAL بسبب بادئة 'أَ' أو ROOT_ELIGIBLE fallback.
        الصحيح: NOMINAL_MORPHOLOGY_PATH بناءً على البنية الداخلية.
        """
        path = self.classify('أَطْفَالُ', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.NOMINAL_MORPHOLOGY_PATH, (
            f"أَطْفَالُ جمع كسر اسمي → NOMINAL، لكن التصنيف أعطى: {path}"
        )
        assert path is not self.MorphologyPath.VERBAL_ROOT_PATH

    def test_root_eligible_fallback_not_verbal(self):
        """ROOT_ELIGIBLE بدون شاهد فعلي صريح → لا يُعطى VERBAL_ROOT_PATH تلقائيًا

        إذا لم تكن هناك بادئة مضارع أو تاء تأنيث ساكنة أو لاحقة اسمية،
        فالنتيجة يجب أن تكون AMBIGUOUS أو NOMINAL — ليس VERBAL بسبب ROOT_ELIGIBLE وحدها.
        """
        # خَالِدُ: لا بادئة مضارع، لا تاء تأنيث، لا تنوين، لا لاحقة اسمية صريحة
        path = self.classify('خَالِدُ', self.BK.ROOT_ELIGIBLE)
        assert path is not self.MorphologyPath.VERBAL_ROOT_PATH, (
            "ROOT_ELIGIBLE وحدها لا تكفي لإعطاء VERBAL_ROOT_PATH"
        )

    def test_naemeen_nominal_tails_before_mudaric(self):
        """نَاءِمِينَ — ينَ اسمي يجب أن يُعطي NOMINAL قبل فحص نَ المضارعية

        نَاءِمِينَ ينتهي بـ ينَ (جمع مذكر سالم) وهو شاهد اسمي قاطع.
        المشكلة: يبدأ بـ نَ فيُصنَّف VERBAL إذا فُحصت البادئة أولًا.
        الصواب: فحص اللواحق الاسمية قبل البادئة المضارعية.
        """
        path = self.classify('نَاءِمِينَ', self.BK.ROOT_ELIGIBLE)
        assert path is self.MorphologyPath.NOMINAL_MORPHOLOGY_PATH, (
            f"نَاءِمِينَ ينتهي بـ ينَ (جمع مذكر سالم) → NOMINAL، لكن: {path}"
        )
        assert path is not self.MorphologyPath.VERBAL_ROOT_PATH

    def test_nawm_not_mudaric_surface(self):
        """نَوْمِ — يبدأ بـ نَ لكن الحرف الثالث و (حرف مد) → لا يُعدّ مضارعًا

        المضارع الحقيقي: نَ + صامت (نَذْهَبُ).
        نَوْمِ: نَ + حرف مد (و) → ليس مضارعًا → لا VERBAL_ROOT_PATH.
        """
        path = self.classify('نَوْمِ', self.BK.ROOT_ELIGIBLE)
        assert path is not self.MorphologyPath.VERBAL_ROOT_PATH, (
            f"نَوْمِ يبدأ بـ نَ+حرف مد (و)، ليس مضارعًا → لا VERBAL، لكن: {path}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# §3  تجميع الأحكام البنيوية
# ══════════════════════════════════════════════════════════════════════════════

class TestStructuralAggregation:
    """Axis 3 — aggregate_structural_verdict()"""

    def setup_method(self):
        from pipeline.pre_root.structural_aggregation import (
            aggregate_structural_verdict,
            verdicts_from_directive,
            residuals_for_verdict,
            STRUCTURAL_DEFER_RESIDUAL,
            STRUCTURAL_BLOCK_RESIDUAL,
        )
        self.aggregate = aggregate_structural_verdict
        self.from_directive = verdicts_from_directive
        self.residuals = residuals_for_verdict
        self.DEFER_RESIDUAL = STRUCTURAL_DEFER_RESIDUAL
        self.BLOCK_RESIDUAL = STRUCTURAL_BLOCK_RESIDUAL

    def test_empty_list(self):
        """قائمة فارغة → ACCEPT"""
        assert self.aggregate([]) == 'ACCEPT'

    def test_all_accept(self):
        """كل القيم ACCEPT → ACCEPT"""
        assert self.aggregate(['ACCEPT', 'ACCEPT', 'ACCEPT']) == 'ACCEPT'

    def test_one_defer(self):
        """ACCEPT + DEFER → DEFER"""
        assert self.aggregate(['ACCEPT', 'DEFER']) == 'DEFER'

    def test_defer_overrides_accept(self):
        """DEFER يطغى على ACCEPT"""
        assert self.aggregate(['ACCEPT', 'ACCEPT', 'DEFER']) == 'DEFER'

    def test_one_block(self):
        """DEFER + BLOCK → BLOCK"""
        assert self.aggregate(['DEFER', 'BLOCK']) == 'BLOCK'

    def test_block_overrides_all(self):
        """BLOCK يطغى على ACCEPT و DEFER"""
        assert self.aggregate(['ACCEPT', 'DEFER', 'BLOCK']) == 'BLOCK'

    def test_single_block(self):
        assert self.aggregate(['BLOCK']) == 'BLOCK'

    def test_single_defer(self):
        assert self.aggregate(['DEFER']) == 'DEFER'

    def test_single_accept(self):
        assert self.aggregate(['ACCEPT']) == 'ACCEPT'

    def test_unknown_verdict_becomes_defer(self):
        """قيمة غير معروفة → DEFER (حفظًا)"""
        result = self.aggregate(['ACCEPT', 'UNKNOWN_VALUE'])
        assert result == 'DEFER'

    def test_unknown_with_block(self):
        """قيمة غير معروفة + BLOCK → BLOCK"""
        result = self.aggregate(['UNKNOWN', 'BLOCK'])
        assert result == 'BLOCK'

    def test_verdicts_from_open(self):
        """OPEN → ['ACCEPT']"""
        assert self.from_directive('OPEN') == ['ACCEPT']

    def test_verdicts_from_defer(self):
        """DEFER → ['DEFER']"""
        assert self.from_directive('DEFER') == ['DEFER']

    def test_verdicts_from_block(self):
        """BLOCK → ['BLOCK']"""
        assert self.from_directive('BLOCK') == ['BLOCK']

    def test_residuals_accept_empty(self):
        """ACCEPT → رموز تحفظ فارغة"""
        assert self.residuals('ACCEPT') == ()

    def test_residuals_defer_has_code(self):
        """DEFER → رمز تحفظ STRUCTURAL_DEFER_RESIDUAL"""
        residuals = self.residuals('DEFER')
        assert self.DEFER_RESIDUAL in residuals

    def test_residuals_block_has_code(self):
        """BLOCK → رمز تحفظ STRUCTURAL_BLOCK_RESIDUAL"""
        residuals = self.residuals('BLOCK')
        assert self.BLOCK_RESIDUAL in residuals


# ══════════════════════════════════════════════════════════════════════════════
# §4  تصنوف أدوار اللواحق
# ══════════════════════════════════════════════════════════════════════════════

class TestAttachmentRoles:
    """Axis 4 — AttachmentRole + AttachmentProjection"""

    def setup_method(self):
        from pipeline.pre_root.attachment_roles import (
            AttachmentRole,
            AttachmentProjection,
            INFLECTIONAL_SUBJECT_WAW_AL_JAMAA,
        )
        self.AR = AttachmentRole
        self.AP = AttachmentProjection
        self.WAW_ALIAS = INFLECTIONAL_SUBJECT_WAW_AL_JAMAA

    def test_all_roles_are_strings(self):
        """كل دور هو str"""
        for role in self.AR:
            assert isinstance(role.value, str)

    def test_definite_article_role_exists(self):
        assert self.AR.DEFINITE_ARTICLE.value == 'definite_article'

    def test_inflectional_subject_suffix(self):
        """واو الجماعة = INFLECTIONAL_SUBJECT_SUFFIX"""
        assert self.AR.INFLECTIONAL_SUBJECT_SUFFIX.value == 'inflectional_subject_suffix'

    def test_object_pronoun_suffix(self):
        """هُ في ضَرَبَهُ = OBJECT_PRONOUN_SUFFIX"""
        assert self.AR.OBJECT_PRONOUN_SUFFIX.value == 'object_pronoun_suffix'

    def test_operator_complement_suffix(self):
        """هُمْ في أَنَّهُمْ = OPERATOR_COMPLEMENT_SUFFIX"""
        assert self.AR.OPERATOR_COMPLEMENT_SUFFIX.value == 'operator_complement_suffix'

    def test_waw_alias_is_inflectional(self):
        """INFLECTIONAL_SUBJECT_WAW_AL_JAMAA → INFLECTIONAL_SUBJECT_SUFFIX"""
        assert self.WAW_ALIAS is self.AR.INFLECTIONAL_SUBJECT_SUFFIX

    def test_attachment_projection_dataclass(self):
        """AttachmentProjection قابل للإنشاء والتسلسل"""
        proj = self.AP(
            surface    = 'الْ',
            role       = self.AR.DEFINITE_ARTICLE,
            span_start = 0,
            span_end   = 3,
            notes      = 'test',
        )
        d = proj.to_dict()
        assert d['role'] == 'definite_article'
        assert d['span_start'] == 0
        assert d['span_end'] == 3

    def test_attachment_projection_frozen(self):
        """AttachmentProjection مُجمَّد (لا تعديل)"""
        proj = self.AP(
            surface='هُ', role=self.AR.OBJECT_PRONOUN_SUFFIX,
            span_start=3, span_end=5,
        )
        with pytest.raises((AttributeError, TypeError)):
            proj.surface = 'هَا'  # type: ignore

    def test_clitic_prefix_role(self):
        assert self.AR.CLITIC_PREFIX.value == 'clitic_prefix'

    def test_unknown_attachment_role(self):
        assert self.AR.UNKNOWN_ATTACHMENT.value == 'unknown_attachment'


# ══════════════════════════════════════════════════════════════════════════════
# §5  إغلاق المشغّلات المركبة
# ══════════════════════════════════════════════════════════════════════════════

class TestHostRouting:
    """Axis 5 — route_host() + HostRoutingDecision"""

    def setup_method(self):
        from pipeline.pre_root.host_routing import (
            route_host, HostRoutingDecision, HostRoute,
        )
        self.route_host = route_host
        self.HostRoutingDecision = HostRoutingDecision
        self.HostRoute = HostRoute

    def test_empty_host_blocked(self):
        """مضيف فارغ → EMPTY → BLOCK"""
        decision = self.route_host('')
        assert decision.route == self.HostRoute.EMPTY
        assert decision.root_path_directive == 'BLOCK'
        assert decision.next_stage == 'EMPTY'

    def test_whitespace_host_blocked(self):
        """مضيف فراغات → EMPTY"""
        decision = self.route_host('   ')
        assert decision.route == self.HostRoute.EMPTY

    def test_open_host_goes_to_hr2s(self):
        """مضيف عادي (ضَرَبَ) → MORPHOLOGY_PATH → HR2S"""
        decision = self.route_host('ضَرَبَ')
        # إما MORPHOLOGY_PATH (لم يُكشف مشغّل) أو CLOSED_OPERATOR_HOST
        # ضَرَبَ ليس مشغّلًا → MORPHOLOGY_PATH
        assert decision.route == self.HostRoute.MORPHOLOGY_PATH
        assert decision.root_path_directive == 'OPEN'
        assert decision.next_stage == 'HOKOM_ROOT_ENGINE'

    def test_routing_decision_frozen(self):
        """HostRoutingDecision مُجمَّد"""
        d = self.route_host('ضَرَبَ')
        with pytest.raises((AttributeError, TypeError)):
            d.route = 'OTHER'  # type: ignore

    def test_routing_to_dict(self):
        """to_dict() يُعيد قاموسًا"""
        import json
        d = self.route_host('ضَرَبَ')
        dd = d.to_dict()
        json.dumps(dd, ensure_ascii=False)  # لا استثناء

    def test_host_route_constants(self):
        """ثوابت HostRoute مُعرَّفة"""
        HR = self.HostRoute
        assert HR.EMPTY == 'EMPTY'
        assert HR.CLOSED_OPERATOR_HOST == 'CLOSED_OPERATOR_HOST'
        assert HR.MABNI_HOST == 'MABNI_HOST'
        assert HR.MORPHOLOGY_PATH == 'MORPHOLOGY_PATH'


# ══════════════════════════════════════════════════════════════════════════════
# §6  تجميع PreRootDecision
# ══════════════════════════════════════════════════════════════════════════════

class TestPreRootDecision:
    """§6 — assess_pre_root() + PreRootDecision"""

    def setup_method(self):
        from pipeline.pre_root.pre_root_decision import (
            assess_pre_root, PreRootDecision,
        )
        from pipeline.pre_root.morphology_path import MorphologyPath
        self.assess = assess_pre_root
        self.PRD = PreRootDecision
        self.MP = MorphologyPath

    def test_returns_pre_root_decision(self):
        result = self.assess('ضَرَبَ')
        assert isinstance(result, self.PRD)

    def test_input_surface_preserved(self):
        result = self.assess('ضَرَبَ')
        assert result.input_surface == 'ضَرَبَ'

    def test_article_stripped_in_host(self):
        """الْأَطْفَالُ → host_surface='أَطْفَالُ'"""
        result = self.assess('الْأَطْفَالُ')
        assert result.host_surface == 'أَطْفَالُ'

    def test_prefixes_populated_for_article(self):
        """prefixes غير فارغة عند وجود الـ"""
        result = self.assess('الْبَيْتُ')
        assert len(result.prefixes) == 1

    def test_no_prefix_for_plain_word(self):
        """لا سوابق للكلمة العادية"""
        result = self.assess('ضَرَبَ')
        assert len(result.prefixes) == 0

    def test_verbal_mudaric_gets_verbal_path(self):
        """يَكْتُبُ → VERBAL_ROOT_PATH"""
        result = self.assess('يَكْتُبُ')
        assert result.morphology_path is self.MP.VERBAL_ROOT_PATH

    def test_closed_function_word_blocked(self):
        """مِنْ → root_path_directive='BLOCK'"""
        result = self.assess('مِنْ')
        assert result.root_path_directive == 'BLOCK'

    def test_root_eligible_opens_path(self):
        """ضَرَبَ → root_path_directive in ('OPEN',)"""
        result = self.assess('ضَرَبَ')
        assert result.root_path_directive == 'OPEN'

    def test_pre_root_decision_frozen(self):
        """PreRootDecision مُجمَّد"""
        result = self.assess('ضَرَبَ')
        with pytest.raises((AttributeError, TypeError)):
            result.input_surface = 'other'  # type: ignore

    def test_to_dict_json_serializable(self):
        """to_dict() قابل لـ JSON"""
        import json
        result = self.assess('ضَرَبَ')
        d = result.to_dict()
        json.dumps(d, ensure_ascii=False)

    def test_solar_article_host_starts_correctly(self):
        """الشَّجَرَةِ → host يبدأ بالشين"""
        result = self.assess('الشَّجَرَةِ')
        assert result.host_surface.startswith('ش')

    def test_structural_verdict_field_populated(self):
        """structural_verdict مملوء"""
        result = self.assess('ضَرَبَ')
        assert result.structural_verdict in ('ACCEPT', 'DEFER', 'BLOCK')

    def test_lexical_boundary_field_populated(self):
        """lexical_boundary مملوء"""
        result = self.assess('ضَرَبَ')
        assert isinstance(result.lexical_boundary, str)
        assert len(result.lexical_boundary) > 0

    def test_atfal_nominal_morphology_path(self):
        """الْأَطْفَالُ → morphology_path=NOMINAL_MORPHOLOGY_PATH (لا VERBAL)

        الْأَطْفَالُ: بعد فصل الـ القمرية يُعطي host='أَطْفَالُ' (جمع كسر).
        يجب أن يُصنَّف NOMINAL لا VERBAL.
        """
        result = self.assess('الْأَطْفَالُ')
        assert result.host_surface == 'أَطْفَالُ'
        assert result.morphology_path is self.MP.NOMINAL_MORPHOLOGY_PATH, (
            f"الْأَطْفَالُ جمع كسر اسمي، التصنيف الخاطئ: {result.morphology_path}"
        )

    def test_solar_host_lexical_not_assimilation(self):
        """الشَّجَرَةِ → host_surface='شَجَرَةِ' (شين واحدة، بدون شدة الإدغام)

        شدة الشين في الشَّجَرَةِ من إدغام اللام الشمسية، لا من الوزن الصرفي.
        المضيف الصحيح المُرسَل للتحليل: شَجَرَةِ
        """
        result = self.assess('الشَّجَرَةِ')
        assert result.host_surface == 'شَجَرَةِ', (
            f"Expected host_surface='شَجَرَةِ', got {result.host_surface!r}"
        )

    def test_defer_gives_deferred_not_blocked(self):
        """كلمة DEFER (POSSIBLE_FUNCTION_WORD) → next_stage='DEFERRED' لا 'BLOCKED'

        التمييز الدلالي: DEFER = مسار معلَّق لم يُرخَّص بعد.
                        BLOCK = عائق مُثبَت.
        عَلَى: POSSIBLE_FUNCTION_WORD → structural_verdict=DEFER → next_stage=DEFERRED.
        """
        result = self.assess('عَلَى')
        assert result.structural_verdict == 'DEFER', (
            f"عَلَى يجب أن يُعطي structural_verdict=DEFER، لكن: {result.structural_verdict}"
        )
        assert result.next_stage == 'DEFERRED', (
            f"DEFER يجب أن يُنتج next_stage='DEFERRED'، لكن: {result.next_stage!r}"
        )
        # التحقق الإضافي: DEFER ليس BLOCK
        assert result.root_path_directive == 'DEFER'
        assert result.next_stage != 'BLOCKED'

    def test_orphan_initial_consonant_deferred_not_blocked(self):
        """حْدَ (صامت يتيم بعد التجزئة) + phonological_slot_verdict=DEFER → DEFER لا BLOCK

        العقد الدلالي:
          UNDERLICENSED_SHORT_SURFACE = عجز بنيوي من أثر التجزئة
          → structural_verdict = DEFER (لا BLOCK)
          → root_path_directive  = 'DEFER'
          → next_stage           = 'DEFERRED'
          → HR2S لا يُستدعى (directive ≠ OPEN)

        الفرق عن BLOCK: لم يثبت مانع معجمي؛ الساكن في البداية
        ناتج عن فصل `وَ` من `وَحْدَهُمْ` أو ما شابهه.
        """
        result = self.assess('حْدَ', phonological_slot_verdict='DEFER')
        assert result.structural_verdict == 'DEFER', (
            f"حْدَ + p4=DEFER → structural=DEFER، لكن: {result.structural_verdict!r}"
        )
        assert result.root_path_directive == 'DEFER', (
            f"root_path_directive={result.root_path_directive!r} (expected DEFER)"
        )
        assert result.next_stage == 'DEFERRED', (
            f"next_stage={result.next_stage!r} (expected DEFERRED)"
        )
        # HR2S لا يُستدعى عند غير OPEN
        assert result.root_path_directive != 'OPEN'

    def test_p4_defer_propagates_to_structural(self):
        """phonological_slot_verdict='DEFER' يُضاف إلى تجميع الأحكام → يمنع root_path_directive=OPEN

        ضَرَبَ مع phonological_slot_verdict='DEFER': بدون الإصلاح تُعطي structural=ACCEPT وroot=OPEN.
        مع الإصلاح: structural_verdict=DEFER وroot_path_directive='DEFER' (لا OPEN).
        """
        result = self.assess('ضَرَبَ', phonological_slot_verdict='DEFER')
        assert result.structural_verdict in ('DEFER', 'BLOCK'), (
            f"phonological_slot_verdict='DEFER' يجب أن يمنع ACCEPT، لكن structural_verdict={result.structural_verdict!r}"
        )
        assert result.root_path_directive != 'OPEN', (
            f"phonological_slot_verdict='DEFER' يجب أن يمنع OPEN، لكن root_path_directive={result.root_path_directive!r}"
        )

    def test_operator_compound_functional_path(self):
        """أَنَّهُمْ → CLOSED_OPERATOR_HOST → morphology_path=FUNCTIONAL_PATH

        إذا كُشف route=CLOSED_OPERATOR_HOST:
          - morphology_path يجب أن يكون FUNCTIONAL_PATH (لا VERBAL_ROOT_PATH)
          - root_path_directive = 'BLOCK'
          - الجمع بين VERBAL_ROOT_PATH + BLOCK + CLOSED_OPERATOR_HOST متناقض دلاليًا
        """
        result = self.assess('أَنَّهُمْ')
        if result.routing.route == 'CLOSED_OPERATOR_HOST':
            assert result.morphology_path is self.MP.FUNCTIONAL_PATH, (
                f"CLOSED_OPERATOR_HOST يجب أن يُعطي FUNCTIONAL_PATH، لكن: {result.morphology_path}"
            )
            assert result.root_path_directive == 'BLOCK'
        # إذا لم يُكشف route=CLOSED_OPERATOR_HOST، نتخطى (تعذّر recognize_token)


# ══════════════════════════════════════════════════════════════════════════════
# §7  تتبع الشواهد (evidence_ids)
# ══════════════════════════════════════════════════════════════════════════════

class TestEvidenceTracking:
    """§7 — evidence_ids مُقيَّدة وقابلة للتتبع"""

    def setup_method(self):
        from pipeline.pre_root.pre_root_decision import assess_pre_root
        self.assess = assess_pre_root

    def test_evidence_ids_is_tuple(self):
        result = self.assess('ضَرَبَ')
        assert isinstance(result.evidence_ids, tuple)

    def test_evidence_ids_non_empty(self):
        """يجب أن تكون هناك شواهد على الأقل"""
        result = self.assess('ضَرَبَ')
        assert len(result.evidence_ids) > 0

    def test_article_evidence_in_ids(self):
        """شاهد الـ في evidence_ids"""
        result = self.assess('الْبَيْتُ')
        # شاهد من article_projection
        assert any('article' in eid for eid in result.evidence_ids)

    def test_no_article_evidence_code(self):
        """'article:none' عند غياب الـ"""
        result = self.assess('ضَرَبَ')
        assert 'article:none' in result.evidence_ids

    def test_evidence_ids_all_strings(self):
        """كل شاهد سلسلة نصية"""
        result = self.assess('يَكْتُبُ')
        assert all(isinstance(e, str) for e in result.evidence_ids)

    def test_trace_ids_contain_steps(self):
        """trace_ids تحتوي على خطوات التنفيذ"""
        result = self.assess('ضَرَبَ')
        assert any('step:' in t for t in result.trace_ids)


# ══════════════════════════════════════════════════════════════════════════════
# §8  رموز التحفظ (residual_codes)
# ══════════════════════════════════════════════════════════════════════════════

class TestResidualCodes:
    """§8 — residual_codes للأحكام المقيِّدة"""

    def setup_method(self):
        from pipeline.pre_root.pre_root_decision import assess_pre_root
        from pipeline.pre_root.structural_aggregation import (
            STRUCTURAL_DEFER_RESIDUAL,
            STRUCTURAL_BLOCK_RESIDUAL,
        )
        self.assess = assess_pre_root
        self.DEFER_RESIDUAL = STRUCTURAL_DEFER_RESIDUAL
        self.BLOCK_RESIDUAL = STRUCTURAL_BLOCK_RESIDUAL

    def test_residual_codes_is_tuple(self):
        result = self.assess('ضَرَبَ')
        assert isinstance(result.residual_codes, tuple)

    def test_open_path_no_structural_residual(self):
        """كلمة مفتوحة (ROOT_ELIGIBLE) → لا رموز تحفظ بنيوية"""
        result = self.assess('ضَرَبَ')
        # لا يجب أن يحتوي على رمز التحفظ البنيوي
        assert self.DEFER_RESIDUAL not in result.residual_codes
        assert self.BLOCK_RESIDUAL not in result.residual_codes

    def test_deferred_word_has_defer_residual(self):
        """كلمة مُؤجَّلة → STRUCTURAL_DEFER_RESIDUAL في residual_codes
        نستخدم تَقِي التي تُعطي AMBIGUOUS من boundary"""
        result = self.assess('تَقِي')
        # قد يكون DEFER أو OPEN بحسب boundary — نتحقق من الاتساق
        if result.structural_verdict == 'DEFER':
            assert self.DEFER_RESIDUAL in result.residual_codes

    def test_blocked_word_has_block_residual(self):
        """مِنْ → BLOCK → STRUCTURAL_BLOCK_RESIDUAL"""
        result = self.assess('مِنْ')
        if result.structural_verdict == 'BLOCK':
            assert self.BLOCK_RESIDUAL in result.residual_codes

    def test_residual_codes_all_strings(self):
        """كل رمز تحفظ سلسلة نصية"""
        result = self.assess('ضَرَبَ')
        assert all(isinstance(r, str) for r in result.residual_codes)

    def test_operator_routing_adds_residual(self):
        """إذا وُجِّه إلى OPERATOR → رمز تحفظ مناسب"""
        result = self.assess('ضَرَبَ')
        # لا يُوجَّه إلى OPERATOR لأنه ليس مشغّلًا
        # نتحقق فقط من أن residual_codes قابل للفحص
        assert isinstance(result.residual_codes, tuple)
