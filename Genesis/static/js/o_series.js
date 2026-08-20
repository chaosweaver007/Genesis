(() => {
    'use strict';

    const state = {
        persona: 'steven',
        sessionId: getOrCreateSessionId(),
        sending: false,
    };

    const form = document.getElementById('chat-form');
    const input = document.getElementById('message-input');
    const messages = document.getElementById('messages');
    const sendButton = document.getElementById('send-button');
    const charCount = document.getElementById('char-count');
    const clearButton = document.getElementById('clear-chat');
    const refreshStatusButton = document.getElementById('refresh-status');
    const liveState = document.getElementById('live-state');
    const liveLabel = document.getElementById('live-label');
    const chatTitle = document.getElementById('chat-title');
    const messageTemplate = document.getElementById('message-template');

    document.getElementById('session-id').textContent = state.sessionId;

    document.querySelectorAll('[data-persona]').forEach((button) => {
        button.addEventListener('click', () => selectPersona(button.dataset.persona));
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        await sendMessage();
    });

    input.addEventListener('input', () => {
        charCount.textContent = `${input.value.length} / 4000`;
        autoGrow(input);
    });

    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            form.requestSubmit();
        }
    });

    clearButton.addEventListener('click', () => {
        messages.innerHTML = '';
        appendMessage({
            label: 'GENESIS',
            text: 'Conversation view cleared. The backend remains stateless and no server-side conversation memory was requested.',
            kind: 'system',
        });
    });

    refreshStatusButton.addEventListener('click', loadStatus);

    function uuid() {
        if (window.crypto && typeof window.crypto.randomUUID === 'function') {
            return window.crypto.randomUUID();
        }
        const bytes = new Uint8Array(16);
        window.crypto.getRandomValues(bytes);
        bytes[6] = (bytes[6] & 0x0f) | 0x40;
        bytes[8] = (bytes[8] & 0x3f) | 0x80;
        const hex = [...bytes].map((b) => b.toString(16).padStart(2, '0')).join('');
        return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
    }

    function getOrCreateSessionId() {
        const key = 'genesis-o-series-session';
        let id = sessionStorage.getItem(key);
        if (!id) {
            id = uuid();
            sessionStorage.setItem(key, id);
        }
        return id;
    }

    function selectPersona(persona) {
        if (!['steven', 'sarah'].includes(persona)) return;
        state.persona = persona;
        document.querySelectorAll('[data-persona]').forEach((button) => {
            const active = button.dataset.persona === persona;
            button.classList.toggle('active', active);
            button.setAttribute('aria-pressed', String(active));
        });
        chatTitle.textContent = persona === 'steven' ? 'Steven · Gate 0' : 'Sarah AI · Gate 0';
        input.placeholder = persona === 'steven'
            ? 'Send a message to Steven through Gate 0…'
            : 'Send a message to Sarah AI through Gate 0…';
        input.focus();
    }

    async function loadStatus() {
        setLiveState('loading', 'Connecting');
        refreshStatusButton.disabled = true;
        try {
            const response = await fetch('/api/o-series/status', {
                headers: { 'Accept': 'application/json' },
                cache: 'no-store',
            });
            if (!response.ok) throw new Error(`Status ${response.status}`);
            const data = await response.json();
            renderStatus(data);
            setLiveState('online', 'Gate online');
        } catch (error) {
            setLiveState('error', 'Gate unavailable');
        } finally {
            refreshStatusButton.disabled = false;
        }
    }

    function renderStatus(data) {
        document.querySelectorAll('[data-status-key]').forEach((element) => {
            const key = element.dataset.statusKey;
            let value = data[key];
            if (Array.isArray(value)) value = value.length ? value.join(', ') : 'none';
            if (typeof value === 'boolean') value = value ? 'monotonic' : 'off';
            if (value === undefined || value === null || value === '') value = 'unknown';
            element.textContent = String(value);
        });
        document.getElementById('pipeline-version').textContent = data.pipeline_version || 'unknown';
        document.getElementById('policy-version').textContent = data.policy_version || 'unknown';
    }

    function setLiveState(mode, label) {
        liveState.classList.remove('online', 'error');
        if (mode === 'online') liveState.classList.add('online');
        if (mode === 'error') liveState.classList.add('error');
        liveLabel.textContent = label;
    }

    async function sendMessage() {
        const text = input.value.trim();
        if (!text || state.sending) return;

        appendMessage({ label: 'YOU', text, kind: 'user' });
        input.value = '';
        charCount.textContent = '0 / 4000';
        autoGrow(input);
        setSending(true);

        const envelope = {
            request_id: uuid(),
            session_id: state.sessionId,
            message: text,
            persona: state.persona,
            consent_level: 'private',
            collective_learning: false,
            pipeline_mode: 'shadow',
        };

        try {
            const response = await fetch('/api/o-series/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(envelope),
            });
            const data = await response.json().catch(() => ({}));
            const label = state.persona === 'steven' ? 'STEVEN' : 'SARAH AI';
            const responseText = data.response || data.error || `Request failed with HTTP ${response.status}.`;
            const metadata = buildMetadata(data, response.status);
            appendMessage({
                label,
                text: responseText,
                kind: response.ok ? 'assistant' : 'error',
                metadata,
            });
        } catch (error) {
            appendMessage({
                label: 'GENESIS',
                text: 'The browser could not reach Gate 0. Make sure the Flask process is still running.',
                kind: 'error',
            });
            setLiveState('error', 'Gate unavailable');
        } finally {
            setSending(false);
            input.focus();
        }
    }

    function buildMetadata(data, statusCode) {
        const metadata = { http_status: statusCode };
        for (const key of ['gate_zero', 'reflection', 'revision_count', 'context_manifest', 'witness_receipt']) {
            if (data[key] !== undefined) metadata[key] = data[key];
        }
        return Object.keys(metadata).length > 1 ? metadata : null;
    }

    function appendMessage({ label, text, kind, metadata = null }) {
        const fragment = messageTemplate.content.cloneNode(true);
        const article = fragment.querySelector('.message');
        const labelNode = fragment.querySelector('.message-label');
        const bodyNode = fragment.querySelector('.message-body');
        const details = fragment.querySelector('.receipt-details');
        const pre = fragment.querySelector('pre');

        if (kind === 'user') article.classList.add('user-message');
        if (kind === 'system') article.classList.add('system-message');
        if (kind === 'error') article.classList.add('error-message');

        labelNode.textContent = label;
        bodyNode.textContent = text;

        if (metadata) {
            details.hidden = false;
            pre.textContent = JSON.stringify(metadata, null, 2);
        }

        messages.appendChild(fragment);
        messages.scrollTop = messages.scrollHeight;
    }

    function setSending(sending) {
        state.sending = sending;
        sendButton.disabled = sending;
        sendButton.querySelector('span').textContent = sending ? 'Sending' : 'Send';
    }

    function autoGrow(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
    }

    loadStatus();
})();
