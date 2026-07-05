// CopyMind 文案智能分析 —— 全局应用入口
App({
  globalData: {
    // API 后端地址：本地开发用 localhost，手机测试改成 ngrok 地址或局域网 IP
    API_BASE_URL: 'http://localhost:8000',
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
App({
  globalData: {
    API_BASE_URL: 'http://localhost:8080',
    analysisResult: null,
    trackList: [
      { id: 'xiaohongshu', name: '小红书种草', color: '#FF6B6B' },
      { id: 'ecommerce', name: '电商商品', color: '#4ECDC4' },
      { id: 'local_tourism', name: '本地文旅', color: '#45B7D1' },
      { id: 'short_video', name: '短视频脚本', color: '#96CEB4' },
    ],
  },
  onLaunch() {
  },
});
