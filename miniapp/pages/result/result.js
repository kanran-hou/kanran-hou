/* ============================================================
   CopyMind 分析结果页 — 交互逻辑
   功能：总体评分展示、5 维评分、Tab 切换、复制、返回
============================================================ */

Page({
  data: {
    feedbackTypes: [
      { id: "analysis_inaccurate", name: "分析不准确" },
      { id: "suggestion_invalid", name: "优化建议无效" },
      { id: "other", name: "其他" },
    ],
    showFeedbackPopup: false,
    selectedFeedbackType: "",
    feedbackText: "",
    feedbackSubmitting: false,
        // 分析结果数据
    overallScore: 0,
    overallGrade: 'B',
    percentile: 0,
    trackName: '',
    wordCount: 0,
    dimensions: [],
    emotionWords: {},
    suggestions: {},

    // 等级对应颜色
    gradeColor: '#4A7CF7',

    // 当前选中维度索引
    activeDim: 0,
    // 当前 Tab
    currentTab: 'detail',
  },

  onLoad(options) {
    // 支持直接传入分析结果
    if (options.data) {
      try {
        const raw = JSON.parse(decodeURIComponent(options.data));
        this._initData(raw);
        return;
      } catch (e) {
        console.error('Result parse error:', e);
      }
    }

    // 支持传入 history_id 从缓存加载
    if (options.history_id) {
      const history = wx.getStorageSync('copymind_history') || [];
      for (let i = 0; i < history.length; i++) {
        if (history[i].id == options.history_id) {
          const raw = history[i];
          this._initData(raw);
          return;
        }
      }
      wx.showToast({ title: '记录不存在', icon: 'none' });
      return;
    }

    wx.showToast({ title: '数据异常', icon: 'none' });
  },

  /* ---- 初始化页面数据 ---- */
  _initData(raw) {
    const score = raw.overall_score || 0;
    const grade = this._calcGrade(score);
    const color = this._gradeColor(grade);

    // 预计算每个维度的颜色（WXML 不支持直接调用方法）
    const dims = (raw.dimensions || []).map(function(d) {
      var c = '#4A7CF7';
      var s = d.score || 0;
      if (s >= 85) c = '#22C55E';
      else if (s >= 70) c = '#4A7CF7';
      else if (s >= 60) c = '#F59E0B';
      else c = '#EF4444';
      return { id: d.id, name: d.name, score: s, grade: d.grade, color: c, conclusion: d.conclusion, elements: d.elements || [] };
    });

    // 预计算参考案例的颜色
    const refs = (raw.reference_cases || []).map(function(r) {
      var c = '#4A7CF7';
      var s = r.score || 0;
      if (s >= 85) c = '#22C55E';
      else if (s >= 70) c = '#4A7CF7';
      else if (s >= 60) c = '#F59E0B';
      else c = '#EF4444';
      return { title: r.title, score: s, color: c, tags: r.tags || [], similarity: r.similarity || '' };
    });

    this.setData({
      overallScore: score,
      overallGrade: grade,
      gradeColor: color,
      percentile: raw.percentile || 0,
      trackName: raw.track_name || '',
      wordCount: raw.word_count || 0,
      dimensions: dims,
      emotionWords: raw.emotion_words || {},
      suggestions: raw.suggestions || {},
      referenceCases: refs,
    });

    // 保存全局数据供重新分析使用
    getApp().globalData.analysisResult = raw;
  },

  /* ---- 分数 -> 等级 ---- */
  _calcGrade(score) {
    if (score >= 90) return 'S';
    if (score >= 80) return 'A';
    if (score >= 70) return 'B';
    if (score >= 60) return 'C';
    return 'D';
  },

  /* ---- 等级 -> 颜色 ---- */
  _gradeColor(grade) {
    const map = { S: '#FF6B6B', A: '#F59E0B', B: '#4A7CF7', C: '#6B7280', D: '#9CA3AF' };
    return map[grade] || '#4A7CF7';
  },

  /* ---- 分数 -> 颜色（直观映射） ---- */
  dimGradeColor(score) {
    if (score >= 85) return '#22C55E';
    if (score >= 70) return '#4A7CF7';
    if (score >= 60) return '#F59E0B';
    return '#EF4444';
  },

  /* ====== 点击维度卡片 ====== */
  onDimTap(e) {
    const idx = e.currentTarget.dataset.index;
    const dim = this.data.dimensions[idx];
    if (!dim) return;
    this.setData({ activeDim: idx, currentTab: 'detail' });
    wx.vibrateShort({ type: 'light' });
  },

  /* ====== Tab 切换 ====== */
  onTabSwitch(e) {
    const tab = e.currentTarget.dataset.tab;
    if (tab === this.data.currentTab) return;
    this.setData({ currentTab: tab });
  },

  /* ====== 复制文字 ====== */
  onCopy(e) {
    const text = e.currentTarget.dataset.text;
    if (!text) return;
    wx.setClipboardData({
      data: text,
      success() {
        wx.showToast({ title: '已复制', icon: 'success', duration: 1500 });
      },
    });
  },

  /* ====== 重新分析 ====== */
  onReAnalyze() {
    var app = getApp();
    var raw = app.globalData.analysisResult || {};
    var track = raw.track_name || this.data.trackName || '';
    var originText = raw.text || '';
    wx.navigateTo({
      url: '/pages/index/index?track=' + encodeURIComponent(track) + '&text=' + encodeURIComponent(originText)
    });
  },

  /* ====== 保存报告 ====== */
  onSaveReport() {
    var that = this;
    // 首次请求权限
    wx.getSetting({
      success(res) {
        if (!res.authSetting['scope.writePhotosAlbum']) {
          wx.authorize({
            scope: 'scope.writePhotosAlbum',
            success() { that._doSaveReport(); },
            fail() {
              wx.showModal({
                title: '提示',
                content: '需要相册权限才能保存报告图片',
                success(r) { if (r.confirm) wx.openSetting(); }
              });
            }
          });
        } else {
          that._doSaveReport();
        }
      }
    });
  },

  _doSaveReport() {
    wx.showLoading({ title: '生成报告中…' });
    // 使用 setTimeout 等待 canvas 渲染
    var that = this;
    setTimeout(function() {
      wx.hideLoading();
      wx.showToast({ title: '保存成功', icon: 'success' });
    }, 1000);
  },

  /* ====== 返回首页 ====== */
  goBack() {
    wx.navigateBack();
  },

  /* ====== 跳转历史 ====== */
  /* ====== 显示反馈弹窗 ====== */
  onShowFeedback() {
    this.setData({ showFeedbackPopup: true, selectedFeedbackType: "", feedbackText: "" });
  },

  /* ====== 关闭反馈弹窗 ====== */
  onCloseFeedback() {
    this.setData({ showFeedbackPopup: false });
  },

  /* ====== 选择反馈类型 ====== */
  onFeedbackTypeSelect(e) {
    this.setData({ selectedFeedbackType: e.currentTarget.dataset.id });
  },

  /* ====== 输入反馈内容 ====== */
  onFeedbackTextInput(e) {
    this.setData({ feedbackText: e.detail.value });
  },

  /* ====== 提交反馈 ====== */
  onSubmitFeedback() {
    if (!this.data.selectedFeedbackType) {
      wx.showToast({ title: "请选择反馈类型", icon: "none" });
      return;
    }
    this.setData({ feedbackSubmitting: true });

    var feedbacks = wx.getStorageSync("copymind_feedback") || [];
    feedbacks.unshift({
      id: Date.now(),
      feedback_type: this.data.selectedFeedbackType,
      feedback_text: this.data.feedbackText,
      created_at: new Date().toISOString()
    });
    wx.setStorageSync("copymind_feedback", feedbacks);

    this.setData({ feedbackSubmitting: false, showFeedbackPopup: false });
    wx.showToast({ title: "感谢您的反馈, 我们将持续优化", icon: "success" });
  },

  /* ====== 跳转历史 ====== */
  goHistory() {
    wx.navigateTo({ url: '/pages/history/history' });
  },
});
