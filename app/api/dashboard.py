# ruff: noqa: E501
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from loguru import logger

from app.config import settings
from app.vectorstore.store import VectorStore

router = APIRouter()

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="fr" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kemi - Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        kemi: {
          50: '#eef2ff', 100: '#e0e7ff', 200: '#c7d2fe', 300: '#a5b4fc',
          400: '#818cf8', 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca',
          800: '#3730a3', 900: '#312e81',
        }
      }
    }
  }
}
</script>
<style>
  @keyframes fade-in { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  .fade-in { animation: fade-in 0.4s ease-out forwards; }
  .stat-card { animation: fade-in 0.4s ease-out forwards; }
  .stat-card:nth-child(2) { animation-delay: 0.1s; }
  .stat-card:nth-child(3) { animation-delay: 0.2s; }
  .stat-card:nth-child(4) { animation-delay: 0.3s; }
  .stat-card:nth-child(5) { animation-delay: 0.4s; }
  .skeleton { background: linear-gradient(90deg, #1e293b 25%, #334155 50%, #1e293b 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 0.5rem; }
  @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen font-sans antialiased">
<nav class="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-gradient-to-br from-kemi-400 to-kemi-600 rounded-lg flex items-center justify-center text-sm font-bold">K</div>
        <span class="text-lg font-semibold">Kemi Dashboard</span>
      </div>
      <div class="flex items-center gap-4 text-sm text-gray-400">
        <span id="lastUpdate"></span>
        <button onclick="refresh()" class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors flex items-center gap-1.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Refresh
        </button>
      </div>
    </div>
  </div>
</nav>

<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8" id="statsGrid">
    <div class="stat-card bg-gray-900 rounded-xl p-5 border border-gray-800">
      <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Status</div>
      <div id="statusBadge" class="skeleton h-7 w-24"></div>
    </div>
    <div class="stat-card bg-gray-900 rounded-xl p-5 border border-gray-800">
      <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Documents</div>
      <div id="docCount" class="skeleton h-8 w-20"></div>
    </div>
    <div class="stat-card bg-gray-900 rounded-xl p-5 border border-gray-800">
      <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Chunks</div>
      <div id="chunkCount" class="skeleton h-8 w-20"></div>
    </div>
    <div class="stat-card bg-gray-900 rounded-xl p-5 border border-gray-800">
      <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Base de donnees</div>
      <div id="dbStatus" class="skeleton h-8 w-20"></div>
    </div>
    <div class="stat-card bg-gray-900 rounded-xl p-5 border border-gray-800">
      <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">LLM</div>
      <div id="llmStatus" class="skeleton h-8 w-20"></div>
    </div>
  </div>

  <div class="bg-gray-900 rounded-xl border border-gray-800">
    <div class="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
      <h2 class="text-sm font-semibold uppercase tracking-wider text-gray-300">Documents indexes</h2>
      <span id="docCountBadge" class="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full"></span>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800">
            <th class="px-6 py-3 font-medium">Document</th>
            <th class="px-6 py-3 font-medium">SHA256</th>
            <th class="px-6 py-3 font-medium text-right">Chunks</th>
          </tr>
        </thead>
        <tbody id="docTableBody">
          <tr><td colspan="3" class="px-6 py-8 text-center text-gray-500">Chargement...</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</main>

<script>
async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function statusBadge(status) {
  if (status === 'ok') return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-900/50 text-emerald-400 border border-emerald-800"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>Online</span>';
  return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-900/50 text-amber-400 border border-amber-800"><span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>Degraded</span>';
}

function boolBadge(val, yes, no) {
  return val
    ? '<span class="text-emerald-400 font-medium">' + yes + '</span>'
    : '<span class="text-red-400 font-medium">' + no + '</span>';
}

function timeAgo(date) {
  const sec = Math.floor((new Date() - date) / 1000);
  if (sec < 60) return 'il y a ' + sec + 's';
  const min = Math.floor(sec / 60);
  if (min < 60) return 'il y a ' + min + 'min';
  const h = Math.floor(min / 60);
  return 'il y a ' + h + 'h';
}

async function refresh() {
  const now = new Date();
  document.getElementById('lastUpdate').textContent = timeAgo(now);

  try {
    const health = await fetchJSON('/health');
    document.getElementById('statusBadge').innerHTML = statusBadge(health.status);
    document.getElementById('docCount').innerHTML = '<span class="text-2xl font-bold text-white">' + health.documents_count + '</span>';
    document.getElementById('dbStatus').innerHTML = boolBadge(health.db, 'Connectee', 'Deconnectee');
    document.getElementById('llmStatus').innerHTML = boolBadge(health.llm, 'Configure', 'Manquant');
  } catch (e) {
    document.getElementById('statusBadge').innerHTML = '<span class="text-red-400">Erreur</span>';
  }

  try {
    const stats = await fetchJSON('/stats');
    document.getElementById('chunkCount').innerHTML = '<span class="text-2xl font-bold text-white">' + stats.chunks_count + '</span>';

    const tbody = document.getElementById('docTableBody');
    if (stats.documents.length === 0) {
      tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-8 text-center text-gray-500">Aucun document indexe</td></tr>';
    } else {
      tbody.innerHTML = stats.documents.map(doc => {
        const hash = doc.hash ? doc.hash.substring(0, 12) + '...' : '-';
        return '<tr class="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">'
          + '<td class="px-6 py-3 font-medium text-gray-200">' + escapeHtml(doc.name) + '</td>'
          + '<td class="px-6 py-3 text-gray-400 font-mono text-xs">' + hash + '</td>'
          + '<td class="px-6 py-3 text-right text-gray-300">' + doc.chunk_count + '</td>'
          + '</tr>';
      }).join('');
    }
    document.getElementById('docCountBadge').textContent = stats.documents.length + ' document' + (stats.documents.length > 1 ? 's' : '');
  } catch (e) {
    document.getElementById('chunkCount').innerHTML = '<span class="text-red-400">Erreur</span>';
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

refresh();
setInterval(refresh, 15000);
</script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard() -> HTMLResponse:
    return HTMLResponse(DASHBOARD_HTML)


@router.get("/stats")
async def stats() -> dict[str, Any]:
    vs = VectorStore()
    try:
        vs.initialize()
        docs_count = vs.count_documents()
        chunks_count = vs.count_chunks()
        documents = vs.get_documents()
        db_ok = True
    except Exception as e:
        logger.error("Stats DB failed: {e}", e=e)
        docs_count = 0
        chunks_count = 0
        documents = []
        db_ok = False

    return {
        "documents_count": docs_count,
        "chunks_count": chunks_count,
        "documents": documents,
        "db_ok": db_ok,
        "llm_ok": bool(settings.openrouter_api_key),
    }
