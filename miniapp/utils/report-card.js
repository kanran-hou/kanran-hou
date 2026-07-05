/* ============================================================
   CopyMind 报告图片绘制工具
   使用 canvas 绘制分析报告，支持保存到相册
============================================================ */

/**
 * 绘制报告卡片
 * @param {string} canvasId - canvas 组件 ID
 * @param {Object} data - 分析结果数据
 * @param {function} callback - 绘制完成回调 (tempFilePath)
 */
function drawReportCard(canvasId, data, callback) {
  var ctx = wx.createCanvasContext(canvasId);
  var W = 560;   // 画布宽度
  var H = 860;   // 画布高度
  var X0 = 30;   // 左边距
  var Y0 = 40;   // 起始Y
  var colW = W - X0 * 2;
  var y = Y0;

  // 背景
  ctx.setFillStyle('#ffffff');
  ctx.fillRect(0, 0, W, H);

  // ---- Header ----
  ctx.setFillStyle('#4A7CF7');
  ctx.fillRect(0, 0, W, 120);
  ctx.setFillStyle('#ffffff');
  ctx.setFontSize(28);
  ctx.fillText('CopyMind AI 文案分析报告', 30, 55);
  ctx.setFontSize(20);
  ctx.fillText('AI Copywriting Analysis Report', 30, 88);
  y = 140;

  // ---- 综合评分 ----
  ctx.setFillStyle('#1A1A2E');
  ctx.setFontSize(24);
  ctx.fillText('综合评分', X0, y);
  y += 35;

  var score = data.overall_score || 0;
  var grade = data.overall_grade || 'B';
  var gradeColor = '#4A7CF7';
  if (score >= 90) gradeColor = '#22C55E';
  else if (score >= 80) gradeColor = '#4A7CF7';
  else if (score >= 70) gradeColor = '#F59E0B';
  else gradeColor = '#EF4444';

  // 圆形分数
  var cx = 120, cy = y + 50, r = 44;
  ctx.setFillStyle('#F0F0F0');
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, 2 * Math.PI);
  ctx.fill();

  ctx.setFillStyle(gradeColor);
  ctx.setFontSize(44);
  ctx.setFontWeight('bold');
  ctx.setTextAlign('center');
  ctx.fillText(score.toString(), cx, cy + 14);
  ctx.setTextAlign('left');
  ctx.setFontSize(18);
  ctx.fillText(grade + '级', cx - 10, cy + 38);

  // 右侧信息
  ctx.setFillStyle('#1A1A2E');
  ctx.setFontSize(26);
  ctx.fillText((data.track_name || '') + ' · ' + (data.word_count || 0) + '字', 190, y + 25);
  ctx.setFillStyle('#6B7280');
  ctx.setFontSize(22);
  ctx.fillText('超过 ' + (data.percentile || 0) + '% 同类文案', 190, y + 55);

  y += 120;

  // ---- 5 维度评分 ----
  ctx.setFillStyle('#1A1A2E');
  ctx.setFontSize(24);
  ctx.fillText('五维评分', X0, y);
  y += 35;

  var dims = data.dimensions || [];
  var barW = Math.floor((colW - 60) / 5);
  for (var i = 0; i < Math.min(dims.length, 5); i++) {
    var dim = dims[i];
    var bx = X0 + i * (barW + 12);
    var ds = dim.score || 0;
    var dc = '#4A7CF7';
    if (ds >= 85) dc = '#22C55E';
    else if (ds >= 70) dc = '#4A7CF7';
    else if (ds >= 60) dc = '#F59E0B';
    else dc = '#EF4444';

    var barH = Math.max(30, ds * 1.2);
    var barTop = y + 60 - barH;

    // 分数
    ctx.setFillStyle(dc);
    ctx.setFontSize(28);
    ctx.setFontWeight('bold');
    ctx.setTextAlign('center');
    ctx.fillText(ds.toString(), bx + barW / 2, barTop - 8);

    // 柱状图
    ctx.setFillStyle('#F0F0F0');
    ctx.fillRect(bx, y + 60 - 80, barW, 80);
    ctx.setFillStyle(dc);
    ctx.fillRect(bx, barTop, barW, barH);

    // 名称
    ctx.setFillStyle('#6B7280');
    ctx.setFontSize(18);
    ctx.fillText(dim.name || '', bx + barW / 2, y + 78);
    ctx.setTextAlign('left');
  }

  y += 105;

  // ---- 优化建议摘要 ----
  ctx.setFillStyle('#1A1A2E');
  ctx.setFontSize(24);
  ctx.fillText('核心优化建议', X0, y);
  y += 35;

  var suggestList = [];
  var sug = data.suggestions || {};
  if (sug.titles && sug.titles.length > 0) suggestList.push('标题优化: ' + sug.titles[0].rewrite);
  if (sug.emotions && sug.emotions.length > 0) suggestList.push('情绪词: +' + sug.emotions[0].word + ' — ' + sug.emotions[0].reason);
  if (sug.paragraphs && sug.paragraphs.length > 0) suggestList.push('段落: ' + sug.paragraphs[0].suggestion);

  ctx.setFillStyle('#6B7280');
  ctx.setFontSize(22);
  for (var si = 0; si < suggestList.length; si++) {
    // 文本换行
    var line = suggestList[si];
    var maxW = colW;
    while (line.length > 0) {
      var chars = line.substring(0, 20);
      var out = line;
      if (ctx.measureText) {
        // 微信小程序不支持 measureText 直接取宽度，用字符数估算
        out = line.substring(0, Math.min(line.length, 22));
      }
      ctx.fillText(out.substring(0, 22), X0, y);
      line = line.substring(out.substring(0, 22).length);
      y += 30;
    }
    y += 5;
  }

  // ---- 底部水印 ----
  y = Math.max(y + 30, H - 60);
  ctx.setFillStyle('#C0C4CC');
  ctx.setFontSize(18);
  ctx.setTextAlign('center');
  var now = new Date();
  var dateStr = now.getFullYear() + '/' + (now.getMonth()+1).toString().padStart(2,'0') + '/' + now.getDate().toString().padStart(2,'0');
  ctx.fillText('由 CopyMind AI 生成 · ' + dateStr, W / 2, y);
  ctx.setTextAlign('left');

  ctx.draw(false, function() {
    wx.canvasToTempFilePath({
      canvasId: canvasId,
      success: function(res) {
        if (callback) callback(res.tempFilePath);
      },
      fail: function() {
        if (callback) callback(null);
      }
    });
  });
}

/**
 * 保存图片到相册
 * @param {string} tempFilePath - 临时文件路径
 * @param {function} callback - 保存结果回调
 */
function saveReportImage(tempFilePath, callback) {
  wx.saveImageToPhotosAlbum({
    filePath: tempFilePath,
    success: function() {
      wx.showToast({ title: '已保存到相册', icon: 'success' });
      if (callback) callback(true);
    },
    fail: function(err) {
      if (err.errMsg.indexOf('auth deny') !== -1 || err.errMsg.indexOf('fail') !== -1) {
        wx.showModal({
          title: '提示',
          content: '需要相册权限才能保存报告图片',
          success: function (res) {
            if (res.confirm) {
              wx.openSetting();
            }
          }
        });
      }
      if (callback) callback(false);
    }
  });
}

module.exports = {
  drawReportCard: drawReportCard,
  saveReportImage: saveReportImage
};
