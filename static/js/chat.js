document.addEventListener('DOMContentLoaded', () => {
    // --- State ---
    let conversations = [];
    let activeConversationId = null;

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
        getConversations: async () => {
            const response = await fetch('/all_conversations');
            if (!response.ok) throw new Error(`Failed to fetch conversations: ${response.statusText}`);
            return response.json();
        },
        getMessages: async (convId) => {
            if (!convId) return { messages: [] };
            const response = await fetch(`/all_msg_by_conv/${convId}`);
            if (!response.ok) throw new Error(`Failed to fetch messages for ${convId}: ${response.statusText}`);
            return response.json();
        },
        sendMessage: async (convId, messageContent) => {
            const response = await fetch(`/create_conversation/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    message: messageContent,
                    ...(convId && { conv_id: convId })
                }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to send message' }));
                throw new Error(errorData.detail || `Failed to send message: ${response.statusText}`);
            }
            return response.json();
        },
        updateConversation: async (messageContent, id_msg) => {
            const response = await fetch(`/update_conversation/${encodeURIComponent(messageContent)}/${id_msg}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ message: messageContent, id_msg: id_msg }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to update message' }));
                throw new Error(errorData.detail || `Failed to update message: ${response.statusText}`);
            }
            return response.json();
        }
    };

    // --- UI Helpers ---
    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, tag => ({
            '&': '&',
            '<': '<',
            '>': '>',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag));
    }

    function clearMessages() {
        elements.chatMessages.innerHTML = '';
    }
    function showWelcomeMessage() {
        if (elements.welcomeMessage) elements.welcomeMessage.style.display = 'flex';
    }
    function hideWelcomeMessage() {
        if (elements.welcomeMessage) elements.welcomeMessage.style.display = 'none';
    }
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded shadow-lg z-50 transition-opacity duration-300 ease-in-out';
        errorDiv.setAttribute('role', 'alert');
        errorDiv.innerHTML = `<strong class="font-bold">Erreur!</strong> <span class="block sm:inline">${message}</span>`;
        document.body.appendChild(errorDiv);
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            setTimeout(() => { errorDiv.remove(); }, 300);
        }, 5000);
    }

    // --- Conversation List ---
    async function updateConversationList() {
        try {
            const data = await api.getConversations();
            const conversationsFromServer = data.conversations || [];
            const isNewConversationActive = activeConversationId === null;
            const tempNewEntryHTML = isNewConversationActive ? document.getElementById('conv-new')?.outerHTML || '' : '';
            elements.conversationList.innerHTML = '';
            if (isNewConversationActive && tempNewEntryHTML) {
                elements.conversationList.innerHTML = tempNewEntryHTML;
                document.getElementById('conv-new')?.addEventListener('click', () => setActiveConversation(null));
            }
            const serverListHTML = conversationsFromServer.map(conv => {
                const convId = conv.conv_id;
                const convTitle = conv.subject;
                if (!convId) return '';
                const isActive = activeConversationId === convId;
                return `
                    <div id="conv-${convId}"
                        class="group conv-detail flex items-center justify-between rounded-md py-2 px-3 cursor-pointer transition-colors duration-150 ${isActive ? 'conversation-active font-semibold' : 'hover:bg-gray-100 text-gray-700'}"
                        data-id="${convId}" role="button" tabindex="0" aria-current="${isActive ? 'page' : 'false'}">
                        <span class="truncate flex-1 text-sm ${isActive ? 'text-inwi' : ''} pr-2" data-conv-id="${convId}">
                            ${convTitle}
                        </span>
                    </div>
                `;
            }).join('');
            elements.conversationList.insertAdjacentHTML('beforeend', serverListHTML);
            elements.conversationList.addEventListener('click', (event) => {
                const targetButton = event.target.closest('.conv-detail');
                if (targetButton) {
                    const id = targetButton.getAttribute('data-id');
                    if (id) setActiveConversation(id);
                }
            });
            updateConversationHighlight();
        } catch (error) {
            elements.conversationList.innerHTML = `<div class="text-red-500 p-4">Erreur chargement conversations. ${error.message}</div>`;
        }
    }

    function updateConversationHighlight() {
        const listItems = elements.conversationList.querySelectorAll('.conv-detail');
        listItems.forEach(div => {
            const id = div.getAttribute('data-id');
            const isActive = (activeConversationId !== null && id === activeConversationId) ||
                (activeConversationId === null && id === 'new');
            if (isActive) {
                div.classList.add('conversation-active', 'font-semibold');
                div.classList.remove('hover:bg-gray-100', 'text-gray-700');
                div.querySelector('span')?.classList.add('text-inwi');
                div.setAttribute('aria-current', 'page');
            } else {
                div.classList.remove('conversation-active', 'font-semibold');
                div.classList.add('hover:bg-gray-100', 'text-gray-700');
                div.querySelector('span')?.classList.remove('text-inwi');
                div.setAttribute('aria-current', 'false');
            }
        });
    }

    function createNewConversationEntry() {
        const existingDraft = document.getElementById('conv-new');
        if (existingDraft) existingDraft.remove();
        const draftHTML = `
            <div id="conv-new"
                class="group flex conv-detail items-center justify-between rounded-md py-2 px-3 cursor-pointer transition-colors duration-150 conversation-active font-semibold"
                data-id="new" role="button" tabindex="0" aria-current="page">
                <span class="truncate flex-1 text-sm text-inwi pr-2" data-conv-id="New Conversation">
                    New Conversation
                </span>
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
        const trimmedConvId = typeof convId === 'string' ? convId.trim() : convId;
        if (trimmedConvId === 'new' || trimmedConvId === null || trimmedConvId === undefined) {
            if (activeConversationId !== null) startNewConversation();
            return;
        }
        if (activeConversationId === trimmedConvId) return;
        activeConversationId = trimmedConvId;
        clearMessages();
        hideWelcomeMessage();
        elements.messageInput.value = '';
        handleInputChange();
        elements.submitButton.disabled = true;
        const tempNewEntry = document.getElementById('conv-new');
        if (tempNewEntry) tempNewEntry.remove();
        try {
            const data = await api.getMessages(activeConversationId);
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    if (msg.msg_user) {
                        renderMessage({
                            data_type: "str",
                            id: `user-${msg.msg_id || Date.now()}-${Math.random()}`,
                            content: msg.msg_user,
                            role: 'user',
                            timestamp: new Date(msg.timestamp || Date.now()),
                            error: false,
                        });
                    }
                    if (msg.hasOwnProperty('res_user')) {
                        let content = null;
                        if (msg.res_user) {
                            content = msg.type_res === "list" ? msg.message : msg.res_user;
                        } else if (msg.res_user == " ") {
                            content = "le message sera affiché ici";
                        }
                        renderMessage({
                            data_type: msg.type_res,
                            id: `bot-${msg.msg_id || Date.now()}-${Math.random()}`,
                            content: content,
                            role: 'bot',
                            timestamp: new Date(msg.timestamp || Date.now()),
                            error: msg.error || false,
                        });
                    }
                });
                elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
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
        const messageElement = document.createElement('div');
        messageElement.id = message.id || `msg-${message.role}-${Date.now()}`;
        messageElement.className = `chat-message ${message.role === 'user' ? 'user' : 'assistant'} mb-4 message-animation`;
        let sanitizedContent = '';
        if (message.data_type === "list") {
            sanitizedContent = createResultContent(message.content);
        } else {
            sanitizedContent = escapeHTML(message.content || '');
        }
        let avatarChar = '?', avatarBg = 'bg-gray-400', bubbleBg = 'bg-gray-100';
        if (message.role === 'user') {
            avatarChar = 'U';
            avatarBg = 'bg-inwi';
            bubbleBg = 'bg-inwi text-white rounded-br-none';
        } else if (message.role === 'bot') {
            avatarChar = 'B';
            avatarBg = 'bg-gray-200';
            bubbleBg = 'bg-white text-gray-800 rounded-bl-none';
        }
        if (message.error) {
            avatarChar = '!';
            avatarBg = 'bg-red-500';
            bubbleBg = 'bg-red-100 text-red-700 border border-red-300 rounded-lg';
        }
        const contentHTML = `
            <div class="flex max-w-[85%] md:max-w-[75%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start gap-2.5">
                <div class="flex-shrink-0">
                    <div class="h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold ${avatarBg} text-white">
                        ${avatarChar}
                    </div>
                </div>
                <div class="flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'}">
                    <div class="message-content px-3.5 py-2.5 rounded-lg shadow-sm text-sm ${bubbleBg}">
                        ${message.isLoading
                            ? '<div class="flex items-center gap-2"><div class="loader"></div><span class="text-gray-500 text-xs italic">Génération...</span></div>'
                            : sanitizedContent
                        }
                    </div>
                    ${!message.isLoading ? `
                    <div class="text-xs text-gray-500 mt-1 px-1">
                        ${message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>` : ''}
                </div>
            </div>
        `;
        messageElement.innerHTML = contentHTML;
        elements.chatMessages.appendChild(messageElement);
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
            sanitizedContent = createResultContent(messageData.content);
        } else {
            sanitizedContent = escapeHTML(messageData.content || '');
        }
        let avatarChar = '?', avatarBg = 'bg-gray-400', bubbleBg = 'bg-gray-100';
        if (messageData.role === 'bot') {
            avatarChar = 'B';
            avatarBg = 'bg-gray-200';
            bubbleBg = 'bg-white text-gray-800 rounded-bl-none';
        }
        if (messageData.error) {
            avatarChar = '!';
            avatarBg = 'bg-red-500';
            bubbleBg = 'bg-red-100 text-red-700 border border-red-300 rounded-lg';
        }
        const contentHTML = `
            <div class="flex max-w-[85%] md:max-w-[75%] ${messageData.role === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start gap-2.5">
                <div class="flex-shrink-0">
                    <div class="h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold ${avatarBg} text-white">
                        ${avatarChar}
                    </div>
                </div>
                <div class="flex flex-col ${messageData.role === 'user' ? 'items-end' : 'items-start'}">
                    <div class="message-content px-3.5 py-2.5 rounded-lg shadow-sm text-sm ${bubbleBg}">
                        ${sanitizedContent}
                    </div>
                    <div class="text-xs text-gray-500 mt-1 px-1">
                        ${messageData.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                </div>
            </div>
        `;
        messageElement.innerHTML = contentHTML;
        messageElement.id = messageData.id || messageElement.id;
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }

    // --- Message Submission ---
    async function handleMessageSubmit(e) {
        e.preventDefault();
        const messageContent = elements.messageInput.value.trim();
        if (!messageContent) return;
        const wasNewConversation = activeConversationId === null;
        const userMessage = {
            data_type: "str",
            id: `msg-user-${Date.now()}`,
            content: messageContent,
            role: 'user',
            timestamp: new Date(),
            error: false,
        };
        renderMessage(userMessage);
        elements.messageInput.value = '';
        handleInputChange();
        elements.submitButton.disabled = true;
        elements.messageInput.disabled = true;
        const loadingMessageData = {
            id: `msg-bot-loading-${Date.now()}`,
            role: 'bot',
            content: 'Génération...',
            timestamp: new Date(),
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
                timestamp: new Date(),
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
    function createResultContent(result) {
        if (Array.isArray(result) && result.length > 0) {
            const columns = Object.keys(result[0]);
            const rows = result.slice(0, 10);
            let tableHTML = `<div class="overflow-x-auto w-full">
                <table class="w-full border-collapse">
                    <thead class="bg-gray-100">
                        <tr>
                            ${columns.map(col => `<th class="border border-gray-300 px-3 py-2 text-left text-sm">${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${rows.map((row, i) => `
                            <tr class="${i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}">
                                ${columns.map(col => {
                                    const cellContent = String(row[col] ?? '').replace(/<br\s*\/?>/gi, '');
                                    return `<td class="border border-gray-300 px-3 py-2 text-sm">${cellContent}</td>`;
                                }).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>`;
            if (result.length > 10) {
                tableHTML += `
                    <div class="mt-2 text-sm text-gray-500 flex justify-center items-center gap-2" style="margin-top: -45px;">
                        <span>* ${result.length} lignes trouvées, affichage limité aux 10 premières.</span>
                        <button class="text-inwi hover:underline view-all-results">Voir tout</button>
                    </div>
                `;
            }
            document.addEventListener('click', function (e) {
                if (e.target && e.target.classList.contains('view-all-results')) {
                    const fullTableHTML = `
                        <div class="overflow-x-auto w-full">
                            <table class="w-full border-collapse">
                                <thead class="bg-gray-100">
                                    <tr>
                                        ${columns.map(col => `<th class="border border-gray-300 px-3 py-2 text-left text-sm">${col}</th>`).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${result.map((row, i) => `
                                        <tr class="${i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}">
                                            ${columns.map(col => {
                                                const cellContent = String(row[col] ?? '').replace(/<br\s*\/?>/gi, '');
                                                return `<td class="border border-gray-300 px-3 py-2 text-sm">${cellContent}</td>`;
                                            }).join('')}
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `;
                    document.getElementById('modalTableContent').innerHTML = fullTableHTML;
                    document.getElementById('fullTableModal').classList.remove('hidden');
                }
            });
            document.getElementById('closeModal')?.addEventListener('click', () => {
                document.getElementById('fullTableModal').classList.add('hidden');
            });
            document.getElementById('downloadExcel')?.addEventListener('click', () => {
                if (!columns.length || !result.length) return;
                const data = [
                    columns,
                    ...result.map(row => columns.map(col => row[col] ?? ''))
                ];
                const worksheet = XLSX.utils.aoa_to_sheet(data);
                const workbook = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(workbook, worksheet, 'Report');
                XLSX.writeFile(workbook, `report_${Date.now()}.xlsx`);
            });
            return tableHTML;
        }
    }

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
        document.documentElement.classList.remove('dark'); // Force light theme
    }

    // --- Event Listeners ---
    function initEventListeners() {
        elements.newConversationBtn?.addEventListener('click', () => startNewConversation(true));
        elements.chatForm?.addEventListener('submit', handleMessageSubmit);
        elements.messageInput?.addEventListener('input', handleInputChange);
        elements.messageInput?.addEventListener('keydown', handleInputKeydown);
    }

    // --- Init ---
    initTheme();
    initEventListeners();
    showWelcomeMessage();
    updateConversationList();
    handleInputChange();
});