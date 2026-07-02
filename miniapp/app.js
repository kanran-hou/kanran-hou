// CopyMind 文案智能分析 —— 全局应用入口
App({
  globalData: {
    analysisResult: null,    // 最近一次分析结果
    trackList: [
      { id: 'xiaohongshu', name: '小红书种草', color: '#FF6B6B' },
      { id: 'ecommerce', name: '电商商品', color: '#4ECDC4' },
      { id: 'local_tourism', name: '本地文旅', color: '#45B7D1' },
      { id: 'short_video', name: '短视频脚本', color: '#96CEB4' },
    ],
  },
  onLaunch() {
    // 小程序启动时可在此处初始化
  },
});