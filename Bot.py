<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TopUp Zone — Boshqaruv Paneli</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0c14;
    --surface: #12151f;
    --surface2: #1a1e2e;
    --border: rgba(100,120,255,0.15);
    --accent: #6477ff;
    --accent2: #a78bfa;
    --accent3: #38bdf8;
    --green: #22d3a0;
    --red: #f87171;
    --yellow: #fbbf24;
    --text: #e2e8f0;
    --muted: #64748b;
    --card-glow: 0 0 40px rgba(100,119,255,0.08);
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'Nunito', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }
  /* BG texture */
  body::before {
    content:'';
    position:fixed; inset:0; z-index:0;
    background: radial-gradient(ellipse 80% 50% at 20% 10%, rgba(100,119,255,0.07) 0%, transparent 60%),
                radial-gradient(ellipse 60% 40% at 80% 80%, rgba(167,139,250,0.05) 0%, transparent 50%);
    pointer-events:none;
  }

  /* ── Login Screen ── */
  #loginScreen {
    position:fixed; inset:0; z-index:100;
    display:flex; align-items:center; justify-content:center;
    background: var(--bg);
  }
  .login-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 48px 44px;
    width: 380px;
    box-shadow: 0 0 80px rgba(100,119,255,0.12), var(--card-glow);
    text-align: center;
    animation: fadeUp .5s ease;
  }
  .login-logo {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
  }
  .login-sub { color: var(--muted); font-size: 13px; margin-bottom: 32px; }
  .login-box label { display:block; text-align:left; font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; margin-bottom:6px; }
  .login-box input {
    width:100%; background:var(--surface2); border:1px solid var(--border);
    border-radius:10px; padding:12px 16px; color:var(--text);
    font-family:inherit; font-size:14px; margin-bottom:16px; outline:none;
    transition: border-color .2s;
  }
  .login-box input:focus { border-color: var(--accent); }
  .login-btn {
    width:100%; padding:14px; background:linear-gradient(135deg,var(--accent),var(--accent2));
    border:none; border-radius:12px; color:#fff; font-family:'Syne',sans-serif;
    font-size:15px; font-weight:700; cursor:pointer; letter-spacing:.04em;
    transition: transform .15s, opacity .15s;
  }
  .login-btn:hover { transform:translateY(-1px); opacity:.9; }
  .login-error { color:var(--red); font-size:13px; margin-top:10px; display:none; }

  /* ── Main Layout ── */
  #app { display:none; min-height:100vh; }
  .sidebar {
    position:fixed; left:0; top:0; bottom:0; width:240px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 28px 16px;
    display:flex; flex-direction:column; gap:4px;
    z-index:10;
  }
  .sidebar-logo {
    font-family:'Syne',sans-serif; font-weight:800; font-size:20px;
    background:linear-gradient(135deg,var(--accent),var(--accent2));
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    padding: 0 12px 20px;
  }
  .nav-item {
    display:flex; align-items:center; gap:10px;
    padding: 10px 12px; border-radius:10px;
    cursor:pointer; font-size:14px; font-weight:600; color:var(--muted);
    transition: all .2s; border:1px solid transparent;
  }
  .nav-item:hover { color:var(--text); background:var(--surface2); }
  .nav-item.active { color:var(--accent); background:rgba(100,119,255,.1); border-color:var(--border); }
  .nav-icon { font-size:16px; width:22px; text-align:center; }
  .sidebar-footer {
    margin-top:auto; padding-top:16px; border-top:1px solid var(--border);
    font-size:12px; color:var(--muted); padding:16px 12px 0;
  }
  .logout-btn {
    width:100%; margin-top:8px; padding:9px; background:rgba(248,113,113,.1);
    border:1px solid rgba(248,113,113,.2); border-radius:8px; color:var(--red);
    font-size:13px; font-weight:600; cursor:pointer; transition:.2s;
  }
  .logout-btn:hover { background:rgba(248,113,113,.2); }

  .main {
    margin-left:240px; padding:32px 36px;
    position:relative; z-index:1;
    min-height:100vh;
  }
  .page { display:none; }
  .page.active { display:block; animation:fadeUp .3s ease; }

  /* ── Cards ── */
  .page-title {
    font-family:'Syne',sans-serif; font-size:26px; font-weight:800;
    margin-bottom:8px;
  }
  .page-desc { color:var(--muted); font-size:14px; margin-bottom:28px; }
  .stat-grid {
    display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:28px;
  }
  .stat-card {
    background:var(--surface); border:1px solid var(--border); border-radius:16px;
    padding:20px 24px; box-shadow:var(--card-glow);
    transition: transform .2s, border-color .2s;
  }
  .stat-card:hover { transform:translateY(-2px); border-color:rgba(100,119,255,.3); }
  .stat-label { font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; margin-bottom:8px; }
  .stat-value { font-family:'Syne',sans-serif; font-size:28px; font-weight:800; }
  .stat-sub { font-size:12px; color:var(--muted); margin-top:4px; }
  .stat-card.green .stat-value { color:var(--green); }
  .stat-card.blue .stat-value { color:var(--accent3); }
  .stat-card.purple .stat-value { color:var(--accent2); }
  .stat-card.yellow .stat-value { color:var(--yellow); }

  /* ── Table ── */
  .section-card {
    background:var(--surface); border:1px solid var(--border); border-radius:16px;
    padding:24px; margin-bottom:20px; box-shadow:var(--card-glow);
  }
  .section-head {
    display:flex; align-items:center; justify-content:space-between; margin-bottom:20px;
  }
  .section-title { font-family:'Syne',sans-serif; font-size:16px; font-weight:700; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th { text-align:left; color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; padding:8px 12px; border-bottom:1px solid var(--border); }
  td { padding:12px 12px; border-bottom:1px solid rgba(255,255,255,.04); vertical-align:middle; }
  tr:last-child td { border-bottom:none; }
  tr:hover td { background:rgba(255,255,255,.02); }
  .badge {
    display:inline-flex; align-items:center; gap:4px;
    padding:3px 10px; border-radius:99px; font-size:11px; font-weight:700;
  }
  .badge-green { background:rgba(34,211,160,.15); color:var(--green); }
  .badge-red { background:rgba(248,113,113,.15); color:var(--red); }
  .badge-yellow { background:rgba(251,191,36,.15); color:var(--yellow); }
  .badge-blue { background:rgba(56,189,248,.15); color:var(--accent3); }
  .badge-purple { background:rgba(167,139,250,.15); color:var(--accent2); }
  .mono { font-family:'DM Mono',monospace; font-size:12px; color:var(--muted); }

  /* ── Buttons ── */
  .btn {
    padding:8px 18px; border-radius:9px; font-family:inherit;
    font-size:13px; font-weight:700; cursor:pointer; transition:.2s;
    border:1px solid transparent;
  }
  .btn-primary { background:var(--accent); color:#fff; }
  .btn-primary:hover { opacity:.85; }
  .btn-danger { background:rgba(248,113,113,.15); color:var(--red); border-color:rgba(248,113,113,.3); }
  .btn-danger:hover { background:rgba(248,113,113,.25); }
  .btn-ghost { background:var(--surface2); color:var(--text); border-color:var(--border); }
  .btn-ghost:hover { border-color:var(--accent); color:var(--accent); }
  .btn-success { background:rgba(34,211,160,.15); color:var(--green); border-color:rgba(34,211,160,.3); }
  .btn-success:hover { background:rgba(34,211,160,.25); }
  .btn-sm { padding:5px 12px; font-size:12px; border-radius:7px; }

  /* ── Form ── */
  .form-row { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px; }
  .form-group { display:flex; flex-direction:column; gap:6px; }
  .form-group.full { grid-column:1/-1; }
  .form-label { font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; }
  .form-input, .form-select {
    background:var(--surface2); border:1px solid var(--border); border-radius:10px;
    padding:11px 14px; color:var(--text); font-family:inherit; font-size:14px;
    outline:none; transition:.2s;
  }
  .form-input:focus, .form-select:focus { border-color:var(--accent); }
  .form-select option { background:var(--surface2); }
  .form-actions { display:flex; gap:10px; margin-top:4px; }

  /* ── Toggle ── */
  .toggle-wrap { display:flex; align-items:center; gap:10px; }
  .toggle {
    position:relative; width:42px; height:24px; cursor:pointer;
  }
  .toggle input { opacity:0; width:0; height:0; }
  .toggle-slider {
    position:absolute; inset:0; background:var(--surface2); border-radius:99px;
    border:1px solid var(--border); transition:.3s;
  }
  .toggle-slider::before {
    content:''; position:absolute; width:16px; height:16px;
    left:3px; bottom:3px; border-radius:50%; background:var(--muted);
    transition:.3s;
  }
  .toggle input:checked + .toggle-slider { background:rgba(34,211,160,.25); border-color:var(--green); }
  .toggle input:checked + .toggle-slider::before { transform:translateX(18px); background:var(--green); }

  /* ── Order detail ── */
  .order-detail-row { display:flex; gap:8px; align-items:center; }
  .detail-key { font-size:12px; color:var(--muted); width:100px; flex-shrink:0; }
  .detail-val { font-size:13px; font-weight:600; }

  /* ── Chart ── */
  .chart-wrap { height:160px; position:relative; display:flex; align-items:flex-end; gap:6px; padding:12px 0 0; }
  .chart-bar-wrap { flex:1; display:flex; flex-direction:column; align-items:center; gap:4px; }
  .chart-bar { width:100%; border-radius:6px 6px 0 0; transition:.5s ease; min-height:4px; }
  .chart-label { font-size:10px; color:var(--muted); }

  /* ── Empty state ── */
  .empty { text-align:center; padding:40px 20px; color:var(--muted); font-size:14px; }
  .empty-icon { font-size:36px; margin-bottom:10px; }

  /* ── Modal ── */
  .modal-overlay {
    position:fixed; inset:0; background:rgba(0,0,0,.7); z-index:200;
    display:flex; align-items:center; justify-content:center;
    backdrop-filter:blur(4px);
  }
  .modal {
    background:var(--surface); border:1px solid var(--border); border-radius:20px;
    padding:32px; width:480px; max-width:95vw;
    box-shadow:0 0 80px rgba(100,119,255,.2);
    animation:fadeUp .25s ease;
  }
  .modal-title { font-family:'Syne',sans-serif; font-size:18px; font-weight:800; margin-bottom:20px; }
  .modal-close { float:right; background:none; border:none; color:var(--muted); font-size:20px; cursor:pointer; }

  /* ── Animations ── */
  @keyframes fadeUp {
    from { opacity:0; transform:translateY(12px); }
    to   { opacity:1; transform:translateY(0); }
  }

  /* ── Alert ── */
  .alert {
    position:fixed; top:24px; right:24px; z-index:999;
    background:var(--surface); border:1px solid var(--border); border-radius:12px;
    padding:14px 20px; font-size:13px; font-weight:600;
    box-shadow:0 8px 32px rgba(0,0,0,.4);
    display:none; animation:fadeUp .3s ease;
  }
  .alert.show { display:block; }
  .alert.success { border-color:rgba(34,211,160,.4); color:var(--green); }
  .alert.error { border-color:rgba(248,113,113,.4); color:var(--red); }

  /* Rate inputs */
  .rate-card {
    background:var(--surface2); border:1px solid var(--border); border-radius:14px;
    padding:20px 24px; display:flex; align-items:center; gap:16px; margin-bottom:12px;
  }
  .rate-icon { font-size:28px; }
  .rate-info { flex:1; }
  .rate-name { font-weight:700; font-size:15px; }
  .rate-cur { font-size:13px; color:var(--muted); margin-top:2px; }
  .rate-input-wrap { display:flex; gap:8px; align-items:center; }
  .rate-input { width:120px; }

  /* Scrollbar */
  ::-webkit-scrollbar { width:6px; }
  ::-webkit-scrollbar-track { background:transparent; }
  ::-webkit-scrollbar-thumb { background:var(--surface2); border-radius:99px; }
</style>
</head>
<body>

<!-- Login Screen -->
<div id="loginScreen">
  <div class="login-box">
    <div class="login-logo">⚡ TopUp Zone</div>
    <div class="login-sub">Admin Boshqaruv Paneli</div>
    <label>Login</label>
    <input type="text" id="loginInput" placeholder="Admin username">
    <label>Parol</label>
    <input type="password" id="passInput" placeholder="••••••••" onkeydown="if(event.key==='Enter')doLogin()">
    <button class="login-btn" onclick="doLogin()">Kirish →</button>
    <div class="login-error" id="loginErr">❌ Login yoki parol noto'g'ri!</div>
  </div>
</div>

<!-- App -->
<div id="app">
  <!-- Sidebar -->
  <div class="sidebar">
    <div class="sidebar-logo">⚡ TopUp Zone</div>
    <div class="nav-item active" onclick="showPage('dashboard')">
      <span class="nav-icon">📊</span> Dashboard
    </div>
    <div class="nav-item" onclick="showPage('orders')">
      <span class="nav-icon">📦</span> Buyurtmalar
    </div>
    <div class="nav-item" onclick="showPage('packages')">
      <span class="nav-icon">💎</span> Paketlar
    </div>
    <div class="nav-item" onclick="showPage('rates')">
      <span class="nav-icon">💱</span> Kurslar
    </div>
    <div class="nav-item" onclick="showPage('status')">
      <span class="nav-icon">🔦</span> Bo'lim holati
    </div>
    <div class="nav-item" onclick="showPage('users')">
      <span class="nav-icon">👥</span> Foydalanuvchilar
    </div>
    <div class="nav-item" onclick="showPage('admins')">
      <span class="nav-icon">👮</span> Adminlar
    </div>
    <div class="nav-item" onclick="showPage('ads')">
      <span class="nav-icon">📣</span> Reklama
    </div>
    <div class="sidebar-footer">
      <div>Admin: <strong>Admin</strong></div>
      <button class="logout-btn" onclick="doLogout()">🚪 Chiqish</button>
    </div>
  </div>

  <!-- Main -->
  <div class="main">

    <!-- Dashboard -->
    <div class="page active" id="page-dashboard">
      <div class="page-title">📊 Dashboard</div>
      <div class="page-desc">Botning umumiy holati va statistikasi</div>
      <div class="stat-grid">
        <div class="stat-card green">
          <div class="stat-label">Jami Foydalanuvchilar</div>
          <div class="stat-value" id="statUsers">247</div>
          <div class="stat-sub">Ro'yxatdan o'tgan</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-label">Jami Buyurtmalar</div>
          <div class="stat-value" id="statOrders">183</div>
          <div class="stat-sub">Tasdiqlangan xaridlar</div>
        </div>
        <div class="stat-card purple">
          <div class="stat-label">Jami Daromad</div>
          <div class="stat-value" id="statIncome">4.6M</div>
          <div class="stat-sub">so'm</div>
        </div>
        <div class="stat-card yellow">
          <div class="stat-label">Kutilayotgan</div>
          <div class="stat-value" id="statPending">3</div>
          <div class="stat-sub">Tasdiqlash kerak</div>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1.4fr 1fr;gap:20px;">
        <div class="section-card">
          <div class="section-head">
            <div class="section-title">📈 Haftalik buyurtmalar</div>
          </div>
          <div class="chart-wrap" id="weekChart"></div>
        </div>
        <div class="section-card">
          <div class="section-head">
            <div class="section-title">🔦 Xizmat holati</div>
          </div>
          <div id="statusMini"></div>
        </div>
      </div>

      <div class="section-card" style="margin-top:20px;">
        <div class="section-head">
          <div class="section-title">⏱ Oxirgi buyurtmalar</div>
          <button class="btn btn-ghost btn-sm" onclick="showPage('orders')">Barchasi →</button>
        </div>
        <table id="recentOrdersTable">
          <thead><tr>
            <th>Foydalanuvchi</th><th>Mahsulot</th><th>Narx</th><th>Holat</th><th>Sana</th>
          </tr></thead>
          <tbody id="recentOrdersTbody"></tbody>
        </table>
      </div>
    </div>

    <!-- Orders -->
    <div class="page" id="page-orders">
      <div class="page-title">📦 Buyurtmalar</div>
      <div class="page-desc">Barcha buyurtmalar tarixi</div>
      <div class="section-card">
        <div class="section-head">
          <div style="display:flex;gap:10px;align-items:center;">
            <input class="form-input" id="orderSearch" placeholder="🔍 Qidirish..." style="width:220px;padding:8px 12px;" oninput="renderOrders()">
            <select class="form-select" id="orderFilter" style="padding:8px 12px;" onchange="renderOrders()">
              <option value="">Barchasi</option>
              <option value="pending">Kutilmoqda</option>
              <option value="approved">Tasdiqlangan</option>
              <option value="rejected">Rad etilgan</option>
            </select>
          </div>
          <button class="btn btn-primary btn-sm" onclick="openAddOrderModal()">+ Yangi buyurtma</button>
        </div>
        <table>
          <thead><tr>
            <th>#</th><th>Foydalanuvchi</th><th>Mahsulot</th><th>Bo'lim</th><th>Narx</th><th>Qabul qiluvchi</th><th>Holat</th><th>Sana</th><th>Amal</th>
          </tr></thead>
          <tbody id="ordersTbody"></tbody>
        </table>
      </div>
    </div>

    <!-- Packages -->
    <div class="page" id="page-packages">
      <div class="page-title">💎 TG Paketlar</div>
      <div class="page-desc">Telegram Premium, Stars va TON paketlarini boshqarish</div>
      <div style="display:grid;grid-template-columns:1fr 1.2fr;gap:20px;">
        <div class="section-card">
          <div class="section-head">
            <div class="section-title">Mavjud paketlar</div>
          </div>
          <div id="packagesList"></div>
        </div>
        <div class="section-card">
          <div class="section-head">
            <div class="section-title">➕ Yangi paket qo'shish</div>
          </div>
          <div class="form-group" style="margin-bottom:14px;">
            <label class="form-label">Bo'lim</label>
            <select class="form-select" id="pkgSection">
              <option value="prem">💎 Telegram Premium</option>
              <option value="stars">⭐ Telegram Stars</option>
              <option value="ton">💠 TON</option>
            </select>
          </div>
          <div class="form-group" style="margin-bottom:14px;">
            <label class="form-label">Usul</label>
            <select class="form-select" id="pkgMethod">
              <option value="id">📨 @username orqali (gift)</option>
              <option value="acc">🔑 Acc kirib (login/parol)</option>
            </select>
          </div>
          <div class="form-group" style="margin-bottom:14px;">
            <label class="form-label">Paket nomi</label>
            <input class="form-input" id="pkgName" placeholder="Misol: 1 oylik Premium">
          </div>
          <div class="form-group" style="margin-bottom:20px;">
            <label class="form-label">Narxi (so'm)</label>
            <input class="form-input" id="pkgPrice" type="number" placeholder="Misol: 42000">
          </div>
          <button class="btn btn-primary" onclick="addPackage()" style="width:100%;">✅ Paket qo'shish</button>
        </div>
      </div>
    </div>

    <!-- Rates -->
    <div class="page" id="page-rates">
      <div class="page-title">💱 Valyuta Kurslari</div>
      <div class="page-desc">Stars va TON kurslarini sozlash</div>
      <div style="max-width:520px;">
        <div class="rate-card">
          <div class="rate-icon">⭐</div>
          <div class="rate-info">
            <div class="rate-name">Telegram Stars</div>
            <div class="rate-cur">Joriy kurs: <strong id="starsRateCur">250 so'm</strong></div>
          </div>
          <div class="rate-input-wrap">
            <input class="form-input rate-input" id="starsRateInput" type="number" placeholder="250">
            <button class="btn btn-success btn-sm" onclick="saveRate('stars')">Saqlash</button>
          </div>
        </div>
        <div class="rate-card">
          <div class="rate-icon">💠</div>
          <div class="rate-info">
            <div class="rate-name">TON</div>
            <div class="rate-cur">Joriy kurs: <strong id="tonRateCur">17.500 so'm</strong></div>
          </div>
          <div class="rate-input-wrap">
            <input class="form-input rate-input" id="tonRateInput" type="number" placeholder="17500">
            <button class="btn btn-success btn-sm" onclick="saveRate('ton')">Saqlash</button>
          </div>
        </div>
        <div class="section-card" style="margin-top:20px;">
          <div class="section-title" style="margin-bottom:14px;">💡 Joriy narxlar (hisoblash)</div>
          <div id="priceCalc" style="display:flex;flex-direction:column;gap:6px;font-size:13px;"></div>
        </div>
      </div>
    </div>

    <!-- Status -->
    <div class="page" id="page-status">
      <div class="page-title">🔦 Bo'lim Holati</div>
      <div class="page-desc">Xizmatlarni yoqish / o'chirish</div>
      <div style="max-width:460px;">
        <div class="section-card">
          <div id="statusToggles" style="display:flex;flex-direction:column;gap:16px;"></div>
        </div>
      </div>
    </div>

    <!-- Users -->
    <div class="page" id="page-users">
      <div class="page-title">👥 Foydalanuvchilar</div>
      <div class="page-desc">Bot foydalanuvchilari ro'yxati</div>
      <div class="section-card">
        <div class="section-head">
          <input class="form-input" id="userSearch" placeholder="🔍 Ism yoki username..." style="width:240px;padding:8px 12px;" oninput="renderUsers()">
          <div style="font-size:13px;color:var(--muted);">Jami: <strong id="totalUsersCount">0</strong> ta</div>
        </div>
        <table>
          <thead><tr>
            <th>ID</th><th>Ism</th><th>Username</th><th>Xaridlar</th><th>Sarflagan</th><th>Oxirgi xarid</th>
          </tr></thead>
          <tbody id="usersTbody"></tbody>
        </table>
      </div>
    </div>

    <!-- Admins -->
    <div class="page" id="page-admins">
      <div class="page-title">👮 Adminlar</div>
      <div class="page-desc">Admin huquqlarini boshqarish</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div class="section-card">
          <div class="section-head">
            <div class="section-title">Adminlar ro'yxati</div>
          </div>
          <div id="adminsList"></div>
        </div>
        <div class="section-card">
          <div class="section-title" style="margin-bottom:16px;">➕ Admin qo'shish</div>
          <div class="form-group" style="margin-bottom:14px;">
            <label class="form-label">Telegram ID</label>
            <input class="form-input" id="newAdminId" type="number" placeholder="Misol: 123456789">
          </div>
          <div class="form-group" style="margin-bottom:14px;">
            <label class="form-label">Ism</label>
            <input class="form-input" id="newAdminName" placeholder="Admin ismi">
          </div>
          <div class="form-group" style="margin-bottom:20px;">
            <label class="form-label">Username</label>
            <input class="form-input" id="newAdminUsername" placeholder="@username">
          </div>
          <button class="btn btn-primary" onclick="addAdmin()" style="width:100%;">✅ Admin qilish</button>
        </div>
      </div>
    </div>

    <!-- Ads -->
    <div class="page" id="page-ads">
      <div class="page-title">📣 Reklama</div>
      <div class="page-desc">Barcha foydalanuvchilarga xabar yuborish</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
        <div class="section-card">
          <div class="section-title" style="margin-bottom:16px;">📝 Yangi reklama yaratish</div>
          <div class="form-group" style="margin-bottom:14px;">
            <label class="form-label">Xabar matni</label>
            <textarea class="form-input" id="adText" rows="5" placeholder="Reklama matni bu yerga..."></textarea>
          </div>
          <div class="form-group" style="margin-bottom:20px;">
            <label class="form-label">Holat</label>
            <select class="form-select" id="adStatus">
              <option value="pending">Kutilmoqda (owner tasdiqlashi kerak)</option>
              <option value="approved">Darhol yuborish</option>
            </select>
          </div>
          <button class="btn btn-primary" onclick="createAd()" style="width:100%;">📤 Reklama yaratish</button>
        </div>
        <div class="section-card">
          <div class="section-head">
            <div class="section-title">Reklamalar tarixi</div>
          </div>
          <div id="adsList"></div>
        </div>
      </div>
    </div>

  </div><!-- /main -->
</div><!-- /app -->

<!-- Alert -->
<div class="alert" id="alertBox"></div>

<!-- Modal: Add Order -->
<div class="modal-overlay" id="addOrderModal" style="display:none;" onclick="if(event.target===this)this.style.display='none'">
  <div class="modal">
    <div class="modal-title">📦 Yangi buyurtma <button class="modal-close" onclick="document.getElementById('addOrderModal').style.display='none'">×</button></div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Foydalanuvchi ismi</label>
        <input class="form-input" id="newOrderUser" placeholder="Ism">
      </div>
      <div class="form-group">
        <label class="form-label">Username</label>
        <input class="form-input" id="newOrderUsername" placeholder="@username">
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Bo'lim</label>
        <select class="form-select" id="newOrderSection">
          <option value="Telegram Premium">💎 Telegram Premium</option>
          <option value="Telegram Stars">⭐ Telegram Stars</option>
          <option value="TON">💠 TON</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Mahsulot nomi</label>
        <input class="form-input" id="newOrderProduct" placeholder="Misol: 1 oylik Premium">
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Narxi (so'm)</label>
        <input class="form-input" id="newOrderPrice" type="number" placeholder="42000">
      </div>
      <div class="form-group">
        <label class="form-label">Qabul qiluvchi</label>
        <input class="form-input" id="newOrderRecipient" placeholder="@username yoki hamyon">
      </div>
    </div>
    <div class="form-actions">
      <button class="btn btn-primary" onclick="saveNewOrder()">✅ Saqlash</button>
      <button class="btn btn-ghost" onclick="document.getElementById('addOrderModal').style.display='none'">Bekor</button>
    </div>
  </div>
</div>

<script>
// ==================== DATA ====================
const CORRECT_LOGIN = 'Admin';
const CORRECT_PASS  = '18092010';

let db = {
  stars_rate: 250,
  ton_rate: 17500,
  status: { prem: true, stars: true, ton: true },
  tg_packages: [
    { id:1, name:'1 oylik Premium', price:85000, section:'prem', method:'id' },
    { id:2, name:'3 oylik Premium', price:220000, section:'prem', method:'id' },
    { id:3, name:'1 oylik Premium (Login bilan)', price:75000, section:'prem', method:'acc' },
    { id:4, name:'50 Stars', price:12500, section:'stars', method:'id' },
    { id:5, name:'100 Stars', price:25000, section:'stars', method:'id' },
    { id:6, name:'250 Stars', price:62500, section:'stars', method:'id' },
    { id:7, name:'500 Stars', price:125000, section:'stars', method:'id' },
    { id:8, name:'1 TON', price:17500, section:'ton', method:'id' },
    { id:9, name:'5 TON', price:87500, section:'ton', method:'id' },
    { id:10, name:'10 TON', price:175000, section:'ton', method:'id' },
  ],
  users: {
    '101001': { name:'Alisher Karimov', username:'ali_k99', orders:[], total_spent:0 },
    '101002': { name:'Nilufar Rashidova', username:'nilufar_r', orders:[], total_spent:0 },
    '101003': { name:'Jasur Toshmatov', username:'jasur_t', orders:[], total_spent:0 },
    '101004': { name:'Malika Yusupova', username:'malika_y', orders:[], total_spent:0 },
    '101005': { name:'Bobur Mirzayev', username:'bobur_m', orders:[], total_spent:0 },
    '101006': { name:'Sherzod Normatov', username:'sherzod_n', orders:[], total_spent:0 },
    '101007': { name:'Zulfiya Abdullayeva', username:'zulfiya_a', orders:[], total_spent:0 },
    '101008': { name:'Davron Xolmatov', username:'davron_x', orders:[], total_spent:0 },
    '101009': { name:'Kamola Ismoilova', username:'kamola_i', orders:[], total_spent:0 },
    '101010': { name:'Ulugbek Sobirov', username:'ulugbek_s', orders:[], total_spent:0 },
  },
  admin_ids: [7362457858],
  pending_ads: {},
};

let orders = [
  { id:1001, userId:'101001', userName:'Alisher Karimov', username:'@ali_k99', product:'1 oylik Premium', section:'Telegram Premium', price:85000, recipient:'@ali_k99', status:'approved', source:'Bot', date:'2025-04-15 14:32' },
  { id:1002, userId:'101002', userName:'Nilufar Rashidova', username:'@nilufar_r', product:'100 Stars', section:'Telegram Stars', price:25000, recipient:'@nilufar_r', status:'approved', source:'Sayt', date:'2025-04-15 16:10' },
  { id:1003, userId:'101003', userName:'Jasur Toshmatov', username:'@jasur_t', product:'5 TON', section:'TON', price:87500, recipient:'UQ...XY', status:'approved', source:'Bot', date:'2025-04-16 09:45' },
  { id:1004, userId:'101004', userName:'Malika Yusupova', username:'@malika_y', product:'3 oylik Premium', section:'Telegram Premium', price:220000, recipient:'@malika_y', status:'pending', source:'Bot', date:'2025-04-17 11:20' },
  { id:1005, userId:'101005', userName:'Bobur Mirzayev', username:'@bobur_m', product:'250 Stars', section:'Telegram Stars', price:62500, recipient:'@bobur_m', status:'pending', source:'Sayt', date:'2025-04-17 13:55' },
  { id:1006, userId:'101006', userName:'Sherzod Normatov', username:'@sherzod_n', product:'10 TON', section:'TON', price:175000, recipient:'EQ...AB', status:'rejected', source:'Bot', date:'2025-04-16 18:30' },
  { id:1007, userId:'101007', userName:'Zulfiya Abdullayeva', username:'@zulfiya_a', product:'1 oylik Premium', section:'Telegram Premium', price:85000, recipient:'@zulfiya_a', status:'approved', source:'Bot', date:'2025-04-14 10:05' },
  { id:1008, userId:'101008', userName:'Davron Xolmatov', username:'@davron_x', product:'500 Stars', section:'Telegram Stars', price:125000, recipient:'@davron_x', status:'pending', source:'Sayt', date:'2025-04-18 08:11' },
  { id:1009, userId:'101009', userName:'Kamola Ismoilova', username:'@kamola_i', product:'1 oylik Premium (Login bilan)', section:'Telegram Premium', price:75000, recipient:'@kamola_i', status:'approved', source:'Bot', date:'2025-04-13 15:40' },
  { id:1010, userId:'101010', userName:'Ulugbek Sobirov', username:'@ulugbek_s', product:'1 TON', section:'TON', price:17500, recipient:'UQ...ZZ', status:'approved', source:'Bot', date:'2025-04-12 12:22' },
];

let ads = [
  { id:'ad001', text:'🎉 TopUp Zone — eng arzon narxlarda Telegram Premium, Stars va TON!\n\nBugun xarid qiling!', status:'approved', from_name:'Admin', date:'2025-04-10' },
  { id:'ad002', text:'⭐ 100 Stars atigi 25.000 so'm! Chegirma faqat bugun!', status:'pending', from_name:'Admin', date:'2025-04-18' },
];

let adminUsers = [
  { id: 7362457858, name: 'Owner (Sizning Botingiz)', username: 'Nobody_ff2' },
];

// Update user orders/spending from orders list
orders.forEach(o => {
  const u = db.users[o.userId];
  if (u && o.status === 'approved') {
    u.orders.push({ product: o.product, price: o.price, section: o.section, recipient: o.recipient });
    u.total_spent += o.price;
  }
});

// ==================== AUTH ====================
function doLogin() {
  const l = document.getElementById('loginInput').value.trim();
  const p = document.getElementById('passInput').value;
  if (l === CORRECT_LOGIN && p === CORRECT_PASS) {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    initApp();
  } else {
    document.getElementById('loginErr').style.display = 'block';
  }
}
function doLogout() {
  document.getElementById('app').style.display = 'none';
  document.getElementById('loginScreen').style.display = 'flex';
  document.getElementById('loginInput').value = '';
  document.getElementById('passInput').value = '';
  document.getElementById('loginErr').style.display = 'none';
}

// ==================== NAV ====================
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => {
    if (n.getAttribute('onclick') && n.getAttribute('onclick').includes("'"+id+"'")) n.classList.add('active');
  });
  if (id === 'packages')  renderPackages();
  if (id === 'orders')    renderOrders();
  if (id === 'users')     renderUsers();
  if (id === 'admins')    renderAdmins();
  if (id === 'status')    renderStatus();
  if (id === 'rates')     renderRates();
  if (id === 'ads')       renderAds();
}

// ==================== INIT ====================
function initApp() {
  renderDashboard();
  renderOrders();
  renderPackages();
  renderUsers();
  renderAdmins();
  renderStatus();
  renderRates();
  renderAds();
}

function fmt(n) {
  return Number(n).toLocaleString('ru-RU') + " so'm";
}
function shortMoney(n) {
  if (n >= 1000000) return (n/1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n/1000).toFixed(0) + 'K';
  return n;
}

// ==================== DASHBOARD ====================
function renderDashboard() {
  const totalUsers = Object.keys(db.users).length;
  const totalOrders = orders.filter(o => o.status === 'approved').length;
  const totalIncome = orders.filter(o => o.status === 'approved').reduce((s,o) => s+o.price, 0);
  const pending = orders.filter(o => o.status === 'pending').length;
  document.getElementById('statUsers').textContent = totalUsers;
  document.getElementById('statOrders').textContent = totalOrders;
  document.getElementById('statIncome').textContent = shortMoney(totalIncome);
  document.getElementById('statPending').textContent = pending;

  // Week chart
  const days = ['Du','Se','Ch','Pa','Ju','Sh','Ya'];
  const vals = [12,19,8,27,15,34,22];
  const max = Math.max(...vals);
  const chart = document.getElementById('weekChart');
  chart.innerHTML = vals.map((v,i) => `
    <div class="chart-bar-wrap">
      <div class="chart-bar" style="height:${(v/max*100)}%;background:linear-gradient(180deg,var(--accent),var(--accent2));opacity:.85;"></div>
      <div class="chart-label">${days[i]}</div>
    </div>
  `).join('');

  // Status mini
  const sections = [{id:'prem',name:'💎 Premium'},{id:'stars',name:'⭐ Stars'},{id:'ton',name:'💠 TON'}];
  document.getElementById('statusMini').innerHTML = sections.map(s => {
    const on = db.status[s.id];
    return `<div style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border);">
      <span style="font-size:14px;font-weight:600;">${s.name}</span>
      <span class="badge ${on?'badge-green':'badge-red'}">${on?'✅ Yoqiq':'❌ O\'chiq'}</span>
    </div>`;
  }).join('');

  // Recent orders
  const recent = [...orders].sort((a,b) => b.id - a.id).slice(0,5);
  document.getElementById('recentOrdersTbody').innerHTML = recent.map(o => `
    <tr>
      <td><strong>${o.userName}</strong><br><span class="mono">${o.username}</span></td>
      <td>${o.product}</td>
      <td>${fmt(o.price)}</td>
      <td>${statusBadge(o.status)}</td>
      <td class="mono">${o.date}</td>
    </tr>
  `).join('') || `<tr><td colspan="5" class="empty">Ma'lumot yo'q</td></tr>`;
}

function statusBadge(s) {
  if (s==='approved') return '<span class="badge badge-green">✅ Tasdiqlangan</span>';
  if (s==='pending')  return '<span class="badge badge-yellow">⏳ Kutilmoqda</span>';
  if (s==='rejected') return '<span class="badge badge-red">❌ Rad etildi</span>';
  return s;
}
function sectionBadge(s) {
  if (s.includes('Premium')) return '<span class="badge badge-purple">💎 Premium</span>';
  if (s.includes('Stars'))   return '<span class="badge badge-yellow">⭐ Stars</span>';
  if (s.includes('TON'))     return '<span class="badge badge-blue">💠 TON</span>';
  return s;
}

// ==================== ORDERS ====================
function renderOrders() {
  const q = (document.getElementById('orderSearch')?.value||'').toLowerCase();
  const f = document.getElementById('orderFilter')?.value||'';
  const list = orders.filter(o => {
    const match = o.userName.toLowerCase().includes(q) || o.username.toLowerCase().includes(q) || o.product.toLowerCase().includes(q);
    const filt = !f || o.status === f;
    return match && filt;
  });
  document.getElementById('ordersTbody').innerHTML = list.map(o => `
    <tr>
      <td class="mono">#${o.id}</td>
      <td><strong>${o.userName}</strong><br><span class="mono">${o.username}</span></td>
      <td>${o.product}</td>
      <td>${sectionBadge(o.section)}</td>
      <td><strong>${fmt(o.price)}</strong></td>
      <td class="mono">${o.recipient}</td>
      <td>${statusBadge(o.status)}</td>
      <td class="mono">${o.date}</td>
      <td>
        ${o.status==='pending'?`
          <button class="btn btn-success btn-sm" onclick="changeOrderStatus(${o.id},'approved')">✅</button>
          <button class="btn btn-danger btn-sm" onclick="changeOrderStatus(${o.id},'rejected')">❌</button>
        `:''}
        <button class="btn btn-ghost btn-sm" onclick="deleteOrder(${o.id})">🗑</button>
      </td>
    </tr>
  `).join('') || `<tr><td colspan="9"><div class="empty"><div class="empty-icon">📦</div>Buyurtma topilmadi</div></td></tr>`;
}

function changeOrderStatus(id, status) {
  const o = orders.find(x => x.id === id);
  if (o) { o.status = status; renderOrders(); renderDashboard(); showAlert(status==='approved'?'✅ Tasdiqlandi!':'❌ Rad etildi!', status==='approved'?'success':'error'); }
}
function deleteOrder(id) {
  if (!confirm('Bu buyurtmani o\'chirasizmi?')) return;
  orders = orders.filter(x => x.id !== id);
  renderOrders(); renderDashboard();
  showAlert('🗑 Buyurtma o\'chirildi', 'success');
}
function openAddOrderModal() {
  document.getElementById('addOrderModal').style.display = 'flex';
}
function saveNewOrder() {
  const user = document.getElementById('newOrderUser').value.trim();
  const username = document.getElementById('newOrderUsername').value.trim();
  const section = document.getElementById('newOrderSection').value;
  const product = document.getElementById('newOrderProduct').value.trim();
  const price = parseInt(document.getElementById('newOrderPrice').value)||0;
  const recipient = document.getElementById('newOrderRecipient').value.trim();
  if (!user || !product || !price) { showAlert('Maydonlarni to\'ldiring!', 'error'); return; }
  const newId = Math.max(...orders.map(o=>o.id)) + 1;
  orders.unshift({ id:newId, userId:'manual', userName:user, username:username||'—', product, section, price, recipient:recipient||'—', status:'pending', source:'Admin', date:new Date().toLocaleString('ru-RU').replace(',','') });
  document.getElementById('addOrderModal').style.display = 'none';
  renderOrders(); renderDashboard();
  showAlert('✅ Buyurtma qo\'shildi!', 'success');
}

// ==================== PACKAGES ====================
function sectionName(s) {
  return {prem:'💎 Premium', stars:'⭐ Stars', ton:'💠 TON'}[s]||s;
}
function renderPackages() {
  const sections = ['prem','stars','ton'];
  let html = '';
  sections.forEach(sec => {
    const pkgs = db.tg_packages.filter(p => p.section === sec);
    html += `<div style="margin-bottom:18px;"><div style="font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;">${sectionName(sec)}</div>`;
    if (!pkgs.length) { html += `<div style="font-size:13px;color:var(--muted);padding:8px 0;">Paket yo'q</div>`; }
    pkgs.forEach(p => {
      const meth = p.method === 'acc' ? '<span class="badge badge-blue">🔑 Acc</span>' : '<span class="badge badge-purple">@id</span>';
      html += `<div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--border);">
        <div style="flex:1;">
          <div style="font-weight:600;font-size:13px;">${p.name}</div>
          <div style="font-size:12px;color:var(--muted);margin-top:2px;">${fmt(p.price)} ${meth}</div>
        </div>
        <button class="btn btn-danger btn-sm" onclick="deletePackage(${p.id})">🗑</button>
      </div>`;
    });
    html += '</div>';
  });
  document.getElementById('packagesList').innerHTML = html;
}

function addPackage() {
  const section = document.getElementById('pkgSection').value;
  const method  = document.getElementById('pkgMethod').value;
  const name    = document.getElementById('pkgName').value.trim();
  const price   = parseInt(document.getElementById('pkgPrice').value)||0;
  if (!name || !price) { showAlert('Nom va narx kiriting!', 'error'); return; }
  const newId = Math.max(0,...db.tg_packages.map(p=>p.id)) + 1;
  db.tg_packages.push({ id:newId, name, price, section, method });
  document.getElementById('pkgName').value = '';
  document.getElementById('pkgPrice').value = '';
  renderPackages();
  showAlert('✅ Paket qo\'shildi!', 'success');
}
function deletePackage(id) {
  if (!confirm('Bu paketni o\'chirasizmi?')) return;
  db.tg_packages = db.tg_packages.filter(p => p.id !== id);
  renderPackages();
  showAlert('🗑 Paket o\'chirildi', 'success');
}

// ==================== RATES ====================
function renderRates() {
  document.getElementById('starsRateCur').textContent = Number(db.stars_rate).toLocaleString('ru-RU') + ' so\'m';
  document.getElementById('tonRateCur').textContent = Number(db.ton_rate).toLocaleString('ru-RU') + ' so\'m';
  document.getElementById('starsRateInput').value = db.stars_rate;
  document.getElementById('tonRateInput').value = db.ton_rate;
  const calc = [
    ['50 Stars', 50 * db.stars_rate],
    ['100 Stars', 100 * db.stars_rate],
    ['500 Stars', 500 * db.stars_rate],
    ['1 TON', db.ton_rate],
    ['5 TON', 5 * db.ton_rate],
    ['10 TON', 10 * db.ton_rate],
  ];
  document.getElementById('priceCalc').innerHTML = calc.map(([n,v]) =>
    `<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--border);">
      <span style="color:var(--muted);">${n}</span>
      <strong>${fmt(v)}</strong>
    </div>`
  ).join('');
}
function saveRate(type) {
  if (type === 'stars') {
    const v = parseInt(document.getElementById('starsRateInput').value)||0;
    if (!v) { showAlert('Kurs kiriting!', 'error'); return; }
    db.stars_rate = v;
  } else {
    const v = parseInt(document.getElementById('tonRateInput').value)||0;
    if (!v) { showAlert('Kurs kiriting!', 'error'); return; }
    db.ton_rate = v;
  }
  renderRates();
  showAlert('✅ Kurs saqlandi!', 'success');
}

// ==================== STATUS ====================
function renderStatus() {
  const items = [
    { id:'prem', name:'💎 Telegram Premium' },
    { id:'stars', name:'⭐ Telegram Stars' },
    { id:'ton', name:'💠 TON' },
  ];
  document.getElementById('statusToggles').innerHTML = items.map(it => {
    const on = db.status[it.id];
    return `<div style="display:flex;align-items:center;justify-content:space-between;">
      <div>
        <div style="font-weight:700;font-size:15px;">${it.name}</div>
        <div style="font-size:12px;color:var(--muted);margin-top:2px;">${on?'Aktiv — foydalanuvchilar ko\'ra oladi':'Nofaol — foydalanuvchilar ko\'ra olmaydi'}</div>
      </div>
      <label class="toggle">
        <input type="checkbox" ${on?'checked':''} onchange="toggleStatus('${it.id}',this.checked)">
        <span class="toggle-slider"></span>
      </label>
    </div>`;
  }).join('');
}
function toggleStatus(id, val) {
  db.status[id] = val;
  renderDashboard();
  showAlert(`${val?'✅ Yoqildi':'❌ O\'chirildi'}: ${id}`, val?'success':'error');
}

// ==================== USERS ====================
function renderUsers() {
  const q = (document.getElementById('userSearch')?.value||'').toLowerCase();
  const list = Object.entries(db.users).filter(([id,u]) =>
    u.name.toLowerCase().includes(q) || (u.username||'').toLowerCase().includes(q)
  );
  document.getElementById('totalUsersCount').textContent = list.length;
  const rows = list.map(([id,u]) => {
    const lastOrder = [...(u.orders||[])].pop();
    return `<tr>
      <td class="mono">${id}</td>
      <td><strong>${u.name}</strong></td>
      <td class="mono">${u.username?'@'+u.username:'—'}</td>
      <td>${(u.orders||[]).length} ta</td>
      <td><strong>${fmt(u.total_spent||0)}</strong></td>
      <td class="mono">${lastOrder?lastOrder.product:'—'}</td>
    </tr>`;
  });
  document.getElementById('usersTbody').innerHTML = rows.join('') || `<tr><td colspan="6"><div class="empty"><div class="empty-icon">👥</div>Foydalanuvchi topilmadi</div></td></tr>`;
}

// ==================== ADMINS ====================
function renderAdmins() {
  if (!adminUsers.length) {
    document.getElementById('adminsList').innerHTML = `<div class="empty"><div class="empty-icon">👮</div>Admin yo'q</div>`;
    return;
  }
  document.getElementById('adminsList').innerHTML = adminUsers.map(a => `
    <div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--border);">
      <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;color:#fff;flex-shrink:0;">${a.name[0]}</div>
      <div style="flex:1;">
        <div style="font-weight:700;font-size:13px;">${a.name}</div>
        <div class="mono">@${a.username} | ${a.id}</div>
      </div>
      ${a.id !== 7362457858 ? `<button class="btn btn-danger btn-sm" onclick="removeAdmin(${a.id})">✕</button>` : '<span class="badge badge-purple">Owner</span>'}
    </div>
  `).join('');
}
function addAdmin() {
  const id   = parseInt(document.getElementById('newAdminId').value)||0;
  const name = document.getElementById('newAdminName').value.trim();
  const un   = document.getElementById('newAdminUsername').value.replace('@','').trim();
  if (!id || !name) { showAlert('ID va ism kiriting!', 'error'); return; }
  if (adminUsers.find(a => a.id === id)) { showAlert('Bu admin allaqachon bor!', 'error'); return; }
  adminUsers.push({ id, name, username:un||'—' });
  db.admin_ids.push(id);
  document.getElementById('newAdminId').value = '';
  document.getElementById('newAdminName').value = '';
  document.getElementById('newAdminUsername').value = '';
  renderAdmins();
  showAlert('✅ Admin qo\'shildi!', 'success');
}
function removeAdmin(id) {
  if (!confirm('Bu adminni o\'chirish?')) return;
  adminUsers = adminUsers.filter(a => a.id !== id);
  db.admin_ids = db.admin_ids.filter(x => x !== id);
  renderAdmins();
  showAlert('🗑 Admin o\'chirildi', 'success');
}

// ==================== ADS ====================
function renderAds() {
  if (!ads.length) {
    document.getElementById('adsList').innerHTML = `<div class="empty"><div class="empty-icon">📣</div>Reklama yo'q</div>`;
    return;
  }
  document.getElementById('adsList').innerHTML = ads.map(a => `
    <div style="padding:14px;background:var(--surface2);border-radius:10px;margin-bottom:10px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <span class="badge ${a.status==='approved'?'badge-green':'badge-yellow'}">${a.status==='approved'?'✅ Yuborildi':'⏳ Kutilmoqda'}</span>
        <span class="mono">${a.date}</span>
      </div>
      <div style="font-size:13px;white-space:pre-wrap;color:var(--text);">${a.text.length>120?a.text.slice(0,120)+'…':a.text}</div>
      ${a.status==='pending'?`<div style="margin-top:10px;display:flex;gap:6px;">
        <button class="btn btn-success btn-sm" onclick="approveAd('${a.id}')">✅ Tasdiqlash</button>
        <button class="btn btn-danger btn-sm" onclick="rejectAd('${a.id}')">❌ Rad</button>
      </div>`:''}
    </div>
  `).join('');
}
function createAd() {
  const text = document.getElementById('adText').value.trim();
  const status = document.getElementById('adStatus').value;
  if (!text) { showAlert('Matn kiriting!', 'error'); return; }
  const newId = 'ad' + Date.now();
  ads.unshift({ id:newId, text, status, from_name:'Admin', date:new Date().toISOString().slice(0,10) });
  document.getElementById('adText').value = '';
  renderAds();
  showAlert(status==='approved'?'📤 Reklama yuborildi!':'✅ Reklama yaratildi!', 'success');
}
function approveAd(id) {
  const a = ads.find(x => x.id === id);
  if (a) { a.status = 'approved'; renderAds(); showAlert('✅ Reklama tasdiqlandi!', 'success'); }
}
function rejectAd(id) {
  ads = ads.filter(x => x.id !== id);
  renderAds();
  showAlert('❌ Reklama rad etildi', 'error');
}

// ==================== ALERT ====================
function showAlert(msg, type='success') {
  const el = document.getElementById('alertBox');
  el.textContent = msg;
  el.className = 'alert show ' + type;
  setTimeout(() => el.classList.remove('show'), 3000);
}

// init login enter key
document.getElementById('loginInput').addEventListener('keydown', e => { if(e.key==='Enter') document.getElementById('passInput').focus(); });
</script>
</body>
</html>
