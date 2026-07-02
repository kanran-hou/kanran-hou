/* ============================================================
  CopyMind 文案录入首页 —— 交互逻辑
  功能：赛道选择、文本输入、图片上传、分析触发
============================================================ */

Page({

  /* ---- 页面初始数据 ---- */
  data: {
    // 赛道列表（从全局数据读取）
    trackList: [],
    // 当前选中的赛道 ID（空 = 未选择）
    selectedTrack: '',
    // 用户输入的文案文本
    inputText: '',
    // 已上传的图片临时路径列表
    imageList: [],
    // 是否正在分析（控制按钮加载态）
    isAnalyzing: false,
    // 是否显示加载动画遮罩
    showLoading: false,
    // 按钮是否可点击（由 JS 计算，WXML 只读 data）
    canAnalyze: false,
  },

  /* ---- 生命周期：页面加载 ---- */
  onLoad() {
    var app = getApp();
    this.setData({
      trackList: app.globalData.trackList || [],
    });

    var cached = wx.getStorageSync('copymind_input_cache');
    if (cached) {
      this.setData({
        selectedTrack: cached.track || '',
        inputText: cached.text || '',
      });
    }
    this._updateCanAnalyze();
    this._saveCache();
  },

  /* ---- 更新按钮状态 ---- */
  _updateCanAnalyze() {
    var can = this.data.selectedTrack !== '' && this.data.inputText.trim().length > 0 && !this.data.isAnalyzing;
    this.setData({ canAnalyze: can });
  },

  /* ====== 赛道选择 ====== */
  onTrackSelect(e) {
    this.setData({ selectedTrack: e.currentTarget.dataset.id });
    this._updateCanAnalyze();
    this._saveCache();
  },

  /* ====== 文本输入 ====== */
  onTextInput(e) {
    this.setData({ inputText: e.detail.value });
    this._updateCanAnalyze();
    this._saveCache();
  },

  /* ====== 图片上传 ====== */
  onUploadImage() {
    var that = this;
    wx.chooseImage({
      count: 6,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success(res) {
        var newList = that.data.imageList.concat(res.tempFilePaths);
        var finalList = newList.slice(0, 6);
        that.setData({ imageList: finalList });
      },
    });
  },

  /* ====== 删除单张图片 ====== */
  onRemoveImage(e) {
    var list = this.data.imageList.slice();
    list.splice(e.currentTarget.dataset.index, 1);
    this.setData({ imageList: list });
  },

  /* ====== AI 一键分析 ====== */
  onAnalyze() {
    if (!this.data.selectedTrack) {
      wx.showToast({ title: '请选择赛道', icon: 'none' });
      return;
    }
    var text = this.data.inputText.trim();
    if (!text) {
      wx.showToast({ title: '请输入文案内容', icon: 'none' });
      return;
    }
    if (text.length > 5000) {
      wx.showToast({ title: '文案超过 5000 字上限', icon: 'none' });
      return;
    }

    this.setData({ isAnalyzing: true, showLoading: true });
    this._updateCanAnalyze();

    var self = this;
    // 调用后端 API 进行 AI 分析
    wx.request({
      url: 'http://localhost:8000/api/v1/analyze',
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: {
        original_text: text,
        track_type: self.data.selectedTrack,
        user_openid: 'wx_user_' + Date.now()
      },
      success(res) {
        self.setData({ isAnalyzing: false, showLoading: false });
        self._updateCanAnalyze();
        if (res.data.code !== 0) {
          wx.showToast({ title: res.data.message || '分析失败', icon: 'none' });
          return;
        }
        var apiData = res.data.data;
        var analysisRaw = apiData.analysis_raw || {};
        var trackNames = {
          xiaohongshu: '小红书种草',
          ecommerce: '电商商品',
          local_tourism: '本地文旅',
          short_video: '短视频脚本'
        };
        var trackName = trackNames[self.data.selectedTrack] || '';

        var dimList = [];
        var dimMap = {
          title: { id: 'title', name: '标题吸引力', key: 'title_analysis' },
          emotion: { id: 'emotion', name: '情绪共鸣', key: 'emotion_analysis' },
          structure: { id: 'structure', name: '结构逻辑', key: 'structure_analysis' },
          audience: { id: 'audience', name: '人群匹配', key: 'audience_analysis' }
        };
        for (var k in dimMap) {
          var info = dimMap[k];
          var src = analysisRaw[info.key] || {};
          var s = src.score || 0;
          dimList.push({
            id: info.id, name: info.name, score: s,
            grade: s >= 80 ? 'A' : s >= 60 ? 'B' : 'C',
            conclusion: src.comment || '',
            elements: []
          });
        }

        var emotionSrc = analysisRaw.emotion_analysis || {};
        var emotionWords = {
          positive: emotionSrc.empathy_words || [],
          anxious: emotionSrc.anxiety_words || [],
          empathetic: []
        };

        var mySuggestions = { titles: [], paragraphs: [], emotions: [] };
        var sugList = analysisRaw.suggestions || [];
        for (var i = 0; i < sugList.length; i++) {
          var s = sugList[i];
          if (s.type === 'title') {
            mySuggestions.titles.push({ rewrite: s.content });
          } else if (s.type === 'structure') {
            mySuggestions.paragraphs.push({ pos: '段落', suggestion: s.content, detail: '' });
          } else if (s.type === 'emotion') {
            mySuggestions.emotions.push({ word: '建议词', reason: s.content });
          } else {
            mySuggestions.titles.push({ rewrite: s.content });
          }
        }

        var overallScore = apiData.overall_score || (analysisRaw.overall_scoring ? analysisRaw.overall_scoring.overall_score : 0) || 0;
        var overallGrade = apiData.overall_grade || (analysisRaw.overall_scoring ? analysisRaw.overall_scoring.overall_grade : 'B') || 'B';

        var resultData = {
          id: apiData.id,
          track_type: self.data.selectedTrack,
          track_name: trackName,
          word_count: apiData.word_count || text.length,
          overall_score: overallScore,
          overall_grade: overallGrade,
          percentile: 0,
          dimensions: dimList,
          emotion_words: emotionWords,
          suggestions: mySuggestions,
          reference_cases: []
        };

        self._saveHistory(self, text, trackName, resultData);
        wx.navigateTo({
          url: '/pages/result/result?data=' + encodeURIComponent(JSON.stringify(resultData)),
        });
      },
      fail(err) {
        self.setData({ isAnalyzing: false, showLoading: false });
        self._updateCanAnalyze();
        wx.showToast({ title: '网络请求失败，请检查后端服务是否启动', icon: 'none' });
        console.error('Request failed:', err);
      }
    });
      self.setData({ isAnalyzing: false, showLoading: false });
      self._updateCanAnalyze();

      var trackNames = {
        xiaohongshu: '小红书种草',
        ecommerce: '电商商品',
        local_tourism: '本地文旅',
        short_video: '短视频脚本'
      };

      var trackName = trackNames[self.data.selectedTrack] || '';



  },

  /* ====== 保存历史记录 ====== */
  _saveHistory(self, text, trackName, mockData) {
    var record = {
      id: mockData.id,
      text: text,
      track_type: self.data.selectedTrack,
      track_name: trackName,
      overall_score: mockData.overall_score,
      overall_grade: mockData.overall_grade,
      percentile: mockData.percentile,
      create_time: Date.now()
    };

    // 本地缓存
    var history = wx.getStorageSync('copymind_history') || [];
    history.unshift(record);
    if (history.length > 50) history = history.slice(0, 50);
    wx.setStorageSync('copymind_history', history);
  },

  /* ====== 缓存中间状态 ====== */
  _saveCache() {
    wx.setStorage({
      key: 'copymind_input_cache',
      data: {
        track: this.data.selectedTrack,
        text: this.data.inputText,
      },
    });
  },
});