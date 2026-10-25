/**
 * AskSpace AI — Core Application Logic
 * Vanilla JavaScript (ES6+), Zero External Heavy Dependencies
 */

(function () {
    'use strict';

    // --- State Management ---
    const state = {
        activeConversationId: null,
        activeCategory: 'All',
        isSubmitting: false,
        conversations: [],
        notebookEntries: [],
        theme: document.documentElement.getAttribute('data-theme') || 'dark',
    };

    // --- DOM Elements Cache ---
    const elements = {
        // Layout & Navigation
        appLayout: document.getElementById('appLayout'),
        sidebar: document.getElementById('sidebar'),
        sidebarOverlay: document.getElementById('sidebarOverlay'),
        mobileMenuBtn: document.getElementById('mobileMenuBtn'),
        sidebarCloseBtn: document.getElementById('sidebarCloseBtn'),
        themeToggleBtn: document.getElementById('themeToggleBtn'),
        
        // Sidebar Content
        conversationsList: document.getElementById('conversationsList'),
        convCountBadge: document.getElementById('convCountBadge'),
        conversationSearchInput: document.getElementById('conversationSearchInput'),
        clearSearchBtn: document.getElementById('clearSearchBtn'),
        categoryPills: document.querySelectorAll('.category-pill'),
        btnNewChat: document.getElementById('btnNewChat'),
        notebookBadge: document.getElementById('notebookBadge'),

        // Topbar
        topbarTitle: document.getElementById('topbarTitle'),
        topbarCategoryBadge: document.getElementById('topbarCategoryBadge'),
        topbarNewChatBtn: document.getElementById('topbarNewChatBtn'),

        // Chat View
        chatWorkspace: document.getElementById('chatWorkspace'),
        chatMessagesContainer: document.getElementById('chatMessagesContainer'),
        welcomeScreen: document.getElementById('welcomeScreen'),
        messagesList: document.getElementById('messagesList'),
        typingIndicator: document.getElementById('typingIndicator'),
        chatComposerForm: document.getElementById('chatComposerForm'),
        messageInput: document.getElementById('messageInput'),
        btnSendMessage: document.getElementById('btnSendMessage'),
        messageCategorySelect: document.getElementById('messageCategorySelect'),
        charCounter: document.getElementById('charCounter'),
        promptCards: document.querySelectorAll('.prompt-card'),

        // Notebook View
        notebookWorkspace: document.getElementById('notebookWorkspace'),
        notebookSearchInput: document.getElementById('notebookSearchInput'),
        clearNotebookSearchBtn: document.getElementById('clearNotebookSearchBtn'),
        notebookTabs: document.querySelectorAll('.notebook-tab'),
        notesGrid: document.getElementById('notesGrid'),
        notebookEmptyState: document.getElementById('notebookEmptyState'),

        // Settings View
        settingsWorkspace: document.getElementById('settingsWorkspace'),
        themeChoiceDark: document.getElementById('themeChoiceDark'),
        themeChoiceLight: document.getElementById('themeChoiceLight'),
        settingToneSelect: document.getElementById('settingToneSelect'),
        statConversations: document.getElementById('statConversations'),
        statMessages: document.getElementById('statMessages'),
        statNotes: document.getElementById('statNotes'),

        // Modal & Toast
        genericModal: document.getElementById('genericModal'),
        modalTitle: document.getElementById('modalTitle'),
        modalBody: document.getElementById('modalBody'),
        modalCloseBtn: document.getElementById('modalCloseBtn'),
        modalCancelBtn: document.getElementById('modalCancelBtn'),
        modalConfirmBtn: document.getElementById('modalConfirmBtn'),
        toastContainer: document.getElementById('toastContainer')
    };

    // =========================================================================
    // Markdown Parser & HTML Escaping
    // =========================================================================
    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function renderMarkdown(rawText) {
        if (!rawText) return '';

        // Extract fenced code blocks first to protect code contents
        const codeBlocks = [];
        let text = rawText.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, function (_, lang, code) {
            const index = codeBlocks.length;
            const language = (lang || 'code').trim();
            codeBlocks.push({
                language: language,
                code: escapeHtml(code.trim())
            });
            return `__CODE_BLOCK_${index}__`;
        });

        // Split into lines for block processing
        const lines = text.split('\n');
        const output = [];
        let inList = false;
        let listType = 'ul';

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];

            // Code block placeholder
            if (line.trim().startsWith('__CODE_BLOCK_') && line.trim().endsWith('__')) {
                if (inList) { output.push(`</${listType}>`); inList = false; }
                const blockIdx = parseInt(line.trim().replace('__CODE_BLOCK_', '').replace('__', ''), 10);
                const block = codeBlocks[blockIdx];
                if (block) {
                    output.push(`
                        <div class="code-block-wrapper">
                            <div class="code-block-header">
                                <span>${block.language}</span>
                                <button class="btn-copy-code" type="button" aria-label="Copy code snippet">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                    <span>Copy</span>
                                </button>
                            </div>
                            <pre><code>${block.code}</code></pre>
                        </div>
                    `);
                }
                continue;
            }

            // GitHub Alert syntax: > [!NOTE] or > [!TIP]
            if (/^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]/i.test(line)) {
                if (inList) { output.push(`</${listType}>`); inList = false; }
                const type = line.match(/^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]/i)[1].toUpperCase();
                output.push(`<blockquote class="alert-box alert-${type.toLowerCase()}"><strong>${type}:</strong> `);
                continue;
            }

            // Normal Blockquote: > text
            if (line.startsWith('> ')) {
                if (inList) { output.push(`</${listType}>`); inList = false; }
                output.push(`<blockquote>${formatInline(line.substring(2))}</blockquote>`);
                continue;
            }

            // Headers
            if (/^#{1,4}\s+/.test(line)) {
                if (inList) { output.push(`</${listType}>`); inList = false; }
                if (line.startsWith('#### ')) {
                    output.push(`<h4>${formatInline(line.substring(5))}</h4>`);
                } else if (line.startsWith('### ')) {
                    output.push(`<h3>${formatInline(line.substring(4))}</h3>`);
                } else if (line.startsWith('## ')) {
                    output.push(`<h2>${formatInline(line.substring(3))}</h2>`);
                } else if (line.startsWith('# ')) {
                    output.push(`<h1>${formatInline(line.substring(2))}</h1>`);
                }
                continue;
            }

            // Unordered list: - item or * item
            if (/^[-*]\s+/.test(line)) {
                if (!inList || listType !== 'ul') {
                    if (inList) output.push(`</${listType}>`);
                    output.push('<ul>');
                    inList = true;
                    listType = 'ul';
                }
                let rawItem = line.replace(/^[-*]\s+/, '');
                if (rawItem.startsWith('[ ] ')) {
                    output.push(`<li style="list-style:none;"><input type="checkbox" disabled style="margin-right:6px;">${formatInline(rawItem.substring(4))}</li>`);
                } else if (rawItem.startsWith('[x] ') || rawItem.startsWith('[X] ')) {
                    output.push(`<li style="list-style:none;"><input type="checkbox" checked disabled style="margin-right:6px;">${formatInline(rawItem.substring(4))}</li>`);
                } else {
                    output.push(`<li>${formatInline(rawItem)}</li>`);
                }
                continue;
            }

            // Ordered list: 1. item
            if (/^\d+\.\s+/.test(line)) {
                if (!inList || listType !== 'ol') {
                    if (inList) output.push(`</${listType}>`);
                    output.push('<ol>');
                    inList = true;
                    listType = 'ol';
                }
                output.push(`<li>${formatInline(line.replace(/^\d+\.\s+/, ''))}</li>`);
                continue;
            }

            // End list if standard paragraph encountered
            if (inList) {
                output.push(`</${listType}>`);
                inList = false;
            }

            // Table rows: | col 1 | col 2 |
            if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
                // If header separator line like | :--- | :--- |, skip
                if (/^\|(\s*:?-+:?\s*\|)+$/.test(line.trim())) {
                    continue;
                }
                const cells = line.split('|').slice(1, -1).map(c => c.trim());
                const isHeader = (i === 0 || (lines[i - 1] && lines[i - 1].trim() === ''));
                const tag = isHeader ? 'th' : 'td';
                const cellHtml = cells.map(c => `<${tag}>${formatInline(c)}</${tag}>`).join('');
                output.push(`<table><tr>${cellHtml}</tr></table>`);
                continue;
            }

            // Empty line
            if (line.trim() === '') {
                continue;
            }

            // Normal paragraph
            output.push(`<p>${formatInline(line)}</p>`);
        }

        if (inList) {
            output.push(`</${listType}>`);
        }

        return output.join('\n');
    }

    function formatInline(text) {
        if (!text) return '';
        let escaped = escapeHtml(text);

        // Inline code: `code`
        escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Bold: **text**
        escaped = escaped.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

        // Italic: *text* or _text_
        escaped = escaped.replace(/(^|[^*])\*([^*]+)\*([^*]|$)/g, '$1<em>$2</em>$3');

        // Strikethrough: ~~text~~
        escaped = escaped.replace(/~~([^~]+)~~/g, '<del>$1</del>');

        // Links: [text](https://...)
        escaped = escaped.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:var(--accent-violet); text-decoration:underline;">$1</a>');

        // Math inline: $O(log n)$
        escaped = escaped.replace(/\$([^$]+)\$/g, '<code class="math-inline">$1</code>');

        return escaped;
    }

    // =========================================================================
    // UI Helpers: Modals & Toasts
    // =========================================================================
    function showToast(message, type = 'info', duration = 3200) {
        if (!elements.toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.setAttribute('role', 'alert');

        let iconSvg = '';
        if (type === 'success') {
            iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
        } else if (type === 'error') {
            iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
        } else {
            iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
        }

        toast.innerHTML = `${iconSvg}<span>${escapeHtml(message)}</span>`;
        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(8px)';
            toast.style.transition = 'all 200ms ease';
            setTimeout(() => toast.remove(), 220);
        }, duration);
    }

    function showModal({ title, body, confirmText = 'Confirm', confirmStyle = 'primary', onConfirm }) {
        if (!elements.genericModal) return;

        elements.modalTitle.textContent = title;
        elements.modalBody.innerHTML = typeof body === 'string' ? body : '';
        elements.modalConfirmBtn.textContent = confirmText;
        elements.modalConfirmBtn.className = `btn btn-${confirmStyle}`;

        elements.genericModal.style.display = 'flex';

        const handleConfirm = () => {
            closeModal();
            if (typeof onConfirm === 'function') onConfirm();
        };

        const closeModal = () => {
            elements.genericModal.style.display = 'none';
            elements.modalConfirmBtn.removeEventListener('click', handleConfirm);
            elements.modalCancelBtn.removeEventListener('click', closeModal);
            elements.modalCloseBtn.removeEventListener('click', closeModal);
        };

        elements.modalConfirmBtn.addEventListener('click', handleConfirm);
        elements.modalCancelBtn.addEventListener('click', closeModal);
        elements.modalCloseBtn.addEventListener('click', closeModal);
    }

    // =========================================================================
    // Theme Management
    // =========================================================================
    function setTheme(newTheme) {
        state.theme = newTheme;
        document.documentElement.setAttribute('data-theme', newTheme);
        document.body.className = `theme-${newTheme}`;
        localStorage.setItem('askspace_theme', newTheme);

        // Update settings page choices if present
        if (elements.themeChoiceDark && elements.themeChoiceLight) {
            elements.themeChoiceDark.classList.toggle('active', newTheme === 'dark');
            elements.themeChoiceLight.classList.toggle('active', newTheme === 'light');
        }

        // Persist to server
        fetch('/api/preferences', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theme: newTheme })
        }).catch(() => {});
    }

    function toggleTheme() {
        const next = state.theme === 'dark' ? 'light' : 'dark';
        setTheme(next);
        showToast(`Switched to ${next} theme`, 'info', 1800);
    }

    // =========================================================================
    // Conversations API & Sidebar Management
    // =========================================================================
    async function loadConversations(category = state.activeCategory, search = '') {
        try {
            let url = '/api/conversations?';
            if (category && category !== 'All') url += `category=${encodeURIComponent(category)}&`;
            if (search) url += `search=${encodeURIComponent(search)}&`;

            const res = await fetch(url);
            const data = await res.json();

            if (data.success) {
                state.conversations = data.data || [];
                renderConversationsList();
            }
        } catch (err) {
            console.error('Failed to load conversations:', err);
        }
    }

    function renderConversationsList() {
        if (!elements.conversationsList) return;

        if (elements.convCountBadge) {
            elements.convCountBadge.textContent = state.conversations.length;
        }

        if (state.conversations.length === 0) {
            elements.conversationsList.innerHTML = `
                <div style="padding: 16px 8px; text-align: center; color: var(--text-muted); font-size: 0.8rem;">
                    No conversations found.
                </div>
            `;
            return;
        }

        elements.conversationsList.innerHTML = '';
        state.conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = `conv-item ${state.activeConversationId === conv.id ? 'active' : ''}`;
            item.setAttribute('data-id', conv.id);
            item.setAttribute('role', 'button');
            item.setAttribute('tabindex', '0');

            item.innerHTML = `
                <div class="conv-item-left" title="${escapeHtml(conv.title)}">
                    <svg class="conv-item-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <span class="conv-item-title">${escapeHtml(conv.title)}</span>
                </div>
                <div class="conv-actions">
                    <button class="conv-action-btn edit-btn" title="Rename conversation" aria-label="Rename conversation">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button class="conv-action-btn delete-btn" title="Delete conversation" aria-label="Delete conversation">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
            `;

            // Open conversation
            item.addEventListener('click', (e) => {
                if (e.target.closest('.conv-actions')) return;
                openConversation(conv.id);
            });

            // Rename button
            const editBtn = item.querySelector('.edit-btn');
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                promptRenameConversation(conv);
            });

            // Delete button
            const deleteBtn = item.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                confirmDeleteConversation(conv);
            });

            elements.conversationsList.appendChild(item);
        });
    }

    async function openConversation(convId) {
        // If not on chat page, navigate to home with query param
        if (!elements.chatWorkspace) {
            window.location.href = `/?conv=${convId}`;
            return;
        }

        try {
            const res = await fetch(`/api/conversations/${convId}`);
            const data = await res.json();

            if (!data.success) {
                showToast(data.error || 'Failed to load conversation', 'error');
                return;
            }

            const conv = data.data;
            state.activeConversationId = conv.id;

            // Update topbar
            if (elements.topbarTitle) elements.topbarTitle.textContent = conv.title;
            if (elements.topbarCategoryBadge) {
                elements.topbarCategoryBadge.textContent = conv.category;
                elements.topbarCategoryBadge.style.display = 'inline-block';
            }
            if (elements.messageCategorySelect) {
                elements.messageCategorySelect.value = conv.category;
            }

            // Render messages
            renderMessages(conv.messages || []);

            // Update active state in sidebar
            renderConversationsList();

            // Show export conversation button
            const exportBtn = document.getElementById('btnExportChat');
            if (exportBtn) exportBtn.style.display = 'inline-flex';

            // Close mobile sidebar if open
            closeSidebar();

        } catch (err) {
            console.error('Error opening conversation:', err);
            showToast('Network error while opening conversation.', 'error');
        }
    }

    function promptRenameConversation(conv) {
        const inputId = 'renameConvInput';
        showModal({
            title: 'Rename Conversation',
            body: `
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <label for="${inputId}" style="font-size:0.85rem; color:var(--text-secondary);">Enter a new title:</label>
                    <input type="text" id="${inputId}" value="${escapeHtml(conv.title)}" maxlength="120" 
                           style="width:100%; padding:8px 10px; background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:6px; color:var(--text-primary); outline:none;">
                </div>
            `,
            confirmText: 'Save Title',
            confirmStyle: 'primary',
            onConfirm: async () => {
                const input = document.getElementById(inputId);
                const newTitle = input ? input.value.trim() : '';
                if (!newTitle) return;

                try {
                    const res = await fetch(`/api/conversations/${conv.id}`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title: newTitle })
                    });
                    const result = await res.json();
                    if (result.success) {
                        showToast('Conversation renamed', 'success');
                        if (state.activeConversationId === conv.id && elements.topbarTitle) {
                            elements.topbarTitle.textContent = newTitle;
                        }
                        loadConversations();
                    } else {
                        showToast(result.error || 'Rename failed', 'error');
                    }
                } catch (err) {
                    showToast('Network error during rename', 'error');
                }
            }
        });

        // Auto-focus input
        setTimeout(() => {
            const input = document.getElementById(inputId);
            if (input) { input.focus(); input.select(); }
        }, 100);
    }

    function confirmDeleteConversation(conv) {
        showModal({
            title: 'Delete Conversation?',
            body: `Are you sure you want to delete <strong>"${escapeHtml(conv.title)}"</strong>? All messages in this conversation will be permanently removed.`,
            confirmText: 'Delete',
            confirmStyle: 'danger',
            onConfirm: async () => {
                try {
                    const res = await fetch(`/api/conversations/${conv.id}`, { method: 'DELETE' });
                    const result = await res.json();
                    if (result.success) {
                        showToast('Conversation deleted', 'success');
                        if (state.activeConversationId === conv.id) {
                            resetToNewChat();
                        }
                        loadConversations();
                    } else {
                        showToast(result.error || 'Delete failed', 'error');
                    }
                } catch (err) {
                    showToast('Network error during deletion', 'error');
                }
            }
        });
    }

    function resetToNewChat() {
        state.activeConversationId = null;
        if (elements.topbarTitle) elements.topbarTitle.textContent = 'New Chat';
        if (elements.topbarCategoryBadge) elements.topbarCategoryBadge.style.display = 'none';
        const exportBtn = document.getElementById('btnExportChat');
        if (exportBtn) exportBtn.style.display = 'none';
        if (elements.messagesList) {
            elements.messagesList.innerHTML = '';
            elements.messagesList.style.display = 'none';
        }
        if (elements.welcomeScreen) {
            elements.welcomeScreen.style.display = 'flex';
        }
        if (elements.messageInput) {
            elements.messageInput.value = '';
            elements.messageInput.focus();
        }
        updateCharCounter();
        renderConversationsList();
    }

    // =========================================================================
    // Chat Message Rendering & Dispatch
    // =========================================================================
    function renderMessages(messages) {
        if (!elements.messagesList || !elements.welcomeScreen) return;

        if (!messages || messages.length === 0) {
            elements.messagesList.style.display = 'none';
            elements.welcomeScreen.style.display = 'flex';
            return;
        }

        elements.welcomeScreen.style.display = 'none';
        elements.messagesList.style.display = 'flex';
        elements.messagesList.innerHTML = '';

        messages.forEach(msg => {
            appendMessageToDOM(msg, false);
        });

        scrollToBottom();
    }

    function appendMessageToDOM(msg, shouldScroll = true) {
        if (!elements.messagesList) return;

        const isUser = msg.role === 'user';
        const item = document.createElement('div');
        item.className = `message-item ${isUser ? 'user-message' : 'assistant-message'}`;
        item.setAttribute('data-msg-id', msg.id || '');

        const formattedTime = msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Just now';

        if (isUser) {
            item.innerHTML = `
                <div class="msg-body-wrap">
                    <div class="msg-bubble">${escapeHtml(msg.content)}</div>
                    <div class="msg-meta-row">
                        <span class="msg-time">${formattedTime}</span>
                    </div>
                </div>
                <div class="msg-avatar user-avatar-tag">You</div>
            `;
        } else {
            const formattedContent = renderMarkdown(msg.content);
            item.innerHTML = `
                <div class="msg-avatar assistant-avatar" title="AskSpace AI">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                    </svg>
                </div>
                <div class="msg-body-wrap">
                    <div class="msg-bubble">${formattedContent}</div>
                    <div class="msg-meta-row">
                        <span class="msg-time">${formattedTime}</span>
                        <div class="msg-actions">
                            <button class="msg-btn btn-copy-msg" type="button" title="Copy response to clipboard">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                <span>Copy</span>
                            </button>
                            <button class="msg-btn btn-save-note" type="button" title="Save this answer to Personal Notebook">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
                                <span>Save to Notebook</span>
                            </button>
                            <button class="msg-btn btn-read-aloud" type="button" title="Listen to response (Speech Synthesis)">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
                                <span>Listen</span>
                            </button>
                            <button class="msg-btn btn-regenerate-msg" type="button" title="Regenerate answer">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
                                <span>Regenerate</span>
                            </button>
                        </div>
                    </div>
                </div>
            `;

            // Attach Copy Action
            const copyBtn = item.querySelector('.btn-copy-msg');
            copyBtn.addEventListener('click', () => {
                navigator.clipboard.writeText(msg.content).then(() => {
                    copyBtn.innerHTML = `
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
                        <span style="color:#10b981;">Copied!</span>
                    `;
                    showToast('Response copied to clipboard', 'success', 2000);
                    setTimeout(() => {
                        copyBtn.innerHTML = `
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            <span>Copy</span>
                        `;
                    }, 2200);
                }).catch(() => showToast('Failed to copy', 'error'));
            });

            // Attach Save to Notebook Action
            const saveBtn = item.querySelector('.btn-save-note');
            saveBtn.addEventListener('click', () => {
                promptSaveToNotebook(msg);
            });

            // Attach Regenerate Action
            const regenBtn = item.querySelector('.btn-regenerate-msg');
            if (regenBtn) {
                regenBtn.addEventListener('click', () => {
                    const allUserMsgs = elements.messagesList.querySelectorAll('.user-message .msg-bubble');
                    if (allUserMsgs.length > 0) {
                        const lastUserPrompt = allUserMsgs[allUserMsgs.length - 1].innerText.trim();
                        showToast('Regenerating response...', 'info', 1800);
                        sendChatMessage(lastUserPrompt);
                    }
                });
            }

            // Attach Read Aloud Action (Web Speech Synthesis)
            const readBtn = item.querySelector('.btn-read-aloud');
            if (readBtn && 'speechSynthesis' in window) {
                readBtn.addEventListener('click', () => {
                    if (window.speechSynthesis.speaking) {
                        window.speechSynthesis.cancel();
                        readBtn.querySelector('span').textContent = 'Listen';
                        showToast('Speech stopped', 'info', 1500);
                        return;
                    }

                    const speechText = msg.content.replace(/[#*`_~>\-+=]/g, ' ').replace(/```[\s\S]*?```/g, 'Code block omitted.');
                    const utterance = new SpeechSynthesisUtterance(speechText);
                    utterance.rate = 1.0;

                    utterance.onstart = () => {
                        readBtn.querySelector('span').textContent = 'Stop';
                        readBtn.style.color = 'var(--accent-violet)';
                    };

                    utterance.onend = utterance.onerror = () => {
                        readBtn.querySelector('span').textContent = 'Listen';
                        readBtn.style.color = '';
                    };

                    window.speechSynthesis.speak(utterance);
                    showToast('Reading response aloud...', 'info', 2000);
                });
            }

            // Attach Code Block Copy Buttons
            item.querySelectorAll('.btn-copy-code').forEach(codeBtn => {
                codeBtn.addEventListener('click', () => {
                    const codeEl = codeBtn.closest('.code-block-wrapper').querySelector('code');
                    if (codeEl) {
                        navigator.clipboard.writeText(codeEl.innerText).then(() => {
                            codeBtn.innerHTML = `<span>Copied!</span>`;
                            setTimeout(() => {
                                codeBtn.innerHTML = `
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                    <span>Copy</span>
                                `;
                            }, 2000);
                        });
                    }
                });
            });
        }

        elements.messagesList.appendChild(item);
        if (shouldScroll) scrollToBottom();
    }

    async function sendChatMessage(promptText, category) {
        const text = (promptText || (elements.messageInput ? elements.messageInput.value : '')).trim();
        if (!text || state.isSubmitting) return;

        const cat = category || (elements.messageCategorySelect ? elements.messageCategorySelect.value : 'General');

        // Switch view to messages list
        if (elements.welcomeScreen) elements.welcomeScreen.style.display = 'none';
        if (elements.messagesList) elements.messagesList.style.display = 'flex';

        // Clear input and reset height
        if (elements.messageInput) {
            elements.messageInput.value = '';
            elements.messageInput.style.height = 'auto';
        }
        updateCharCounter();

        // Append user message immediately
        const tempUserMsg = {
            role: 'user',
            content: text,
            created_at: new Date().toISOString()
        };
        appendMessageToDOM(tempUserMsg, true);

        // Lock UI & show typing indicator
        setSubmittingState(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    conversation_id: state.activeConversationId,
                    category: cat
                })
            });

            const result = await res.json();

            if (!result.success) {
                showToast(result.error || 'Failed to process message', 'error');
                appendMessageToDOM({
                    role: 'assistant',
                    content: `### Request Failed\n\n${result.error || 'The server encountered an error while processing your request.'}\n\nPlease try again.`,
                    created_at: new Date().toISOString()
                }, true);
                return;
            }

            const data = result.data;
            state.activeConversationId = data.conversation_id;

            // Update topbar title & badge
            if (elements.topbarTitle) elements.topbarTitle.textContent = data.conversation_title;
            if (elements.topbarCategoryBadge) {
                elements.topbarCategoryBadge.textContent = data.category;
                elements.topbarCategoryBadge.style.display = 'inline-block';
            }

            // Append assistant reply
            appendMessageToDOM(data.assistant_message, true);

            // Refresh conversations list in sidebar
            loadConversations();

        } catch (err) {
            console.error('Chat error:', err);
            showToast('Network error while sending message', 'error');
            appendMessageToDOM({
                role: 'assistant',
                content: "### Connection Error\n\nCould not reach the AskSpace AI service. Please verify that the local server is running.",
                created_at: new Date().toISOString()
            }, true);
        } finally {
            setSubmittingState(false);
            if (elements.messageInput) elements.messageInput.focus();
        }
    }

    function setSubmittingState(submitting) {
        state.isSubmitting = submitting;
        if (elements.btnSendMessage) elements.btnSendMessage.disabled = submitting;
        if (elements.typingIndicator) {
            elements.typingIndicator.style.display = submitting ? 'flex' : 'none';
            if (submitting) scrollToBottom();
        }
    }

    function scrollToBottom() {
        if (!elements.chatMessagesContainer) return;
        requestAnimationFrame(() => {
            elements.chatMessagesContainer.scrollTop = elements.chatMessagesContainer.scrollHeight;
        });
    }

    function updateCharCounter() {
        if (!elements.charCounter || !elements.messageInput) return;
        const len = elements.messageInput.value.length;
        elements.charCounter.textContent = `${len.toLocaleString()} / 8,000`;
        if (elements.btnSendMessage) {
            elements.btnSendMessage.disabled = len === 0 || state.isSubmitting;
        }
    }

    // =========================================================================
    // Notebook Management
    // =========================================================================
    function promptSaveToNotebook(msg) {
        // Derive clean initial title from content
        const firstLine = msg.content.split('\n')[0].replace(/^[#*`_\s]+/, '').trim();
        const initialTitle = firstLine ? firstLine.slice(0, 60) : 'Saved Insight';

        const titleInputId = 'noteTitleInput';
        showModal({
            title: 'Save to Personal Notebook',
            body: `
                <div style="display:flex; flex-direction:column; gap:12px;">
                    <div>
                        <label for="${titleInputId}" style="display:block; font-size:0.82rem; color:var(--text-secondary); margin-bottom:4px;">Note Title:</label>
                        <input type="text" id="${titleInputId}" value="${escapeHtml(initialTitle)}" maxlength="150"
                               style="width:100%; padding:8px 10px; background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:6px; color:var(--text-primary); outline:none;">
                    </div>
                    <div>
                        <label style="display:block; font-size:0.82rem; color:var(--text-secondary); margin-bottom:4px;">Category:</label>
                        <select id="noteCategoryInput" style="width:100%; padding:8px 10px; background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:6px; color:var(--text-primary); outline:none;">
                            <option value="General">General</option>
                            <option value="Study">Study</option>
                            <option value="Coding">Coding</option>
                            <option value="Career">Career</option>
                        </select>
                    </div>
                    <p style="font-size:0.78rem; color:var(--text-muted);">
                        This will save the entire response with syntax-highlighted code to your searchable notebook.
                    </p>
                </div>
            `,
            confirmText: 'Save Note',
            confirmStyle: 'primary',
            onConfirm: async () => {
                const titleInput = document.getElementById(titleInputId);
                const categoryInput = document.getElementById('noteCategoryInput');
                const noteTitle = titleInput ? titleInput.value.trim() : initialTitle;
                const noteCat = categoryInput ? categoryInput.value : 'General';

                try {
                    const res = await fetch('/api/notebook', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            title: noteTitle,
                            content: msg.content,
                            category: noteCat,
                            message_id: msg.id,
                            conversation_id: state.activeConversationId
                        })
                    });
                    const result = await res.json();
                    if (result.success) {
                        showToast('Saved to your Notebook', 'success');
                        updateNotebookCountBadge();
                    } else {
                        showToast(result.error || 'Failed to save note', 'error');
                    }
                } catch (err) {
                    showToast('Network error while saving note', 'error');
                }
            }
        });

        setTimeout(() => {
            const input = document.getElementById(titleInputId);
            if (input) { input.focus(); input.select(); }
        }, 100);
    }

    async function loadNotebookEntries(category = 'All', search = '') {
        if (!elements.notesGrid) return;

        try {
            let url = '/api/notebook?';
            if (category && category !== 'All') url += `category=${encodeURIComponent(category)}&`;
            if (search) url += `search=${encodeURIComponent(search)}&`;

            const res = await fetch(url);
            const data = await res.json();

            if (data.success) {
                state.notebookEntries = data.data || [];
                renderNotebookGrid();
                updateNotebookCountBadge();
            }
        } catch (err) {
            console.error('Failed to load notebook entries:', err);
        }
    }

    function renderNotebookGrid() {
        if (!elements.notesGrid || !elements.notebookEmptyState) return;

        if (state.notebookEntries.length === 0) {
            elements.notesGrid.innerHTML = '';
            elements.notebookEmptyState.style.display = 'flex';
            return;
        }

        elements.notebookEmptyState.style.display = 'none';
        elements.notesGrid.innerHTML = '';

        state.notebookEntries.forEach(note => {
            const card = document.createElement('div');
            card.className = 'note-card';

            const formattedDate = note.created_at ? new Date(note.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : '';
            const renderedContent = renderMarkdown(note.content);

            card.innerHTML = `
                <div class="note-header">
                    <h3 class="note-title">${escapeHtml(note.title)}</h3>
                </div>
                <div class="note-meta">
                    <span class="note-badge">${escapeHtml(note.category)}</span>
                    <span>${formattedDate}</span>
                </div>
                <div class="note-body">${renderedContent}</div>
                <div class="note-footer">
                    <div style="display:flex; align-items:center; gap:6px;">
                        ${note.conversation_id ? `
                            <a href="/?conv=${note.conversation_id}" class="btn-note-action" title="Open original conversation">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                                <span>Open Chat</span>
                            </a>
                        ` : ''}
                        <button class="btn-note-action btn-copy-note" type="button" title="Copy note content">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            <span>Copy</span>
                        </button>
                    </div>
                    <button class="btn-note-action delete btn-delete-note" type="button" title="Delete note">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        <span>Remove</span>
                    </button>
                </div>
            `;

            // Copy note action
            const copyNoteBtn = card.querySelector('.btn-copy-note');
            if (copyNoteBtn) {
                copyNoteBtn.addEventListener('click', () => {
                    navigator.clipboard.writeText(`${note.title}\n\n${note.content}`).then(() => {
                        showToast('Note copied to clipboard', 'success', 2000);
                    }).catch(() => showToast('Failed to copy note', 'error'));
                });
            }

            // Delete action
            const deleteBtn = card.querySelector('.btn-delete-note');
            deleteBtn.addEventListener('click', () => {
                showModal({
                    title: 'Delete Notebook Entry?',
                    body: `Are you sure you want to remove <strong>"${escapeHtml(note.title)}"</strong> from your personal notebook?`,
                    confirmText: 'Remove',
                    confirmStyle: 'danger',
                    onConfirm: async () => {
                        try {
                            const res = await fetch(`/api/notebook/${note.id}`, { method: 'DELETE' });
                            const result = await res.json();
                            if (result.success) {
                                showToast('Note removed from notebook', 'success');
                                loadNotebookEntries();
                            } else {
                                showToast(result.error || 'Failed to delete note', 'error');
                            }
                        } catch (err) {
                            showToast('Network error while deleting note', 'error');
                        }
                    }
                });
            });

            elements.notesGrid.appendChild(card);
        });
    }

    async function updateNotebookCountBadge() {
        if (!elements.notebookBadge) return;
        try {
            const res = await fetch('/api/notebook');
            const data = await res.json();
            if (data.success) {
                elements.notebookBadge.textContent = data.count || 0;
            }
        } catch (err) {}
    }

    // =========================================================================
    // Settings Management
    // =========================================================================
    async function loadSettings() {
        if (!elements.settingsWorkspace) return;

        try {
            const res = await fetch('/api/preferences');
            const data = await res.json();

            if (data.success) {
                const prefs = data.preferences || {};
                const stats = data.stats || {};

                if (elements.settingToneSelect && prefs.system_tone) {
                    elements.settingToneSelect.value = prefs.system_tone;
                }

                if (elements.statConversations) elements.statConversations.textContent = stats.total_conversations || 0;
                if (elements.statMessages) elements.statMessages.textContent = stats.total_messages || 0;
                if (elements.statNotes) elements.statNotes.textContent = stats.total_notebook_entries || 0;
            }
        } catch (err) {
            console.error('Failed to load settings:', err);
        }
    }

    // =========================================================================
    // Sidebar & Mobile Navigation
    // =========================================================================
    function openSidebar() {
        if (elements.sidebar) elements.sidebar.classList.add('open');
        if (elements.sidebarOverlay) elements.sidebarOverlay.classList.add('active');
    }

    function closeSidebar() {
        if (elements.sidebar) elements.sidebar.classList.remove('open');
        if (elements.sidebarOverlay) elements.sidebarOverlay.classList.remove('active');
    }

    // =========================================================================
    // Event Listeners & Initialization
    // =========================================================================
    function initEventListeners() {
        // Theme toggle
        if (elements.themeToggleBtn) {
            elements.themeToggleBtn.addEventListener('click', toggleTheme);
        }

        // Mobile drawer toggles
        if (elements.mobileMenuBtn) elements.mobileMenuBtn.addEventListener('click', openSidebar);
        if (elements.sidebarCloseBtn) elements.sidebarCloseBtn.addEventListener('click', closeSidebar);
        if (elements.sidebarOverlay) elements.sidebarOverlay.addEventListener('click', closeSidebar);

        // New Chat Button
        if (elements.btnNewChat) {
            elements.btnNewChat.addEventListener('click', (e) => {
                if (elements.chatWorkspace) {
                    e.preventDefault();
                    resetToNewChat();
                    closeSidebar();
                }
            });
        }

        // Topbar New Chat Button
        if (elements.topbarNewChatBtn) {
            elements.topbarNewChatBtn.addEventListener('click', (e) => {
                if (elements.chatWorkspace) {
                    e.preventDefault();
                    resetToNewChat();
                }
            });
        }

        // Sidebar Search Input
        if (elements.conversationSearchInput) {
            let debounceTimer;
            elements.conversationSearchInput.addEventListener('input', (e) => {
                const val = e.target.value;
                if (elements.clearSearchBtn) {
                    elements.clearSearchBtn.style.display = val ? 'block' : 'none';
                }
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    loadConversations(state.activeCategory, val);
                }, 250);
            });
        }

        if (elements.clearSearchBtn) {
            elements.clearSearchBtn.addEventListener('click', () => {
                if (elements.conversationSearchInput) {
                    elements.conversationSearchInput.value = '';
                    elements.clearSearchBtn.style.display = 'none';
                    loadConversations(state.activeCategory, '');
                }
            });
        }

        // Category Pills
        elements.categoryPills.forEach(pill => {
            pill.addEventListener('click', () => {
                elements.categoryPills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                state.activeCategory = pill.getAttribute('data-category');
                const search = elements.conversationSearchInput ? elements.conversationSearchInput.value : '';
                loadConversations(state.activeCategory, search);
            });
        });

        // Chat Textarea Auto-expand & Submit on Enter
        if (elements.messageInput) {
            elements.messageInput.addEventListener('input', () => {
                elements.messageInput.style.height = 'auto';
                elements.messageInput.style.height = Math.min(elements.messageInput.scrollHeight, 160) + 'px';
                updateCharCounter();
            });

            elements.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendChatMessage();
                }
            });
        }

        // Send Button
        if (elements.btnSendMessage) {
            elements.btnSendMessage.addEventListener('click', (e) => {
                e.preventDefault();
                sendChatMessage();
            });
        }

        // Starter Prompt Cards
        elements.promptCards.forEach(card => {
            card.addEventListener('click', () => {
                const prompt = card.getAttribute('data-prompt');
                const cat = card.getAttribute('data-category');
                if (elements.messageCategorySelect && cat) {
                    elements.messageCategorySelect.value = cat;
                }
                sendChatMessage(prompt, cat);
            });
        });

        // Notebook Search & Filter Tabs
        if (elements.notebookSearchInput) {
            let debounceTimer;
            elements.notebookSearchInput.addEventListener('input', (e) => {
                const val = e.target.value;
                if (elements.clearNotebookSearchBtn) {
                    elements.clearNotebookSearchBtn.style.display = val ? 'block' : 'none';
                }
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    const activeTab = document.querySelector('.notebook-tab.active');
                    const cat = activeTab ? activeTab.getAttribute('data-category') : 'All';
                    loadNotebookEntries(cat, val);
                }, 250);
            });
        }

        if (elements.clearNotebookSearchBtn) {
            elements.clearNotebookSearchBtn.addEventListener('click', () => {
                elements.notebookSearchInput.value = '';
                elements.clearNotebookSearchBtn.style.display = 'none';
                const activeTab = document.querySelector('.notebook-tab.active');
                const cat = activeTab ? activeTab.getAttribute('data-category') : 'All';
                loadNotebookEntries(cat, '');
            });
        }

        elements.notebookTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                elements.notebookTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                const cat = tab.getAttribute('data-category');
                const search = elements.notebookSearchInput ? elements.notebookSearchInput.value : '';
                loadNotebookEntries(cat, search);
            });
        });

        // Settings View Actions
        if (elements.themeChoiceDark) {
            elements.themeChoiceDark.addEventListener('click', () => setTheme('dark'));
        }
        if (elements.themeChoiceLight) {
            elements.themeChoiceLight.addEventListener('click', () => setTheme('light'));
        }
        if (elements.settingToneSelect) {
            elements.settingToneSelect.addEventListener('change', async (e) => {
                const tone = e.target.value;
                try {
                    await fetch('/api/preferences', {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ system_tone: tone })
                    });
                    showToast('Response tone updated', 'success', 2000);
                } catch (err) {}
            });
        }

        // Quick Action Prompt Template Pills
        document.querySelectorAll('.quick-pill').forEach(pill => {
            pill.addEventListener('click', () => {
                const template = pill.getAttribute('data-template');
                if (elements.messageInput && template) {
                    elements.messageInput.value = template;
                    elements.messageInput.style.height = 'auto';
                    elements.messageInput.style.height = Math.min(elements.messageInput.scrollHeight, 160) + 'px';
                    updateCharCounter();
                    elements.messageInput.focus();
                    showToast('Quick prompt inserted! Add your code/topic and press Enter.', 'info', 2500);
                }
            });
        });

        // Voice Dictation (Speech to Text using Web Speech API)
        const micBtn = document.getElementById('btnVoiceInput');
        if (micBtn) {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRec) {
                const recognition = new SpeechRec();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                let isRecording = false;

                micBtn.addEventListener('click', () => {
                    if (!isRecording) {
                        try {
                            recognition.start();
                            isRecording = true;
                            micBtn.classList.add('recording');
                            showToast('Listening... Speak into your microphone', 'info', 2500);
                        } catch (err) {
                            showToast('Could not access microphone', 'error');
                        }
                    } else {
                        recognition.stop();
                        isRecording = false;
                        micBtn.classList.remove('recording');
                    }
                });

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    if (elements.messageInput) {
                        elements.messageInput.value = (elements.messageInput.value ? elements.messageInput.value + ' ' : '') + transcript;
                        elements.messageInput.style.height = 'auto';
                        elements.messageInput.style.height = Math.min(elements.messageInput.scrollHeight, 160) + 'px';
                        updateCharCounter();
                        elements.messageInput.focus();
                    }
                    showToast('Speech converted to text!', 'success', 2000);
                };

                recognition.onend = recognition.onerror = () => {
                    isRecording = false;
                    micBtn.classList.remove('recording');
                };
            } else {
                micBtn.addEventListener('click', () => {
                    showToast('Voice dictation is supported in Google Chrome and Microsoft Edge.', 'info', 3000);
                });
            }
        }

        // Export Conversation Markdown
        const exportChatBtn = document.getElementById('btnExportChat');
        if (exportChatBtn) {
            exportChatBtn.addEventListener('click', () => {
                if (!state.activeConversationId) {
                    showToast('Open a chat to export', 'info');
                    return;
                }
                window.location.href = `/api/conversations/${state.activeConversationId}/export`;
                showToast('Downloading conversation markdown...', 'success', 2000);
            });
        }

        // Add Custom Note in Notebook View
        const newNoteModalBtn = document.getElementById('btnNewNoteModal');
        if (newNoteModalBtn) {
            newNoteModalBtn.addEventListener('click', () => {
                showModal({
                    title: 'Create Personal Study Note',
                    body: `
                        <div style="display:flex; flex-direction:column; gap:12px;">
                            <div>
                                <label style="display:block; font-size:0.82rem; color:var(--text-secondary); margin-bottom:4px;">Note Title:</label>
                                <input type="text" id="customNoteTitleInput" placeholder="e.g. Dijkstra's Algorithm Complexity" maxlength="150"
                                       style="width:100%; padding:8px 10px; background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:6px; color:var(--text-primary); outline:none;">
                            </div>
                            <div>
                                <label style="display:block; font-size:0.82rem; color:var(--text-secondary); margin-bottom:4px;">Category:</label>
                                <select id="customNoteCategoryInput" style="width:100%; padding:8px 10px; background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:6px; color:var(--text-primary); outline:none;">
                                    <option value="Study">Study</option>
                                    <option value="Coding">Coding</option>
                                    <option value="Career">Career</option>
                                    <option value="General">General</option>
                                </select>
                            </div>
                            <div>
                                <label style="display:block; font-size:0.82rem; color:var(--text-secondary); margin-bottom:4px;">Content (Markdown supported):</label>
                                <textarea id="customNoteContentInput" rows="5" placeholder="Write your notes, formulas, or code snippets..."
                                          style="width:100%; padding:8px 10px; background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:6px; color:var(--text-primary); font-family:inherit; outline:none; resize:vertical;"></textarea>
                            </div>
                        </div>
                    `,
                    confirmText: 'Save Note',
                    confirmStyle: 'primary',
                    onConfirm: async () => {
                        const title = document.getElementById('customNoteTitleInput')?.value.trim();
                        const category = document.getElementById('customNoteCategoryInput')?.value || 'General';
                        const content = document.getElementById('customNoteContentInput')?.value.trim();

                        if (!title || !content) {
                            showToast('Both title and content are required', 'error');
                            return;
                        }

                        try {
                            const res = await fetch('/api/notebook', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ title, content, category })
                            });
                            const result = await res.json();
                            if (result.success) {
                                showToast('Custom note saved to notebook!', 'success');
                                loadNotebookEntries();
                            } else {
                                showToast(result.error || 'Failed to save note', 'error');
                            }
                        } catch (err) {
                            showToast('Network error while saving note', 'error');
                        }
                    }
                });
            });
        }

        // Export Compiled Notebook
        const exportNotebookBtn = document.getElementById('btnExportNotebook');
        if (exportNotebookBtn) {
            exportNotebookBtn.addEventListener('click', () => {
                const activeTab = document.querySelector('.notebook-tab.active');
                const cat = activeTab ? activeTab.getAttribute('data-category') : 'All';
                let url = '/api/notebook/export';
                if (cat && cat !== 'All') url += `?category=${encodeURIComponent(cat)}`;
                window.location.href = url;
                showToast('Downloading compiled study notebook...', 'success', 2000);
            });
        }

        // Keyboard Shortcuts Modal & Hotkeys
        const openShortcuts = () => {
            showModal({
                title: '⚡ Keyboard Shortcuts & Power Tips',
                body: `
                    <div style="display:flex; flex-direction:column; gap:10px; font-size:0.86rem;">
                        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid var(--border-subtle);">
                            <span>Send Message</span>
                            <kbd>Enter</kbd>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid var(--border-subtle);">
                            <span>Multi-line code / New line</span>
                            <span><kbd>Shift</kbd> + <kbd>Enter</kbd></span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid var(--border-subtle);">
                            <span>Quick Search Conversations</span>
                            <span><kbd>Ctrl</kbd> + <kbd>K</kbd></span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid var(--border-subtle);">
                            <span>Start Fresh Chat</span>
                            <span><kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>C</kbd></span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:6px 0;">
                            <span>Voice Dictation</span>
                            <span>Click 🎙️ Microphone</span>
                        </div>
                    </div>
                `,
                confirmText: 'Got It',
                confirmStyle: 'primary'
            });
        };

        const shortcutsBtn = document.getElementById('btnShortcutsModal');
        if (shortcutsBtn) {
            shortcutsBtn.addEventListener('click', openShortcuts);
        }

        // Global hotkeys
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                if (elements.conversationSearchInput) {
                    elements.conversationSearchInput.focus();
                    elements.conversationSearchInput.select();
                }
            }
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'c') {
                e.preventDefault();
                resetToNewChat();
            }
            if (e.key === '?' && !['TEXTAREA', 'INPUT'].includes(document.activeElement.tagName)) {
                e.preventDefault();
                openShortcuts();
            }
        });
    }

    // --- Bootstrap ---
    document.addEventListener('DOMContentLoaded', () => {
        // Theme init
        const savedTheme = localStorage.getItem('askspace_theme');
        if (savedTheme && savedTheme !== state.theme) {
            setTheme(savedTheme);
        }

        initEventListeners();
        loadConversations();
        updateNotebookCountBadge();

        if (elements.notebookWorkspace) {
            loadNotebookEntries();
        }

        if (elements.settingsWorkspace) {
            loadSettings();
        }

        // Check if query param specifies conversation to open
        const urlParams = new URLSearchParams(window.location.search);
        const convParam = urlParams.get('conv');
        if (convParam && elements.chatWorkspace) {
            openConversation(parseInt(convParam, 10));
        }
    });

})();
