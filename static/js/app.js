// Prompt Archive (amkki) - Frontend Logic

let currentSuggestions = [];
let activeEntry = null;
let siteSettings = {};
let uploadQueue = [];
let currentUser = null; // { username: string, is_admin: boolean, is_following: boolean }
let authToken = sessionStorage.getItem("x_auth_token") || null;

// DOM Elements
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const clearSearchBtn = document.getElementById("clearSearchBtn");
const suggestBox = document.getElementById("suggestBox");
const suggestList = document.getElementById("suggestList");
const galleryGrid = document.getElementById("galleryGrid");
const resultCount = document.getElementById("resultCount");
const activeQueryBadge = document.getElementById("activeQueryBadge");
const emptyState = document.getElementById("emptyState");
const loadingState = document.getElementById("loadingState");
const popularTagsList = document.getElementById("popularTagsList");

// Header & Promo DOM
const headerXLink = document.getElementById("headerXLink");
const headerXText = document.getElementById("headerXText");
const promoBanner = document.getElementById("promoBanner");
const promoMainTitle = document.getElementById("promoMainTitle");
const modalPromoBox = document.getElementById("modalPromoBox");

// Tools Modal DOM
const toolsModal = document.getElementById("toolsModal");
const closeToolsModalBtn = document.getElementById("closeToolsModalBtn");
const closeToolsModalBottomBtn = document.getElementById("closeToolsModalBottomBtn");
const toolsListContainer = document.getElementById("toolsListContainer");

// Env Modal DOM
const openEnvBtn = document.getElementById("openEnvBtn");
const envModal = document.getElementById("envModal");
const closeEnvModalBtn = document.getElementById("closeEnvModalBtn");
const envContent = document.getElementById("envContent");

// X Auth DOM
const authBtn = document.getElementById("authBtn");
const authIcon = document.getElementById("authIcon");
const authBtnText = document.getElementById("authBtnText");
const xAuthModal = document.getElementById("xAuthModal");
const closeXAuthModalBtn = document.getElementById("closeXAuthModalBtn");
const xAuthUnlinkedView = document.getElementById("xAuthUnlinkedView");
const xAuthLinkedView = document.getElementById("xAuthLinkedView");
const linkedUsernameDisplay = document.getElementById("linkedUsernameDisplay");
const userLogoutBtn = document.getElementById("userLogoutBtn");
const closeLinkedModalBtn = document.getElementById("closeLinkedModalBtn");
const xAuthForm = document.getElementById("xAuthForm");
const xUsernameInput = document.getElementById("xUsernameInput");
const adminPasswordGroup = document.getElementById("adminPasswordGroup");
const adminPasswordInput = document.getElementById("adminPasswordInput");
const xAuthSubmitBtn = document.getElementById("xAuthSubmitBtn");
const xAuthSubmitText = document.getElementById("xAuthSubmitText");
const xAuthSubmitIcon = document.getElementById("xAuthSubmitIcon");
const followingCheck = document.getElementById("followingCheck");
const footerAdminBtn = document.getElementById("footerAdminBtn");

// Admin Panel DOM
const adminPanel = document.getElementById("adminPanel");
const closeAdminPanelBtn = document.getElementById("closeAdminPanelBtn");
const adminLogoutBtn = document.getElementById("adminLogoutBtn");
const adminSyncBtn = document.getElementById("adminSyncBtn");
const tabUploadBtn = document.getElementById("tabUploadBtn");
const tabToolsBtn = document.getElementById("tabToolsBtn");
const tabSettingsBtn = document.getElementById("tabSettingsBtn");
const tabUploadContent = document.getElementById("tabUploadContent");
const tabToolsContent = document.getElementById("tabToolsContent");
const tabSettingsContent = document.getElementById("tabSettingsContent");
const adminAddToolForm = document.getElementById("adminAddToolForm");
const adminToolsTable = document.getElementById("adminToolsTable");
const settingsForm = document.getElementById("settingsForm");
const changePasswordForm = document.getElementById("changePasswordForm");
const currentPasswordInput = document.getElementById("currentPasswordInput");
const newPasswordInput = document.getElementById("newPasswordInput");
const adminDeleteContainer = document.getElementById("adminDeleteContainer");

// Upload DOM
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const uploadQueueContainer = document.getElementById("uploadQueueContainer");
const queueCount = document.getElementById("queueCount");
const queueList = document.getElementById("queueList");
const clearQueueBtn = document.getElementById("clearQueueBtn");
const submitAllBtn = document.getElementById("submitAllBtn");
const uploadProgressBarContainer = document.getElementById("uploadProgressBarContainer");
const uploadProgressBar = document.getElementById("uploadProgressBar");

// Detail Modal DOM
const detailModal = document.getElementById("detailModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const modalImage = document.getElementById("modalImage");
const modalImageDownload = document.getElementById("modalImageDownload");
const modalFilename = document.getElementById("modalFilename");
const modalDate = document.getElementById("modalDate");
const modalPrompt = document.getElementById("modalPrompt");
const modalTags = document.getElementById("modalTags");
const socialLockerOverlay = document.getElementById("socialLockerOverlay");
const lockerFollowLink = document.getElementById("lockerFollowLink");
const lockerAuthTriggerBtn = document.getElementById("lockerAuthTriggerBtn");
const unlockedBadge = document.getElementById("unlockedBadge");
const copyActionContainer = document.getElementById("copyActionContainer");
const copyPromptBtn = document.getElementById("copyPromptBtn");
const copyPromptText = document.getElementById("copyPromptText");
const deleteEntryBtn = document.getElementById("deleteEntryBtn");

// --------------------------------------------------------------------------
// Initialization
// --------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", async () => {
  lucide.createIcons();
  await loadPublicSettings();
  await checkCurrentAuth();
  loadPopularTags();
  loadEntries("");

  setupSearchAndTabSuggest();
  setupAuthEvents();
  setupAdminPanel();
  setupUploadQueue();
  setupModals();
});

// Toast (Calm & Minimal)
function showToast(message) {
  const toast = document.getElementById("toast");
  const toastMsg = document.getElementById("toastMsg");
  toastMsg.textContent = message;
  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.remove("translate-y-3", "opacity-0");
    toast.classList.add("translate-y-0", "opacity-100");
  }, 10);
  setTimeout(() => {
    toast.classList.remove("translate-y-0", "opacity-100");
    toast.classList.add("translate-y-3", "opacity-0");
    setTimeout(() => toast.classList.add("hidden"), 200);
  }, 2200);
}

// --------------------------------------------------------------------------
// 1. Settings & Promo
// --------------------------------------------------------------------------
// --------------------------------------------------------------------------
// 1. Settings & Promo
// --------------------------------------------------------------------------
async function loadPublicSettings() {
  try {
    const res = await fetch("/api/settings/public");
    if (!res.ok) return;
    siteSettings = await res.json();

    if (siteSettings.x_username) {
      headerXLink.href = `https://x.com/${siteSettings.x_username}`;
      headerXText.textContent = `@${siteSettings.x_username}`;
      lockerFollowLink.href = `https://x.com/${siteSettings.x_username}`;
    }

    if (siteSettings.pixai_promo_enabled) {
      promoBanner.classList.remove("hidden");
      modalPromoBox.classList.remove("hidden");
      const mainText = siteSettings.promo_main_text || siteSettings.pixai_promo_badge || "便利な自動化ツールを公開中";
      if (promoMainTitle) promoMainTitle.textContent = mainText;
    } else {
      promoBanner.classList.add("hidden");
      modalPromoBox.classList.add("hidden");
    }

    envContent.textContent = siteSettings.environment_info || "(未設定)";
  } catch (err) {
    console.error(err);
  }
}

// --------------------------------------------------------------------------
// 1-2. Tools & Scripts Modal Logic (自作プログラム一覧)
// --------------------------------------------------------------------------
function openToolsModal() {
  if (!toolsModal) return;
  toolsModal.classList.remove("hidden");
  loadTools();
  lucide.createIcons();
}

function closeToolsModal() {
  if (!toolsModal) return;
  toolsModal.classList.add("hidden");
}

window.openToolsModal = openToolsModal;
window.closeToolsModal = closeToolsModal;

async function loadTools() {
  try {
    const res = await fetch("/api/tools");
    if (!res.ok) return;
    const tools = await res.json();
    renderToolsList(tools);
    if (currentUser?.is_admin) {
      renderAdminToolsTable(tools);
    }
  } catch (err) {
    console.error("Failed to load tools:", err);
  }
}

function renderToolsList(tools) {
  if (!toolsListContainer) return;
  toolsListContainer.innerHTML = "";
  if (!tools || tools.length === 0) {
    toolsListContainer.innerHTML = `
      <div class="p-6 text-center text-gray-500 font-mono text-xs">
        現在準備中のツールはありません。
      </div>
    `;
    return;
  }

  tools.forEach((tool) => {
    const card = document.createElement("div");
    card.className = "p-3.5 rounded-lg bg-gray-950/70 border border-gray-800/80 hover:border-gray-700/80 transition space-y-2";

    const isAdmin = currentUser && currentUser.is_admin;
    const isActive = tool.status === "active";
    const badgeText = tool.badge || (isActive ? "公開中" : "準備中");
    const badgeStyle = isActive
      ? "bg-blue-950/60 border-blue-800/60 text-blue-300"
      : "bg-gray-900 border-gray-800 text-gray-500";

    const tagsHtml = (tool.tags || []).map(t => `<span class="text-[10px] text-gray-500 font-mono">#${escapeHtml(t)}</span>`).join(" ");

    let actionBtnHtml = "";
    if (isActive && tool.url && tool.url !== "#") {
      actionBtnHtml = `
        <a href="${escapeHtml(tool.url)}" target="_blank" class="flex items-center gap-1 px-3 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-mono font-medium transition shadow-sm">
          <span>詳細・入手</span>
          <i data-lucide="arrow-up-right" class="w-3.5 h-3.5"></i>
        </a>
      `;
    } else {
      actionBtnHtml = `
        <span class="px-2.5 py-1 rounded bg-gray-900 border border-gray-800 text-gray-500 text-[11px] font-mono">
          近日公開
        </span>
      `;
    }

    const adminDeleteHtml = isAdmin ? `
      <button class="delete-tool-btn text-gray-500 hover:text-red-400 p-1 transition" data-id="${escapeHtml(tool.id)}" title="ツールを削除">
        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
      </button>
    ` : "";

    card.innerHTML = `
      <div class="flex items-start justify-between gap-2">
        <div class="flex items-center gap-2 flex-wrap">
          <h4 class="text-xs font-semibold text-gray-100 font-mono">${escapeHtml(tool.title)}</h4>
          <span class="px-1.5 py-0.5 rounded text-[10px] font-mono border ${badgeStyle}">
            ${escapeHtml(badgeText)}
          </span>
        </div>
        ${adminDeleteHtml}
      </div>
      <p class="text-[11px] text-gray-300 leading-relaxed font-sans">
        ${escapeHtml(tool.description)}
      </p>
      <div class="flex items-center justify-between pt-1 gap-2 flex-wrap">
        <div class="flex items-center gap-1.5 flex-wrap">
          ${tagsHtml}
        </div>
        <div>
          ${actionBtnHtml}
        </div>
      </div>
    `;

    // Admin Delete listener
    const delBtn = card.querySelector(".delete-tool-btn");
    if (delBtn) {
      delBtn.addEventListener("click", async () => {
        if (!confirm(`ツール「${tool.title}」を削除しますか？`)) return;
        await deleteTool(tool.id);
      });
    }

    toolsListContainer.appendChild(card);
  });

  lucide.createIcons();
}

function renderAdminToolsTable(tools) {
  if (!adminToolsTable) return;
  adminToolsTable.innerHTML = "";
  if (!tools || tools.length === 0) {
    adminToolsTable.innerHTML = '<p class="text-gray-500 text-xs">登録されているツールはありません</p>';
    return;
  }

  tools.forEach(tool => {
    const row = document.createElement("div");
    row.className = "flex items-center justify-between p-2 rounded bg-gray-900/60 border border-gray-800 text-xs font-mono";
    row.innerHTML = `
      <div class="flex items-center space-x-2">
        <span class="font-medium text-gray-300">${escapeHtml(tool.title)}</span>
        <span class="text-[10px] px-1.5 py-0.2 rounded border ${tool.status === 'active' ? 'border-blue-900 text-blue-400' : 'border-gray-800 text-gray-500'}">
          ${escapeHtml(tool.status)}
        </span>
      </div>
      <div class="flex items-center space-x-2">
        <button class="admin-del-tool text-gray-500 hover:text-red-400" data-id="${escapeHtml(tool.id)}">
          削除
        </button>
      </div>
    `;

    row.querySelector(".admin-del-tool").addEventListener("click", async () => {
      if (!confirm(`ツール「${tool.title}」を削除しますか？`)) return;
      await deleteTool(tool.id);
    });

    adminToolsTable.appendChild(row);
  });
}

async function deleteTool(toolId) {
  if (!authToken || !currentUser?.is_admin) return;
  try {
    const res = await fetch(`/api/tools/${toolId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) throw new Error("削除失敗");
    showToast("ツールを削除しました");
    await loadTools();
  } catch (err) {
    showToast("ツールの削除に失敗しました");
  }
}

// --------------------------------------------------------------------------
// 2. Search & Tab-key Suggestion Completion Logic
// --------------------------------------------------------------------------
function setupSearchAndTabSuggest() {
  let debounceTimer = null;

  searchInput.addEventListener("input", () => {
    const val = searchInput.value;
    clearSearchBtn.classList.toggle("hidden", val.length === 0);
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => fetchSuggestions(), 100);
  });

  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Tab") {
      if (currentSuggestions.length > 0) {
        e.preventDefault();
        applySuggestion(currentSuggestions[0]);
      }
    } else if (e.key === "Enter") {
      e.preventDefault();
      closeSuggestions();
      executeSearch();
    } else if (e.key === "Escape") {
      closeSuggestions();
    }
  });

  searchBtn.addEventListener("click", () => {
    closeSuggestions();
    executeSearch();
  });

  clearSearchBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearSearchBtn.classList.add("hidden");
    closeSuggestions();
    executeSearch();
  });

  document.addEventListener("click", (e) => {
    if (!searchInput.contains(e.target) && !suggestBox.contains(e.target)) {
      closeSuggestions();
    }
  });
}

function getCurrentToken() {
  const val = searchInput.value;
  const cursor = searchInput.selectionStart || val.length;
  const beforeCursor = val.slice(0, cursor);
  const parts = beforeCursor.split(",");
  return parts[parts.length - 1].trim();
}

async function fetchSuggestions() {
  const prefix = getCurrentToken();
  if (!prefix) {
    closeSuggestions();
    return;
  }

  try {
    const res = await fetch(`/api/tags/suggest?prefix=${encodeURIComponent(prefix)}&limit=8`);
    if (!res.ok) return;
    const data = await res.json();
    currentSuggestions = data.suggestions || [];
    if (currentSuggestions.length > 0) {
      renderSuggestions(currentSuggestions);
    } else {
      closeSuggestions();
    }
  } catch (err) {
    console.error(err);
  }
}

function renderSuggestions(suggestions) {
  suggestList.innerHTML = "";
  suggestions.forEach((tag, index) => {
    const item = document.createElement("div");
    item.className = "suggest-item px-3 py-1.5 hover:bg-gray-900 cursor-pointer flex items-center justify-between text-xs text-gray-300 font-mono transition";
    if (index === 0) item.classList.add("active");

    item.innerHTML = `
      <span>#${escapeHtml(tag)}</span>
      ${index === 0 ? '<span class="text-[10px] text-gray-500">[Tab]</span>' : ''}
    `;

    item.addEventListener("click", () => {
      applySuggestion(tag);
      searchInput.focus();
    });

    suggestList.appendChild(item);
  });
  suggestBox.classList.remove("hidden");
}

function applySuggestion(tag) {
  const val = searchInput.value;
  const cursor = searchInput.selectionStart || val.length;
  const beforeCursor = val.slice(0, cursor);
  const afterCursor = val.slice(cursor);
  const parts = beforeCursor.split(",");
  parts[parts.length - 1] = " " + tag;

  let newBefore = parts.join(",");
  if (newBefore.startsWith(" ,")) newBefore = newBefore.slice(2);
  else if (newBefore.startsWith(" ")) newBefore = newBefore.slice(1);

  searchInput.value = newBefore + ", " + afterCursor.trimStart();
  const newPos = newBefore.length + 2;
  searchInput.setSelectionRange(newPos, newPos);

  closeSuggestions();
}

function closeSuggestions() {
  suggestBox.classList.add("hidden");
  currentSuggestions = [];
}

function executeSearch() {
  loadEntries(searchInput.value.trim());
}

function resetSearch() {
  searchInput.value = "";
  clearSearchBtn.classList.add("hidden");
  closeSuggestions();
  loadEntries("");
}

// --------------------------------------------------------------------------
// 3. Gallery Loading & Rendering
// --------------------------------------------------------------------------
async function loadEntries(query = "") {
  loadingState.classList.remove("hidden");
  galleryGrid.innerHTML = "";
  emptyState.classList.add("hidden");

  if (query) {
    activeQueryBadge.textContent = `query: ${query}`;
    activeQueryBadge.classList.remove("hidden");
  } else {
    activeQueryBadge.classList.add("hidden");
  }

  try {
    const headers = {};
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;
    const res = await fetch(`/api/entries?q=${encodeURIComponent(query)}&limit=100`, { headers });
    if (!res.ok) throw new Error("取得失敗");
    const entries = await res.json();

    loadingState.classList.add("hidden");
    resultCount.textContent = entries.length;

    if (entries.length === 0) {
      emptyState.classList.remove("hidden");
      return;
    }

    renderGallery(entries);
  } catch (err) {
    loadingState.classList.add("hidden");
    console.error(err);
  }
}

function renderGallery(entries) {
  galleryGrid.innerHTML = "";
  const unlocked = isUnlocked();

  entries.forEach((entry) => {
    const card = document.createElement("div");
    card.className = "image-card group bg-gray-950 border border-gray-800/90 hover:border-gray-700/80 rounded-lg overflow-hidden cursor-pointer flex flex-col shadow-sm transition";

    const promptStatusHtml = unlocked
      ? `<div class="flex items-center gap-1 text-[10px] text-emerald-400/90 font-mono"><i data-lucide="unlock" class="w-3 h-3 text-emerald-500"></i><span>prompt unlocked</span></div>`
      : `<div class="flex items-center gap-1 text-[10px] text-gray-500 font-mono"><i data-lucide="lock" class="w-3 h-3 text-gray-600"></i><span>X連携でプロンプト表示</span></div>`;

    card.innerHTML = `
      <div class="relative w-full aspect-square bg-black/60 overflow-hidden flex items-center justify-center">
        <img
          src="/data/${entry.thumbnail_path}"
          alt="${escapeHtml(entry.filename)}"
          loading="lazy"
          class="w-full h-full object-cover group-hover:scale-102 transition-transform duration-200"
          onerror="this.src='/data/${entry.stored_path}'"
        >
      </div>
      <div class="p-2.5 flex-1 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          ${promptStatusHtml}
          <span class="text-[10px] text-gray-600 font-mono">${escapeHtml(entry.created_at || "")}</span>
        </div>
      </div>
    `;

    card.addEventListener("click", () => openDetailModal(entry));
    galleryGrid.appendChild(card);
  });

  lucide.createIcons();
}

// --------------------------------------------------------------------------
// 4. Detail Modal & Auth Locker
// --------------------------------------------------------------------------
function isUnlocked() {
  return currentUser !== null && (currentUser.is_admin || currentUser.is_following);
}

function openDetailModal(entry) {
  activeEntry = entry;
  modalImage.src = `/data/${entry.stored_path}`;
  modalImageDownload.href = `/data/${entry.stored_path}`;
  modalFilename.textContent = entry.filename;
  modalDate.textContent = entry.created_at;
  modalPrompt.textContent = entry.raw_prompt || "(prompt empty)";

  // Check Locker status
  if (isUnlocked()) {
    unlockPromptUI();
  } else {
    lockPromptUI();
  }

  // Admin delete action visibility
  adminDeleteContainer.classList.toggle("hidden", !(currentUser && currentUser.is_admin));

  // Tags are handled internally for search only (hidden from UI)
  if (modalTags) modalTags.innerHTML = "";

  detailModal.classList.remove("hidden");
  lucide.createIcons();
}

function unlockPromptUI() {
  modalPrompt.classList.remove("prompt-locked");
  socialLockerOverlay.classList.add("hidden");
  unlockedBadge.classList.remove("hidden");
  copyActionContainer.classList.remove("hidden");
}

function lockPromptUI() {
  modalPrompt.classList.add("prompt-locked");
  socialLockerOverlay.classList.remove("hidden");
  unlockedBadge.classList.add("hidden");
  copyActionContainer.classList.add("hidden");
}

function closeDetailModal() {
  detailModal.classList.add("hidden");
  activeEntry = null;
}

// --------------------------------------------------------------------------
// 5. X Authentication Logic (@amkki_aipix = Admin)
// --------------------------------------------------------------------------
async function checkCurrentAuth() {
  if (!authToken) {
    updateAuthUI(null);
    return;
  }

  try {
    const res = await fetch("/api/auth/me", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (res.ok) {
      const data = await res.json();
      if (data.authenticated) {
        currentUser = data;
        updateAuthUI(currentUser);
        return;
      }
    }
  } catch (err) {}

  authToken = null;
  currentUser = null;
  sessionStorage.removeItem("x_auth_token");
  updateAuthUI(null);
}

function updateAuthUI(user) {
  if (user) {
    if (user.is_admin) {
      authBtnText.textContent = `@${user.username} (Admin)`;
      authBtn.className = "flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-blue-900/60 bg-blue-950/40 hover:bg-blue-950/70 text-blue-300 transition font-mono shadow-sm";
      if (authIcon) authIcon.setAttribute("data-lucide", "shield");
    } else {
      authBtnText.textContent = `@${user.username}`;
      authBtn.className = "flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-emerald-900/60 bg-emerald-950/40 hover:bg-emerald-950/70 text-emerald-400 transition font-mono shadow-sm";
      if (authIcon) authIcon.setAttribute("data-lucide", "check-circle-2");
      adminPanel.classList.add("hidden");
    }
  } else {
    authBtnText.textContent = "プロンプト表示";
    authBtn.className = "flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-gray-800 bg-gray-900/90 hover:bg-gray-800 text-gray-300 transition font-mono shadow-sm";
    if (authIcon) authIcon.setAttribute("data-lucide", "lock");
    adminPanel.classList.add("hidden");
  }
  lucide.createIcons();
}

function checkAdminUsernameInput() {
  const val = xUsernameInput ? xUsernameInput.value.trim().replace(/^@/, "").toLowerCase() : "";
  if (val === "amkki_aipix") {
    if (adminPasswordGroup) adminPasswordGroup.classList.remove("hidden");
    if (xAuthSubmitText) xAuthSubmitText.textContent = "管理者としてログイン";
    if (xAuthSubmitIcon) xAuthSubmitIcon.setAttribute("data-lucide", "shield-check");
  } else {
    if (adminPasswordGroup) {
      adminPasswordGroup.classList.add("hidden");
      if (adminPasswordInput) adminPasswordInput.value = "";
    }
    if (xAuthSubmitText) xAuthSubmitText.textContent = "プロンプトを表示する";
    if (xAuthSubmitIcon) xAuthSubmitIcon.setAttribute("data-lucide", "unlock");
  }
  lucide.createIcons();
}

function openXAuthModal(forAdmin = false) {
  if (currentUser) {
    if (xAuthUnlinkedView) xAuthUnlinkedView.classList.add("hidden");
    if (xAuthLinkedView) xAuthLinkedView.classList.remove("hidden");
    if (linkedUsernameDisplay) {
      linkedUsernameDisplay.textContent = `@${currentUser.username}${currentUser.is_admin ? " (Admin)" : ""}`;
    }
  } else {
    if (xAuthUnlinkedView) xAuthUnlinkedView.classList.remove("hidden");
    if (xAuthLinkedView) xAuthLinkedView.classList.add("hidden");
    if (xUsernameInput) {
      if (forAdmin) {
        xUsernameInput.value = "amkki_aipix";
        checkAdminUsernameInput();
        if (adminPasswordInput) {
          setTimeout(() => adminPasswordInput.focus(), 60);
        }
      } else {
        xUsernameInput.value = "";
        checkAdminUsernameInput();
        setTimeout(() => xUsernameInput.focus(), 60);
      }
    }
  }
  xAuthModal.classList.remove("hidden");
  lucide.createIcons();
}

function closeXAuthModal() {
  xAuthModal.classList.add("hidden");
  if (xUsernameInput) xUsernameInput.value = "";
  if (adminPasswordInput) adminPasswordInput.value = "";
  checkAdminUsernameInput();
}

window.openXAuthModal = openXAuthModal;
window.closeXAuthModal = closeXAuthModal;

function setupAuthEvents() {
  // Real-time username input listener for admin detection
  if (xUsernameInput) {
    xUsernameInput.addEventListener("input", checkAdminUsernameInput);
  }

  // Top auth button
  authBtn.addEventListener("click", () => {
    if (currentUser && currentUser.is_admin) {
      // Toggle admin panel
      adminPanel.classList.toggle("hidden");
      if (!adminPanel.classList.contains("hidden")) {
        loadAdminSettingsForm();
      }
    } else {
      openXAuthModal(false);
    }
  });

  // Footer admin trigger
  if (footerAdminBtn) {
    footerAdminBtn.addEventListener("click", () => {
      if (currentUser && currentUser.is_admin) {
        adminPanel.classList.toggle("hidden");
        if (!adminPanel.classList.contains("hidden")) {
          loadAdminSettingsForm();
        }
      } else {
        openXAuthModal(true);
      }
    });
  }

  // Detail Modal Locker Trigger
  lockerAuthTriggerBtn.addEventListener("click", () => {
    openXAuthModal(false);
  });

  closeXAuthModalBtn.addEventListener("click", closeXAuthModal);
  if (closeLinkedModalBtn) {
    closeLinkedModalBtn.addEventListener("click", closeXAuthModal);
  }

  // General User Logout / Disconnect
  if (userLogoutBtn) {
    userLogoutBtn.addEventListener("click", async () => {
      try {
        await fetch("/api/auth/logout", {
          method: "POST",
          headers: { "Authorization": `Bearer ${authToken}` }
        });
      } catch (err) {}
      authToken = null;
      currentUser = null;
      sessionStorage.removeItem("x_auth_token");
      updateAuthUI(null);
      closeXAuthModal();
      showToast("連携を解除しました");
      loadEntries(searchInput.value.trim());
      if (activeEntry) {
        lockPromptUI();
      }
    });
  }

  // Submit X Auth Form (Secure password check for admin)
  xAuthForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = xUsernameInput.value.trim().replace(/^@/, "");
    if (!username) return;

    const isTargetAdmin = username.toLowerCase() === "amkki_aipix";
    const password = adminPasswordInput ? adminPasswordInput.value.trim() : "";

    if (isTargetAdmin && !password) {
      showToast("管理者パスワードを入力してください");
      if (adminPasswordInput) adminPasswordInput.focus();
      return;
    }

    try {
      const res = await fetch("/api/auth/x/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: username,
          following_confirmed: true,
          password: password || null
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "認証に失敗しました");
      }

      const data = await res.json();
      authToken = data.token;
      currentUser = {
        username: data.username,
        is_admin: data.is_admin,
        is_following: data.is_following
      };
      sessionStorage.setItem("x_auth_token", authToken);

      closeXAuthModal();
      xUsernameInput.value = "";
      if (adminPasswordInput) adminPasswordInput.value = "";
      checkAdminUsernameInput();
      updateAuthUI(currentUser);

      if (currentUser.is_admin) {
        adminPanel.classList.remove("hidden");
        loadAdminSettingsForm();
        showToast(`管理者として認証しました (@${currentUser.username})`);
      } else {
        showToast(`@${currentUser.username} として連携しました (プロンプト表示中)`);
      }

      // ギャラリー一覧を再読込してアンロック状態を反映
      loadEntries(searchInput.value.trim());

      // もし詳細モーダルが開いていたら、最新の平文プロンプトを再取得
      if (activeEntry) {
        try {
          const detailRes = await fetch(`/api/entries/${activeEntry.id}`, {
            headers: { "Authorization": `Bearer ${authToken}` }
          });
          if (detailRes.ok) {
            const updated = await detailRes.json();
            activeEntry = updated;
            modalPrompt.textContent = updated.raw_prompt || "(prompt empty)";
          }
        } catch (err) {}
        unlockPromptUI();
      }
    } catch (err) {
      showToast(err.message || "Xアカウント連携に失敗しました");
    }
  });

  // Change Admin Password Form
  if (changePasswordForm) {
    changePasswordForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!authToken || !currentUser?.is_admin) return;
      const curPass = currentPasswordInput ? currentPasswordInput.value.trim() : "";
      const newPass = newPasswordInput ? newPasswordInput.value.trim() : "";

      if (!curPass || !newPass) {
        showToast("パスワードを入力してください");
        return;
      }

      try {
        const res = await fetch("/api/auth/change-password", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${authToken}`
          },
          body: JSON.stringify({
            current_password: curPass,
            new_password: newPass
          })
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || "パスワード変更に失敗しました");
        }

        showToast("管理者パスワードを正常に変更しました");
        if (currentPasswordInput) currentPasswordInput.value = "";
        if (newPasswordInput) newPasswordInput.value = "";
      } catch (err) {
        showToast(err.message || "パスワード変更に失敗しました");
      }
    });
  }

  // Admin Logout
  adminLogoutBtn.addEventListener("click", async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: { "Authorization": `Bearer ${authToken}` }
      });
    } catch (err) {}
    authToken = null;
    currentUser = null;
    sessionStorage.removeItem("x_auth_token");
    updateAuthUI(null);
    showToast("ログアウトしました");
    loadEntries(searchInput.value.trim());
    if (activeEntry) {
      lockPromptUI();
    }
  });

  // Shortcut key: Shift + A for Admin toggle
  document.addEventListener("keydown", (e) => {
    if (e.shiftKey && (e.key === "A" || e.key === "a")) {
      const tag = document.activeElement ? document.activeElement.tagName : "";
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      e.preventDefault();
      if (currentUser && currentUser.is_admin) {
        adminPanel.classList.toggle("hidden");
        if (!adminPanel.classList.contains("hidden")) {
          loadAdminSettingsForm();
        }
      } else {
        openXAuthModal(true);
      }
    }
  });

  // Copy Prompt
  copyPromptBtn.addEventListener("click", () => {
    if (!activeEntry || !activeEntry.raw_prompt) return;
    navigator.clipboard.writeText(activeEntry.raw_prompt).then(() => {
      copyPromptText.textContent = "コピー完了";
      showToast("クリップボードにコピーしました");
      setTimeout(() => copyPromptText.textContent = "コピー", 1500);
    });
  });

  // Delete Image (Admin only)
  deleteEntryBtn.addEventListener("click", async () => {
    if (!activeEntry || !authToken || !currentUser?.is_admin) return;
    if (!confirm(`画像「${activeEntry.filename}」を削除しますか？`)) return;

    try {
      const res = await fetch(`/api/entries/${activeEntry.id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${authToken}` }
      });
      if (!res.ok) throw new Error("削除失敗");
      showToast("削除しました");
      closeDetailModal();
      loadEntries(searchInput.value.trim());
      loadPopularTags();
    } catch (err) {
      showToast("削除に失敗しました");
    }
  });
}

// --------------------------------------------------------------------------
// 6. Admin Panel Setup
// --------------------------------------------------------------------------
function setupAdminPanel() {
  closeAdminPanelBtn.addEventListener("click", () => {
    adminPanel.classList.add("hidden");
  });

  // Manual Sync from Personal Vault
  adminSyncBtn.addEventListener("click", async () => {
    if (!authToken || !currentUser?.is_admin) return;
    adminSyncBtn.disabled = true;
    showToast("個人Vaultから同期中...");

    try {
      const res = await fetch("/api/admin/sync", {
        method: "POST",
        headers: { "Authorization": `Bearer ${authToken}` }
      });
      const data = await res.json();
      if (data.status === "ok") {
        showToast(data.message || "同期完了");
        loadEntries(searchInput.value.trim());
        loadPopularTags();
      } else {
        showToast(data.message || "同期失敗");
      }
    } catch (err) {
      showToast("同期通信エラー");
    } finally {
      adminSyncBtn.disabled = false;
    }
  });

  // Tabs
  tabUploadBtn.addEventListener("click", () => {
    tabUploadBtn.classList.add("active");
    tabToolsBtn.classList.remove("active");
    tabSettingsBtn.classList.remove("active");
    tabUploadContent.classList.remove("hidden");
    tabToolsContent.classList.add("hidden");
    tabSettingsContent.classList.add("hidden");
  });

  tabToolsBtn.addEventListener("click", () => {
    tabToolsBtn.classList.add("active");
    tabUploadBtn.classList.remove("active");
    tabSettingsBtn.classList.remove("active");
    tabToolsContent.classList.remove("hidden");
    tabUploadContent.classList.add("hidden");
    tabSettingsContent.classList.add("hidden");
    loadTools();
  });

  tabSettingsBtn.addEventListener("click", () => {
    tabSettingsBtn.classList.add("active");
    tabUploadBtn.classList.remove("active");
    tabToolsBtn.classList.remove("active");
    tabSettingsContent.classList.remove("hidden");
    tabUploadContent.classList.add("hidden");
    tabToolsContent.classList.add("hidden");
    loadAdminSettingsForm();
  });

  // Admin Add Tool Form
  if (adminAddToolForm) {
    adminAddToolForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!authToken || !currentUser?.is_admin) return;

      const payload = {
        title: document.getElementById("adminNewToolTitle").value.trim(),
        badge: document.getElementById("adminNewToolBadge").value.trim(),
        description: document.getElementById("adminNewToolDesc").value.trim(),
        tags: document.getElementById("adminNewToolTags").value.trim(),
        url: document.getElementById("adminNewToolUrl").value.trim(),
        status: document.getElementById("adminNewToolStatus").value,
      };

      try {
        const res = await fetch("/api/tools", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${authToken}`
          },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("登録失敗");
        showToast("新しいツールを登録しました");
        adminAddToolForm.reset();
        await loadTools();
      } catch (err) {
        showToast("ツールの登録に失敗しました");
      }
    });
  }

  // Settings form
  settingsForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!authToken || !currentUser?.is_admin) return;

    const payload = {
      pixai_promo_enabled: document.getElementById("setPromoEnabled").value,
      promo_main_text: document.getElementById("setPromoMainText").value.trim(),
      pixai_promo_badge: document.getElementById("setPromoMainText").value.trim(),
      environment_info: document.getElementById("setEnvInfo").value,
    };

    try {
      const res = await fetch("/api/admin/settings", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${authToken}`
        },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("保存失敗");
      showToast("設定を保存しました");
      await loadPublicSettings();
    } catch (err) {
      showToast("設定保存に失敗しました");
    }
  });
}

async function loadAdminSettingsForm() {
  if (!authToken || !currentUser?.is_admin) return;
  try {
    const res = await fetch("/api/admin/settings", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("setPromoEnabled").value = data.pixai_promo_enabled || "1";
    document.getElementById("setPromoMainText").value = data.promo_main_text || data.pixai_promo_badge || "便利な自動化ツールを公開中";
    document.getElementById("setEnvInfo").value = data.environment_info || "";
  } catch (err) {}
}

// --------------------------------------------------------------------------
// 7. Admin Upload Queue Logic
// --------------------------------------------------------------------------
function setupUploadQueue() {
  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("border-gray-500");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("border-gray-500");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("border-gray-500");
    if (e.dataTransfer.files) handleFiles(Array.from(e.dataTransfer.files));
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
      fileInput.value = "";
    }
  });

  clearQueueBtn.addEventListener("click", () => {
    uploadQueue = [];
    renderQueue();
  });

  submitAllBtn.addEventListener("click", uploadAllQueue);
}

function handleFiles(files) {
  const images = files.filter(f => f.type.startsWith("image/"));
  if (images.length === 0) return;

  images.forEach(f => {
    uploadQueue.push({
      id: Math.random().toString(36).substring(2, 9),
      file: f,
      previewUrl: URL.createObjectURL(f),
      prompt: ""
    });
  });

  renderQueue();
}

function renderQueue() {
  queueCount.textContent = uploadQueue.length;
  if (uploadQueue.length === 0) {
    uploadQueueContainer.classList.add("hidden");
    queueList.innerHTML = "";
    return;
  }

  uploadQueueContainer.classList.remove("hidden");
  queueList.innerHTML = "";

  uploadQueue.forEach(item => {
    const row = document.createElement("div");
    row.className = "flex items-start gap-2 p-2 bg-gray-950 rounded border border-gray-800";
    row.innerHTML = `
      <img src="${item.previewUrl}" class="w-10 h-10 object-cover rounded border border-gray-800 flex-shrink-0">
      <div class="flex-1 min-w-0 space-y-1">
        <p class="text-[10px] text-gray-400 font-mono truncate">${escapeHtml(item.file.name)}</p>
        <textarea
          data-id="${item.id}"
          placeholder="prompt"
          class="queue-prompt w-full p-1 bg-black border border-gray-800 rounded text-xs font-mono text-gray-300 outline-none resize-y min-h-[36px]"
        >${escapeHtml(item.prompt)}</textarea>
      </div>
      <button data-del="${item.id}" class="p-1 text-gray-600 hover:text-red-400">
        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
      </button>
    `;

    row.querySelector(".queue-prompt").addEventListener("input", (e) => {
      item.prompt = e.target.value;
    });

    row.querySelector(`[data-del="${item.id}"]`).addEventListener("click", () => {
      URL.revokeObjectURL(item.previewUrl);
      uploadQueue = uploadQueue.filter(q => q.id !== item.id);
      renderQueue();
    });

    queueList.appendChild(row);
  });
  lucide.createIcons();
}

async function uploadAllQueue() {
  if (uploadQueue.length === 0 || !authToken || !currentUser?.is_admin) return;

  submitAllBtn.disabled = true;
  uploadProgressBarContainer.classList.remove("hidden");
  uploadProgressBar.style.width = "0%";

  const total = uploadQueue.length;
  let successCount = 0;

  for (let i = 0; i < total; i++) {
    const item = uploadQueue[i];
    const formData = new FormData();
    formData.append("file", item.file);
    formData.append("prompt", item.prompt);

    try {
      const res = await fetch("/api/entries", {
        method: "POST",
        headers: { "Authorization": `Bearer ${authToken}` },
        body: formData
      });
      if (res.ok) {
        successCount++;
        URL.revokeObjectURL(item.previewUrl);
      }
    } catch (err) {}

    uploadProgressBar.style.width = `${Math.round(((i + 1) / total) * 100)}%`;
  }

  submitAllBtn.disabled = false;
  uploadProgressBarContainer.classList.add("hidden");
  showToast(`${successCount} 件登録完了`);
  uploadQueue = [];
  renderQueue();

  loadEntries(searchInput.value.trim());
  loadPopularTags();
}

// --------------------------------------------------------------------------
// 8. Modals & Tag Examples (タグ例)
// --------------------------------------------------------------------------
function setupModals() {
  closeModalBtn.addEventListener("click", closeDetailModal);
  detailModal.addEventListener("click", (e) => {
    if (e.target === detailModal) closeDetailModal();
  });

  // Tools Modal Triggers
  if (promoBanner) {
    promoBanner.addEventListener("click", () => openToolsModal());
  }
  if (modalPromoBox) {
    modalPromoBox.addEventListener("click", () => openToolsModal());
  }
  if (closeToolsModalBtn) {
    closeToolsModalBtn.addEventListener("click", closeToolsModal);
  }
  if (closeToolsModalBottomBtn) {
    closeToolsModalBottomBtn.addEventListener("click", closeToolsModal);
  }
  if (toolsModal) {
    toolsModal.addEventListener("click", (e) => {
      if (e.target === toolsModal) closeToolsModal();
    });
  }

  openEnvBtn.addEventListener("click", () => envModal.classList.remove("hidden"));
  closeEnvModalBtn.addEventListener("click", () => envModal.classList.add("hidden"));
  envModal.addEventListener("click", (e) => {
    if (e.target === envModal) envModal.classList.add("hidden");
  });

  xAuthModal.addEventListener("click", (e) => {
    if (e.target === xAuthModal) xAuthModal.classList.add("hidden");
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeDetailModal();
      closeToolsModal();
      envModal.classList.add("hidden");
      xAuthModal.classList.add("hidden");
    }
  });
}

// タグ例 (Tag Examples)
async function loadPopularTags() {
  try {
    const res = await fetch("/api/tags/popular?limit=25");
    if (!res.ok) return;
    const tags = await res.json();
    popularTagsList.innerHTML = "";
    if (tags.length === 0) return;

    tags.forEach(t => {
      const chip = document.createElement("button");
      chip.className = "px-1.5 py-0.2 rounded bg-gray-900 hover:bg-gray-800 text-gray-400 hover:text-gray-200 border border-gray-800 transition font-mono text-[11px] flex items-center gap-1";
      chip.innerHTML = `<span>#${escapeHtml(t.name)}</span>`;
      chip.addEventListener("click", () => {
        searchInput.value = t.name + ", ";
        clearSearchBtn.classList.remove("hidden");
        searchInput.focus();
        executeSearch();
      });
      popularTagsList.appendChild(chip);
    });
  } catch (err) {}
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
