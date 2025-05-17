document.addEventListener('DOMContentLoaded', () => {
    // --- State ---
    let activeConversationId = null;
    function formattedTime() {
        const timestamp = new Date();
        return `${String(timestamp.getHours()).padStart(2, '0')}:${String(timestamp.getMinutes()).padStart(2, '0')}`;
    }

    // --- Elements ---
    const elements = {
        newConversationBtn: document.getElementById('newConversationBtn'),
        conversationList: document.getElementById('conversationList'),
        chatMessages: document.getElementById('chatMessages'),
        chatForm: document.getElementById('chatForm'),
        messageInput: document.getElementById('messageInput'),
        submitButton: document.querySelector('#chatForm button[type="submit"]'),
        welcomeMessage: document.getElementById('welcomeMessage'),
    };

    // --- API ---
    const api = {
        async getConversations() {
            const res = await fetch('/all_conversations');
            if (!res.ok) throw new Error(`Failed to fetch conversations: ${res.statusText}`);
            return res.json();
        },
        async getMessages(convId) {
            if (!convId) return { messages: [] };
            const res = await fetch(`/all_msg_by_conv/${convId}`);
            if (!res.ok) throw new Error(`Failed to fetch messages for ${convId}: ${res.statusText}`);
            return res.json();
        },
        async sendMessage(convId, messageContent) {
            const res = await fetch(`/create_conversation/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    message: messageContent,
                    ...(convId && { conv_id: convId })
                }),
            });
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({ detail: 'Failed to send message' }));
                throw new Error(errorData.detail || `Failed to send message: ${res.statusText}`);
            }
            return res.json();
        },
        async updateConversation(messageContent, id_msg) {
            const res = await fetch(`/update_conversation/${encodeURIComponent(messageContent)}/${id_msg}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ message: messageContent, id_msg }),
            });
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({ detail: 'Failed to update message' }));
                throw new Error(errorData.detail || `Failed to update message: ${res.statusText}`);
            }
            return res.json();
        }
    };

    // --- UI Helpers ---
    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag));
    }

    function clearMessages() {
        const wrapper = elements.chatMessages.querySelector('.max-w-3xl.mx-auto.w-full');
        (wrapper || elements.chatMessages).innerHTML = '';
    }

    function showWelcomeMessage() {
        if (elements.welcomeMessage) elements.welcomeMessage.style.display = 'flex';
    }

    function hideWelcomeMessage() {
        if (elements.welcomeMessage) elements.welcomeMessage.style.display = 'none';
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed bottom-4 right-4 bg-red-100 border border-violet-700 text-red-700 px-4 py-3 rounded shadow-lg z-50 transition-opacity duration-300 ease-in-out';
        errorDiv.setAttribute('role', 'alert');
        errorDiv.innerHTML = `<strong class="font-bold">Erreur!</strong> <span class="block sm:inline">${message}</span>`;
        document.body.appendChild(errorDiv);
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }

    // --- Conversation List ---
    async function updateConversationList() {
        try {
            const data = await api.getConversations();
            const conversations = data.conversations || [];
            const isNew = activeConversationId === null;
            const tempNewEntryHTML = isNew ? document.getElementById('conv-new')?.outerHTML || '' : '';
            elements.conversationList.innerHTML = `
                <div class="px-0 py-2 text-xs font-semibold text-gray-400 uppercase border-b border-gray-200">Recent Chats</div>
            `;
            if (isNew && tempNewEntryHTML) {
                elements.conversationList.innerHTML += tempNewEntryHTML;
                document.getElementById('conv-new')?.addEventListener('click', () => setActiveConversation(null));
            }
            elements.conversationList.insertAdjacentHTML('beforeend',
                conversations.map(conv => {
                    const convId = conv.conv_id;
                    const convTitle = escapeHTML(conv.subject || 'Untitled Conversation');
                    if (!convId) return '';
                    const isActive = activeConversationId === convId;
                    return `
                        <div id="conv-${convId}"
                            class="flex items-center px-2 py-0.25 text-xs cursor-pointer ${isActive ? 'bg-violet-200' : 'hover:bg-violet-100'} transition-colors duration-200"
                            data-id="${convId}" role="button" tabindex="0" aria-current="${isActive ? 'page' : 'false'}">
                            <div class="flex-shrink-0 w-6 h-6 mr-1">
                                <i class="fa ${isActive ? 'fa-solid fa-comment' : 'fa-regular fa-comment'} text-sm ${isActive ? 'text-violet-600' : 'text-gray-400'}"></i>
                            </div>
                            <span class="truncate flex-1 text-gray-700 leading-tight">${convTitle}</span>
                        </div>
                    `;
                }).join('')
            );
            elements.conversationList.addEventListener('click', (event) => {
                const target = event.target.closest('[data-id]');
                if (target) setActiveConversation(target.getAttribute('data-id'));
            });
            updateConversationHighlight();
        } catch (error) {
            elements.conversationList.innerHTML = `<div class="text-violet-700 p-4">Erreur chargement conversations. ${error.message}</div>`;
        }
    }

    function updateConversationHighlight() {
        elements.conversationList.querySelectorAll('[data-id]').forEach(div => {
            const id = div.getAttribute('data-id');
            const isActive = (activeConversationId !== null && id === activeConversationId) ||
                (activeConversationId === null && id === 'new');
            div.classList.toggle('bg-violet-50', isActive);
            div.querySelector('i').classList.toggle('fa-solid', isActive);
            div.querySelector('i').classList.toggle('fa-regular', !isActive);
            div.querySelector('i').classList.toggle('text-violet-600', isActive);
            div.querySelector('i').classList.toggle('text-gray-400', !isActive);
            div.classList.toggle('hover:bg-gray-50', !isActive);
            div.setAttribute('aria-current', isActive ? 'page' : 'false');
        });
    }

    function createNewConversationEntry() {
        document.getElementById('conv-new')?.remove();
        const draftHTML = `
            <div id="conv-new"
                class="flex items-center px-4 py-2.5 text-sm bg-violet-50 cursor-pointer transition-colors duration-200"
                data-id="new" role="button" tabindex="0" aria-current="page">
                <div class="flex-shrink-0 w-6 h-6 mr-3">
                    <i class="fa fa-solid fa-circle text-base text-violet-600"></i>
                </div>
                <span class="truncate flex-1 text-gray-800 font-medium leading-tight">New Chat</span>
            </div>
        `;
        elements.conversationList.insertAdjacentHTML("afterbegin", draftHTML);
        document.getElementById('conv-new')?.addEventListener('click', () => setActiveConversation(null));
    }

    function startNewConversation() {
        activeConversationId = null;
        clearMessages();
        showWelcomeMessage();
        elements.messageInput.value = '';
        handleInputChange();
        elements.messageInput.focus();
        createNewConversationEntry();
        updateConversationHighlight();
    }

    // --- Conversation Messages ---
    async function setActiveConversation(convId) {
        const id = typeof convId === 'string' ? convId.trim() : convId;
        if (id === 'new' || id === null || id === undefined) {
            if (activeConversationId !== null) startNewConversation();
            return;
        }
        if (activeConversationId === id) return;
        activeConversationId = id;
        clearMessages();
        hideWelcomeMessage();
        elements.messageInput.value = '';
        handleInputChange();
        elements.submitButton.disabled = true;
        document.getElementById('conv-new')?.remove();
        try {
            const data = await api.getMessages(activeConversationId);
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    if (msg.msg_user) {
                        renderMessage({
                            data_type: "str",
                            id: `${msg.msg_id}`,
                            content: msg.msg_user,
                            role: 'user',
                            timestamp: msg.date_env,
                            error: false,
                        });
                    }
                    if ('res_user' in msg) {
                        let content = null;
                        if (msg.res_user) {
                            content = msg.type_res === "list" ? msg.message : msg.res_user;
                        } else if (msg.res_user === " ") {
                            content = "le message sera affiché ici";
                        }
                        renderMessage({
                            data_type: msg.type_res,
                            id: `${msg.msg_id}`,
                            content,
                            role: 'bot',
                            timestamp: msg.date_rec,
                            error: msg.error || false,
                        });
                    }
                });
                elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
            } else {
                renderMessage({
                    id: `notice-${Date.now()}`,
                    content: 'Aucun message dans cette conversation.',
                    role: 'bot',
                    timestamp: formattedTime(),
                    error: false,
                });
            }
            updateConversationHighlight();
            elements.messageInput.focus();
            elements.submitButton.disabled = false;
        } catch (error) {
            showError(`Impossible de charger la conversation ${activeConversationId}.`);
            showWelcomeMessage();
            activeConversationId = null;
            updateConversationHighlight();
        } finally {
            handleInputChange();
        }
    }

    // --- Message Rendering ---
    function renderMessage(message) {
        hideWelcomeMessage();
        const wrapper = elements.chatMessages.querySelector('.max-w-3xl.mx-auto.w-full') || elements.chatMessages;
        const messageElement = document.createElement('div');
        messageElement.id = message.id || `msg-${message.role}-${Date.now()}`;
        messageElement.className = `chat-message ${message.role === 'user' ? 'user' : 'assistant'} message-animation`;
        let sanitizedContent = '';
        if (message.data_type === "list") {
            sanitizedContent = createResultContent(message.content,message.id);
        } else {
            sanitizedContent = escapeHTML(message.content || '');
        }
        let avatarChar = '?', avatarBg = 'bg-violet-300', bubbleBg = 'bg-violet-100';
        if (message.role === 'user') {
            avatarChar = 'U';
            avatarBg = 'bg-violet-600';
            bubbleBg = 'bg-violet-300 text-gray-800 rounded-lg';
        } else if (message.role === 'bot') {
            avatarChar = 'B';
            avatarBg = 'bg-violet-300';
            bubbleBg = 'bg-violet-200 text-gray-800 rounded-lg';
        }
        if (message.error) {
            avatarChar = '!';
            avatarBg = 'bg-violet-700';
            bubbleBg = 'bg-violet-100 text-violet-700 border border-violet-700 rounded-lg';
        }
        messageElement.innerHTML = `
            <div class="flex w-full items-start gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}">
                <div class="flex-shrink-0">
                    <div class="h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold ${avatarBg} text-white">
                        ${avatarChar}
                    </div>
                </div>
                <div class="flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'} w-full">
                    <div class="message-content p-4 rounded-lg shadow-sm text-sm ${bubbleBg} max-w-[85%] md:max-w-[100%]">
                        ${message.isLoading
                            ? '<div class="flex items-center gap-2"><div class="loader"></div><span class="text-gray-500 text-xs italic">Génération...</span></div>'
                            : sanitizedContent
                        }
                    </div>
                    ${!message.isLoading ? `
                    <div class="text-xs text-gray-500 mt-1 px-1">
                        ${message.timestamp}
                    </div>` : ''}
                </div>
            </div>
        `;
        wrapper.appendChild(messageElement);
        requestAnimationFrame(() => {
            messageElement.classList.remove('message-enter');
            messageElement.classList.add('message-enter-active');
        });
        if (!message.isLoading) {
            elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
        }
        return messageElement;
    }

    function updateRenderedMessage(messageElement, messageData) {
        if (!messageElement || !messageData) return;
        let sanitizedContent = '';
        if (messageData.type_res === "list") {
            sanitizedContent = createResultContent(messageData.content,messageData.id);
        } else {
            sanitizedContent = escapeHTML(messageData.content || '');
        }
        let avatarChar = '?', avatarBg = 'bg-violet-300', bubbleBg = 'bg-violet-100';
        if (messageData.role === 'bot') {
            avatarChar = 'B';
            avatarBg = 'bg-violet-300';
            bubbleBg = 'bg-violet-200 text-gray-800 rounded-lg';
        }
        if (messageData.error) {
            avatarChar = '!';
            avatarBg = 'bg-violet-700';
            bubbleBg = 'bg-violet-100 text-violet-700 border border-violet-700 rounded-lg';
        }
        messageElement.innerHTML = `
            <div class="flex w-full items-start gap-3 ${messageData.role === 'user' ? 'flex-row-reverse' : 'flex-row'}">
                <div class="flex-shrink-0">
                    <div class="h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold ${avatarBg} text-white">
                        ${avatarChar}
                    </div>
                </div>
                <div class="flex flex-col ${messageData.role === 'user' ? 'items-end' : 'items-start'} w-full">
                    <div class="message-content p-4 rounded-lg shadow-sm text-sm ${bubbleBg} max-w-[85%] md:max-w-[100%]">
                        ${sanitizedContent}
                    </div>
                    <div class="text-xs text-gray-500 mt-1 px-1">
                        ${messageData.timestamp}
                    </div>
                </div>
            </div>
        `;
        messageElement.id = messageData.id || messageElement.id;
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }

    // --- Message Submission ---
    async function handleMessageSubmit(e) {
        e.preventDefault();
        const messageContent = elements.messageInput.value.trim();
        if (!messageContent) return;
        const wasNewConversation = activeConversationId === null;
        renderMessage({
            data_type: "str",
            id: `msg-user-${Date.now()}`,
            content: messageContent,
            role: 'user',
            timestamp: formattedTime(),
            error: false,
        });
        elements.messageInput.value = '';
        handleInputChange();
        elements.submitButton.disabled = true;
        elements.messageInput.disabled = true;
        const loadingMessageData = {
            id: `msg-bot-loading-${Date.now()}`,
            role: 'bot',
            content: 'Génération...',
            timestamp: formattedTime(),
            isLoading: true,
        };
        const loadingElement = renderMessage(loadingMessageData);
        try {
            const responseData = await api.sendMessage(activeConversationId, messageContent);
            if (wasNewConversation && responseData.conv_id) {
                activeConversationId = responseData.conv_id;
                await updateConversationList();
                updateConversationHighlight();
            } else if (activeConversationId !== responseData.conv_id) {
                activeConversationId = responseData.conv_id;
                await updateConversationList();
                updateConversationHighlight();
            }
            if (responseData.message && responseData.message.content) {
                const response_update = await api.updateConversation(responseData.message.content, responseData.message.msg_id);
                updateRenderedMessage(loadingElement, {
                    id: responseData.message.msg_id,
                    content: response_update.response,
                    role: 'bot',
                    timestamp: response_update.format_date,
                    error: false,
                    isLoading: false,
                    type_res: response_update.type_res
                });
            } else {
                throw new Error("Réponse invalide du serveur.");
            }
        } catch (error) {
            updateRenderedMessage(loadingElement, {
                id: loadingElement.id,
                content: `Erreur: ${error.message || "Impossible d'envoyer le message."}`,
                role: 'bot',
                timestamp: formattedTime(),
                error: error.message || true,
                isLoading: false,
            });
            if (wasNewConversation) {
                activeConversationId = null;
                updateConversationHighlight();
            }
        } finally {
            elements.submitButton.disabled = false;
            elements.messageInput.disabled = false;
            handleInputChange();
            elements.messageInput.focus();
            elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
        }
    }

    // --- Table Result Rendering ---

    let currentDownloadMsgId = null;


    function createResultContent(result, id_msg) {
    if (!Array.isArray(result) || result.length === 0) return '';

    const columns = Object.keys(result[0]);
    const rows = result.slice(0, 10); // Afficher seulement les 10 premières lignes

    // Construction du tableau HTML
    // Construction du tableau HTML
    let tableHTML = `
<div class="overflow-x-auto w-full">
    <table class="w-full border-collapse">
        <thead class="bg-gray-100">
            <tr>
                ${columns.map(col => `<th class="border border-gray-300 px-3 py-2 text-left text-sm font-medium text-gray-700">${col}</th>`).join('')}
            </tr>
        </thead>
        <tbody>
            ${rows.map((row, i) => `
                <tr class="${i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}">
                    ${columns.map(col => {
                        const cellContent = String(row[col] ?? '').replace(/<br\s*\/?>/gi, '');
                        return `<td class="border border-gray-300 px-3 py-2 text-sm text-gray-700">${cellContent}</td>`;
                    }).join('')}
                </tr>
            `).join('')}
        </tbody>
    </table>
</div>
    `;

    // Si plus de 10 lignes, bouton "Voir tout"
    if (result.length >= 10) {
        tableHTML += `
<div class="mt-3 flex items-center justify-between">
    <span class="text-xs text-gray-500">
        Affichage de 10 sur ${result.length} lignes
    </span>
    <button 
        class="view-all-results px-3 py-1 text-xs font-medium text-violet-600 hover:text-violet-800 bg-violet-50 hover:bg-violet-100 rounded-md transition-colors"
        data-id="${id_msg}"
    >
        Voir tout
    </button>
</div>
        `;
    }

    // Stocker les résultats complets pour usage ultérieur
    window.fullResultsById = window.fullResultsById || {};
    window.fullResultsById[id_msg] = result;


    return tableHTML;
}

// Voir tous les résultats dans une modale
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('view-all-results')) {
        const id_msg = e.target.getAttribute('data-id');
        const fullResult = window.fullResultsById?.[id_msg];
        if (!fullResult) return;
        currentDownloadMsgId = id_msg;

        const columns = Object.keys(fullResult[0] || {});
        const fullTableHTML = `
            <div class="overflow-x-auto w-full">
                <table class="w-full border-collapse text-sm">
                    <thead class="bg-gray-100 dark:bg-gray-700">
                        <tr>
                            ${columns.map(col => `<th class="border px-3 py-2 text-left">${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${fullResult.map((row, i) => `
                            <tr class="${i % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'}">
                                ${columns.map(col => `<td class="border px-3 py-2">${String(row[col] ?? '').replace(/<br\s*\/?>/gi, '')}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        document.getElementById('modalTableContent').innerHTML = fullTableHTML;
        document.getElementById('fullTableModal')?.classList.remove('hidden');
       
    }
   
});

// Fermer la modale
document.getElementById('closeModal')?.addEventListener('click', () => {
    document.getElementById('fullTableModal')?.classList.add('hidden');
});
document.getElementById('downloadExcel')?.addEventListener('click', () => {
    id_msg =currentDownloadMsgId
    console.log("iddddddd",id_msg)
   
    const downloadUrl = `/new_excel/${id_msg}/`;

    console.log("downloadUrl",downloadUrl)
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `response_${id_msg}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});    

    // --- Input Handlers ---
    function handleInputChange() {
        const message = elements.messageInput.value.trim();
        elements.submitButton.disabled = !message;
        autoResizeTextarea();
    }

    function autoResizeTextarea() {
        const textarea = elements.messageInput;
        textarea.style.height = 'auto';
        const scrollHeight = textarea.scrollHeight;
        const maxHeight = 150, minHeight = 44;
        textarea.style.height = `${Math.min(maxHeight, Math.max(minHeight, scrollHeight))}px`;
    }

    function handleInputKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!elements.submitButton.disabled) {
                elements.chatForm.requestSubmit();
            }
        }
    }

    // --- Theme ---
    function initTheme() {
        document.documentElement.classList.remove('dark');
    }

    // --- Event Listeners ---
    function initEventListeners() {
        elements.newConversationBtn?.addEventListener('click', () => startNewConversation(true));
        elements.chatForm?.addEventListener('submit', handleMessageSubmit);
        elements.messageInput?.addEventListener('input', handleInputChange);
        elements.messageInput?.addEventListener('keydown', handleInputKeydown);
    }

    // --- Init ---
    function init() {
        initTheme();
        initEventListeners();
        showWelcomeMessage();
        updateConversationList();
        handleInputChange();
    }

    init();
});