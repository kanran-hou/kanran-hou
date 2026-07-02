/* ============================================================
   CopyMind 历史记录页 — 交互逻辑
============================================================ */
Page({

  data: {
    list: [],
    page: 1,
    pageSize: 20,
    hasMore: true,
    isLoading: false,
    totalCount: 0,
    avgScore: 0,
    bestScore: 0
  },

  onLoad() {
    this._loadFromCache();
  },

  onShow() {
    // 每次显示刷新
    this._loadFromCache();
  },

  /* ---- 从缓存加载记录 ---- */
  _loadFromCache() {
    var history = wx.getStorageSync('copymind_history') || [];
    var list = [];
    var totalScore = 0;
    var bestScore = 0;

    for (var i = 0; i < history.length; i++) {
      var item = history[i];
      var score = item.overall_score || 0;
      totalScore += score;
      if (score > bestScore) bestScore = score;

      list.push({
        id: item.id,
        excerpt: (item.text || '').substring(0, 30) + ((item.text || '').length > 30 ? '…' : ''),
        score: score,
        grade: item.overall_grade || 'B',
        trackName: item.track_name || '',
        time: this._formatTime(item.create_time || item.id)
      });
    }

    var avgScore = list.length > 0 ? Math.round(totalScore / list.length) : 0;

    this.setData({
      list: this._paginate(list, 1, this.data.pageSize),
      totalCount: list.length,
      avgScore: avgScore,
      bestScore: bestScore,
      page: 1,
      hasMore: list.length > this.data.pageSize
    });
  },

  /* ---- 分页 ---- */
  _paginate(arr, page, size) {
    return arr.slice(0, page * size);
  },

  onLoadMore() {
    if (!this.data.hasMore || this.data.isLoading) return;
    var history = wx.getStorageSync('copymind_history') || [];
    var nextPage = this.data.page + 1;
    var newList = this._paginate(history, nextPage, this.data.pageSize);

    var list = [];
    for (var i = 0; i < newList.length; i++) {
      var item = newList[i];
      list.push({
        id: item.id,
        excerpt: (item.text || '').substring(0, 30) + ((item.text || '').length > 30 ? '…' : ''),
        score: item.overall_score || 0,
        grade: item.overall_grade || 'B',
        trackName: item.track_name || '',
        time: this._formatTime(item.create_time || item.id)
      });
    }

    this.setData({
      list: list,
      page: nextPage,
      hasMore: newList.length < history.length,
      isLoading: false
    });
  },

  /* ---- 点击列表项 ---- */
  onItemTap(e) {
    var id = e.currentTarget.dataset.id;
    var history = wx.getStorageSync('copymind_history') || [];
    var found = null;
    for (var i = 0; i < history.length; i++) {
      if (history[i].id === id) { found = history[i]; break; }
    }
    if (found) {
      wx.navigateTo({
        url: '/pages/result/result?history_id=' + id
      });
    }
  },

  /* ---- 评分颜色 ---- */
  getScoreColor(score) {
    if (score >= 85) return '#22C55E';
    if (score >= 70) return '#4A7CF7';
    if (score >= 60) return '#F59E0B';
    return '#EF4444';
  },

  /* ---- 时间格式化 ---- */
  _formatTime(timestamp) {
    if (!timestamp) return '';
    var d = new Date(timestamp);
    var month = (d.getMonth() + 1).toString().padStart(2, '0');
    var day = d.getDate().toString().padStart(2, '0');
    var hour = d.getHours().toString().padStart(2, '0');
    var min = d.getMinutes().toString().padStart(2, '0');
    return month + '/' + day + ' ' + hour + ':' + min;
  },

  goBack() { wx.navigateBack(); },
  goAnalyze() { wx.switchTab({ url: '/pages/index/index' }); }
});
