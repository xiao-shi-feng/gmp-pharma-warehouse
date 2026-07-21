/* GMP 药品仓库管理 AI 系统 — 前端交互 */
let currentMode = 'search';

// ============ 初始化 ============
document.addEventListener('DOMContentLoaded', function() {
  loadModules();
  loadWelcome();

  // 输入框回车搜索
  document.getElementById('searchInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') doSearch();
  });

  // 输入框实时提示
  let debounceTimer;
  document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(debounceTimer);
    const q = this.value.trim();
    if (q.length < 2) { document.getElementById('searchHints').innerHTML = ''; return; }
    debounceTimer = setTimeout(function() {
      fetchSuggestions(q);
    }, 300);
  });
});

// ============ 切换模式 ============
function switchMode(mode) {
  currentMode = mode;
  document.querySelectorAll('.search-tab').forEach(function(tab) {
    tab.classList.toggle('active', tab.dataset.mode === mode);
  });
  var input = document.getElementById('searchInput');
  input.placeholder = mode === 'search'
    ? '输入关键词搜索 GMP/GSP 知识库...'
    : '输入你的问题，AI 基于知识库回答...';
  input.focus();
}

// ============ 加载模块列表 ============
function loadModules() {
  fetch('/api/modules').then(function(r) { return r.json(); }).then(function(data) {
    var nav = document.getElementById('moduleNav');
    nav.innerHTML = '';
    data.modules.forEach(function(mod, i) {
      var btn = document.createElement('button');
      btn.className = 'module-item' + (i === 0 ? ' active' : '');
      btn.textContent = mod.name;
      btn.onclick = function() {
        document.querySelectorAll('.module-item').forEach(function(m) { m.classList.remove('active'); });
        btn.classList.add('active');
        showModule(mod.name);
      };
      nav.appendChild(btn);
    });
    document.getElementById('moduleCount').textContent = data.modules.length + '个';
    document.getElementById('headerStats').textContent =
      data.modules.length + ' 模块 · ' + data.modules.reduce(function(s, m) { return s + m.count; }, 0) + ' 条目';
  });
}

// ============ 加载欢迎页 ============
function loadWelcome() {
  fetch('/api/modules').then(function(r) { return r.json(); }).then(function(data) {
    var container = document.getElementById('welcomeModules');
    container.innerHTML = '';
    data.modules.forEach(function(mod) {
      var card = document.createElement('div');
      card.className = 'module-card';
      card.textContent = mod.name;
      card.onclick = function() { showModule(mod.name); };
      container.appendChild(card);
    });
  });
}

// ============ 显示模块详情 ============
function showModule(moduleName) {
  var results = document.getElementById('results');
  results.innerHTML = '<div class="loading">加载中...</div>';

  fetch('/api/module/' + encodeURIComponent(moduleName)).then(function(r) { return r.json(); }).then(function(data) {
    var html = '<div class="module-detail">';
    html += '<h2>📂 ' + data.module + '</h2>';
    html += '<p style="color:#8896b0;font-size:13px;margin-bottom:20px">共 ' + data.entries.length + ' 条内容</p>';

    data.entries.forEach(function(entry) {
      html += '<div class="detail-card">';
      html += '<h3>' + entry.title + '</h3>';
      html += '<p>' + entry.content + '</p>';
      if (entry.keywords && entry.keywords.length > 0) {
        html += '<div class="result-keywords" style="margin-top:10px">';
        entry.keywords.slice(0, 8).forEach(function(kw) {
          html += '<span class="result-keyword">#' + kw + '</span>';
        });
        html += '</div>';
      }
      html += '</div>';
    });
    html += '</div>';
    results.innerHTML = html;
  });
}

// ============ 搜索 ============
function doSearch() {
  var query = document.getElementById('searchInput').value.trim();
  if (!query) return;

  var results = document.getElementById('results');
  results.innerHTML = '<div class="loading">搜索中...</div>';

  if (currentMode === 'ask') {
    // 问答模式
    fetch('/api/ask?q=' + encodeURIComponent(query)).then(function(r) { return r.json(); }).then(function(data) {
      var html = '';
      if (data.answer) {
        html += '<div class="answer-card">';
        html += '<div class="answer-label">💬 AI 回答</div>';
        html += '<div class="answer-text">' + data.answer.replace(/\n/g, '<br>') + '</div>';
        if (data.sources && data.sources.length > 0) {
          html += '<div class="answer-sources">';
          html += '<div style="font-size:11px;color:#546079;margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06)">📋 参考来源：</div>';
          data.sources.forEach(function(src) {
            html += '<div class="answer-source">📄 [' + src.module + '] ' + src.title + '</div>';
          });
          html += '</div>';
        }
        html += '</div>';
      }
      results.innerHTML = html || '<div class="no-results">未找到相关答案，请换种方式提问</div>';
    });
  } else {
    // 搜索模式
    fetch('/api/search?q=' + encodeURIComponent(query)).then(function(r) { return r.json(); }).then(function(data) {
      document.getElementById('searchHints').innerHTML = '';
      if (data.suggestions && data.suggestions.length > 0) {
        data.suggestions.forEach(function(s) {
          var hint = document.createElement('span');
          hint.className = 'search-hint';
          hint.textContent = '📌 ' + s;
          document.getElementById('searchHints').appendChild(hint);
        });
      }

      if (data.results.length === 0) {
        results.innerHTML = '<div class="no-results">未找到匹配结果，请尝试其他关键词</div>';
        return;
      }

      var html = '<div style="font-size:12px;color:#546079;margin-bottom:12px">共 ' + data.total + ' 条结果</div>';
      data.results.forEach(function(r) {
        html += '<div class="result-item">';
        html += '<div class="result-meta">';
        html += '<span class="result-module">' + r.module + '</span>';
        r.tags.slice(0, 3).forEach(function(t) { html += '<span class="result-tag">' + t + '</span>'; });
        html += '</div>';
        html += '<div class="result-title">' + r.title + '</div>';
        html += '<div class="result-content">' + r.summary + '</div>';
        if (r.keywords && r.keywords.length > 0) {
          html += '<div class="result-keywords">';
          r.keywords.slice(0, 10).forEach(function(kw) { html += '<span class="result-keyword">#' + kw + '</span>'; });
          html += '</div>';
        }
        html += '</div>';
      });
      results.innerHTML = html;
    });
  }
}

// ============ 搜索建议 ============
function fetchSuggestions(q) {
  fetch('/api/search?q=' + encodeURIComponent(q)).then(function(r) { return r.json(); }).then(function(data) {
    var container = document.getElementById('searchHints');
    container.innerHTML = '';
    if (data.suggestions && data.suggestions.length > 0) {
      data.suggestions.forEach(function(s) {
        var hint = document.createElement('span');
        hint.className = 'search-hint';
        hint.textContent = '📌 ' + s;
        container.appendChild(hint);
      });
    }
  });
}
