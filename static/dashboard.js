/* GMP 数据管理仪表盘 — 前端交互 */

document.addEventListener('DOMContentLoaded', function() {
  updateClock();
  showSection('overview');
});

function updateClock() {
  var el = document.getElementById('headerTime');
  if (el) {
    var now = new Date();
    el.textContent = now.toLocaleString('zh-CN');
    setTimeout(updateClock, 60000);
  }
}

function showSection(section) {
  document.querySelectorAll('.module-item').forEach(function(b) { b.classList.remove('active'); });
  document.querySelectorAll('.module-item').forEach(function(b) {
    if (b.textContent.includes(section === 'overview' ? '总览' :
        section === 'zones' ? '仓库' :
        section === 'batches' ? '物料' :
        section === 'alarms' ? '报警' :
        section === 'validations' ? '验证' : '近效期')) {
      b.classList.add('active');
    }
  });

  var content = document.getElementById('dashboardContent');
  content.innerHTML = '<div class="loading">加载中...</div>';

  switch(section) {
    case 'overview': loadOverview(); break;
    case 'zones': loadZones(); break;
    case 'batches': loadBatches(); break;
    case 'alarms': loadAlarms(); break;
    case 'validations': loadValidations(); break;
    case 'expiry': loadNearExpiry(); break;
  }
}

// ============ 总览 ============
function loadOverview() {
  Promise.all([
    fetch('/api/dashboard/stats').then(function(r) { return r.json(); }),
    fetch('/api/dashboard/zones').then(function(r) { return r.json(); })
  ]).then(function(results) {
    var stats = results[0];
    var zonesData = results[1];
    var html = '<div class="dash-header"><h2>📊 系统总览</h2></div>';

    // 统计卡片
    html += '<div class="stats-row">';
    html += '<div class="stat-card"><div class="label">物料批次总量</div><div class="value blue">' + stats.total_batches + '</div></div>';
    html += '<div class="stat-card"><div class="label">合格批次</div><div class="value green">' + stats.approved_batches + '</div></div>';
    html += '<div class="stat-card"><div class="label">不合格批次</div><div class="value red">' + stats.rejected_batches + '</div></div>';
    html += '<div class="stat-card"><div class="label">未关闭偏差</div><div class="value yellow">' + stats.open_nc_count + '</div></div>';
    html += '<div class="stat-card"><div class="label">近效期(90天)</div><div class="value yellow">' + stats.near_expiry_90d + '</div></div>';
    html += '<div class="stat-card"><div class="label">24h报警数</div><div class="value ' + (stats.recent_alarms_24h > 0 ? 'red' : 'green') + '">' + stats.recent_alarms_24h + '</div></div>';
    html += '</div>';

    // 各区当前温度
    html += '<div class="section-title">🏭 仓库实时状态</div>';
    html += '<div class="zone-grid">';
    zonesData.zones.forEach(function(z) {
      var colorClass = z.color_mark === '绿色' ? 'green' : z.color_mark === '黄色' ? 'yellow' : 'red';
      html += '<div class="zone-card ' + colorClass + '">';
      html += '<div class="name">' + z.zone_name + '</div>';
      html += '<div class="type">色标：' + z.color_mark + ' | 容量：' + z.capacity + ' 单位</div>';
      html += '<div class="temps">';
      if (z.current_temp) html += '<span class="temp">🌡 ' + z.current_temp + '℃</span>';
      if (z.current_humidity) html += '<span class="humi">💧 ' + z.current_humidity + '%RH</span>';
      html += '<span>📦 ' + (z.batch_count || 0) + ' 批</span>';
      html += '</div>';
      html += '<div class="desc">' + (z.description || '') + '</div>';
      html += '</div>';
    });
    html += '</div>';

    // 最近报警
    fetch('/api/dashboard/alarms').then(function(r) { return r.json(); }).then(function(alarmData) {
      if (alarmData.alarms.length > 0) {
        html += '<div class="section-title" style="margin-top:24px">🔔 最近报警</div>';
        html += '<div class="table-wrap"><table><tr><th>时间</th><th>区域</th><th>温度</th><th>湿度</th></tr>';
        alarmData.alarms.slice(0, 5).forEach(function(a) {
          html += '<tr><td>' + a.recorded_at + '</td><td>' + a.zone_name + '</td><td style="color:var(--red)">' + a.temperature + '℃</td><td>' + (a.humidity || '-') + '</td></tr>';
        });
        html += '</table></div>';
      }
      document.getElementById('dashboardContent').innerHTML = html;
    });
  });
}

// ============ 仓库区域 ============
function loadZones() {
  fetch('/api/dashboard/zones').then(function(r) { return r.json(); }).then(function(data) {
    var html = '<div class="dash-header"><h2>🏭 仓库区域管理</h2></div>';
    html += '<div class="zone-grid">';
    data.zones.forEach(function(z) {
      var colorClass = z.color_mark === '绿色' ? 'green' : z.color_mark === '黄色' ? 'yellow' : 'red';
      html += '<div class="zone-card ' + colorClass + '">';
      html += '<div class="name">' + z.zone_name + '</div>';
      html += '<div class="type">色标：' + z.color_mark + ' | 容量：' + z.capacity + ' 单位</div>';
      html += '<div class="temps">';
      if (z.current_temp) html += '<span class="temp">🌡 ' + z.current_temp + '℃</span>';
      if (z.current_humidity) html += '<span class="humi">💧 ' + z.current_humidity + '%RH</span>';
      html += '<span>📦 ' + (z.batch_count || 0) + ' 批</span>';
      html += '</div>';
      html += '<div class="desc">' + (z.description || '') + '</div>';
      html += '<div style="font-size:11px;color:var(--text3);margin-top:6px">温控范围：';
      if (z.temperature_min !== null) html += z.temperature_min + '~' + z.temperature_max + '℃';
      if (z.humidity_min !== null) html += ' | ' + z.humidity_min + '~' + z.humidity_max + '%RH';
      html += '</div></div>';
    });
    html += '</div>';
    document.getElementById('dashboardContent').innerHTML = html;
  });
}

// ============ 物料批次 ============
function loadBatches() {
  fetch('/api/dashboard/batches').then(function(r) { return r.json(); }).then(function(data) {
    var html = '<div class="dash-header"><h2>📦 物料批次管理</h2></div>';

    // 状态筛选
    html += '<div class="tab-bar">';
    html += '<button class="tab-btn active" onclick="loadBatchesFilter(\'all\',this)">全部</button>';
    html += '<button class="tab-btn" onclick="loadBatchesFilter(\'approved\',this)">合格</button>';
    html += '<button class="tab-btn" onclick="loadBatchesFilter(\'rejected\',this)">不合格</button>';
    html += '<button class="tab-btn" onclick="loadBatchesFilter(\'quarantine\',this)">待验</button>';
    html += '</div>';

    if (data.batches.length === 0) {
      html += '<div class="no-results">暂无数据</div>';
      document.getElementById('dashboardContent').innerHTML = html;
      return;
    }

    html += '<div class="table-wrap"><table>';
    html += '<tr><th>批号</th><th>品名</th><th>供应商</th><th>数量</th><th>生产日期</th><th>有效期至</th><th>状态</th><th>存放区域</th></tr>';
    data.batches.forEach(function(b) {
      var statusClass = 'status-' + b.status;
      var statusMap = {approved:'✅ 合格', rejected:'❌ 不合格', quarantine:'⏳ 待验', pending:'📋 待处理'};
      html += '<tr><td><strong>' + b.batch_no + '</strong></td><td>' + b.material_name + '</td><td>' + b.supplier + '</td><td>' + b.quantity + b.unit + '</td><td>' + b.manufacture_date + '</td><td>' + b.expiry_date + '</td><td class="' + statusClass + '">' + (statusMap[b.status] || b.status) + '</td><td>' + (b.zone_name || '-') + '</td></tr>';
    });
    html += '</table></div>';
    document.getElementById('dashboardContent').innerHTML = html;
  });
}

function loadBatchesFilter(status, btn) {
  document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
  btn.classList.add('active');

  var url = status === 'all' ? '/api/dashboard/batches' : '/api/dashboard/batches?status=' + status;
  fetch(url).then(function(r) { return r.json(); }).then(function(data) {
    var html = '<div class="dash-header"><h2>📦 物料批次管理</h2></div>';
    html += '<div class="tab-bar">';
    html += '<button class="tab-btn" onclick="loadBatchesFilter(\'all\',this)">全部</button>';
    html += '<button class="tab-btn" onclick="loadBatchesFilter(\'approved\',this)">合格</button>';
    html += '<button class="tab-btn" onclick="loadBatchesFilter(\'rejected\',this)">不合格</button>';
    html += '<button class="tab-btn" onclick="loadBatchesFilter(\'quarantine\',this)">待验</button>';
    html += '</div>';

    if (data.batches.length === 0) {
      html += '<div class="no-results">暂无数据</div>';
      document.getElementById('dashboardContent').innerHTML = html;
      return;
    }
    html += '<div class="table-wrap"><table>';
    html += '<tr><th>批号</th><th>品名</th><th>供应商</th><th>数量</th><th>生产日期</th><th>有效期至</th><th>状态</th><th>存放区域</th></tr>';
    data.batches.forEach(function(b) {
      var statusClass = 'status-' + b.status;
      var statusMap = {approved:'✅ 合格', rejected:'❌ 不合格', quarantine:'⏳ 待验', pending:'📋 待处理'};
      html += '<tr><td><strong>' + b.batch_no + '</strong></td><td>' + b.material_name + '</td><td>' + b.supplier + '</td><td>' + b.quantity + b.unit + '</td><td>' + b.manufacture_date + '</td><td>' + b.expiry_date + '</td><td class="' + statusClass + '">' + (statusMap[b.status] || b.status) + '</td><td>' + (b.zone_name || '-') + '</td></tr>';
    });
    html += '</table></div>';
    document.getElementById('dashboardContent').innerHTML = html;
  });
}

// ============ 报警记录 ============
function loadAlarms() {
  fetch('/api/dashboard/alarms').then(function(r) { return r.json(); }).then(function(data) {
    var html = '<div class="dash-header"><h2>🔔 温湿度报警记录</h2></div>';
    if (data.alarms.length === 0) {
      html += '<div class="stat-card" style="text-align:center;padding:40px"><div style="font-size:48px;margin-bottom:12px">✅</div><div style="color:var(--green)">暂无报警记录</div></div>';
      document.getElementById('dashboardContent').innerHTML = html;
      return;
    }
    html += '<div class="table-wrap"><table>';
    html += '<tr><th>时间</th><th>区域</th><th>温度</th><th>湿度</th><th>设备</th></tr>';
    data.alarms.forEach(function(a) {
      html += '<tr><td>' + a.recorded_at + '</td><td style="color:var(--red)">' + a.zone_name + '</td><td style="color:var(--red);font-weight:600">' + a.temperature + '℃</td><td>' + (a.humidity || '-') + '%RH</td><td>' + a.device_id + '</td></tr>';
    });
    html += '</table></div>';
    document.getElementById('dashboardContent').innerHTML = html;
  });
}

// ============ 验证记录 ============
function loadValidations() {
  fetch('/api/dashboard/zones').then(function(r) { return r.json(); }).then(function(data) {
    var html = '<div class="dash-header"><h2>✅ 验证记录概览</h2></div>';
    html += '<div class="stats-row">';
    html += '<div class="stat-card"><div class="label">仓库区域数</div><div class="value blue">' + data.zones.length + '</div></div>';
    html += '<div class="stat-card"><div class="label">冷库/冷冻/冷藏</div><div class="value blue">' + data.zones.filter(function(z) { return z.zone_type === 'cold_storage' || z.zone_type === 'freezer'; }).length + '</div></div>';
    html += '<div class="stat-card"><div class="label">常温库</div><div class="value green">' + data.zones.filter(function(z) { return z.zone_type === 'storage'; }).length + '</div></div>';
    html += '</div>';
    html += '<div class="section-title">验证管理流程</div>';
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px">';
    var items = [
      {icon:'📋',title:'冷库空载验证',desc:'初次使用前及改造后，≥48h数据采集'},
      {icon:'📦',title:'冷库满载验证',desc:'年度定期，≥70%装载，≥48h'},
      {icon:'🚪',title:'开门测试',desc:'满载状态下3次，记录恢复时长'},
      {icon:'🔌',title:'断电测试',desc:'满载状态下3次，确定保温时限'},
      {icon:'🚛',title:'冷藏车验证',desc:'≥8项，含开门/断电/极端环境'},
      {icon:'📦',title:'保温箱验证',desc:'≥6项，须放模拟物品'},
      {icon:'🌡',title:'温湿度监测验证',desc:'每年至少1次，含断电/防篡改测试'},
      {icon:'📅',title:'年度验证计划',desc:'最热月+最冷月各一次满载验证'},
    ];
    items.forEach(function(item) {
      html += '<div class="zone-card green">';
      html += '<div style="font-size:24px;margin-bottom:8px">' + item.icon + '</div>';
      html += '<div style="font-size:14px;font-weight:600;margin-bottom:4px">' + item.title + '</div>';
      html += '<div style="font-size:12px;color:var(--text3)">' + item.desc + '</div>';
      html += '</div>';
    });
    html += '</div>';
    document.getElementById('dashboardContent').innerHTML = html;
  });
}

// ============ 近效期 ============
function loadNearExpiry() {
  fetch('/api/dashboard/near-expiry').then(function(r) { return r.json(); }).then(function(data) {
    var html = '<div class="dash-header"><h2>⏰ 近效期预警（' + data.days + '天内）</h2></div>';
    if (data.batches.length === 0) {
      html += '<div class="stat-card" style="text-align:center;padding:40px"><div style="font-size:48px;margin-bottom:12px">✅</div><div style="color:var(--green)">暂无近效期物料</div></div>';
      document.getElementById('dashboardContent').innerHTML = html;
      return;
    }
    html += '<div class="table-wrap"><table>';
    html += '<tr><th>批号</th><th>品名</th><th>供应商</th><th>数量</th><th>有效期至</th><th>剩余天数</th><th>存放区域</th></tr>';
    data.batches.forEach(function(b) {
      var daysLeft = Math.round((new Date(b.expiry_date) - new Date()) / (1000*60*60*24));
      var isUrgent = daysLeft <= 30;
      html += '<tr><td><strong>' + b.batch_no + '</strong></td><td>' + b.material_name + '</td><td>' + b.supplier + '</td><td>' + b.quantity + b.unit + '</td><td>' + b.expiry_date + '</td><td style="color:' + (isUrgent ? 'var(--red)' : 'var(--yellow)') + ';font-weight:600">' + daysLeft + '天' + (isUrgent ? ' ⚠️' : '') + '</td><td>' + (b.zone_name || '-') + '</td></tr>';
    });
    html += '</table></div>';
    document.getElementById('dashboardContent').innerHTML = html;
  });
}
