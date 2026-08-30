(() => {
    'use strict';

    const RECEIPT_KEY = 'genesis-sovereignty-receipts';
    const FROZEN_KEY = 'genesis-sovereignty-frozen';

    const sessionId = document.getElementById('session-id')?.textContent?.trim() || 'unknown-session';
    const form = document.getElementById('chat-form');
    const input = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const personaButtons = [...document.querySelectorAll('[data-persona]')];
    const primeRefusalButton = document.getElementById('prime-refusal');
    const refusalDialog = document.getElementById('prime-refusal-dialog');
    const freezeButton = document.getElementById('freeze-session');
    const resumeButton = document.getElementById('resume-session');
    const exportButton = document.getElementById('export-consent');
    const exportFromRefusalButton = document.getElementById('export-from-refusal');
    const clearExitButton = document.getElementById('clear-exit');
    const receiptCount = document.getElementById('receipt-count');
    const receiptJson = document.getElementById('consent-receipt-json');
    const messages = document.getElementById('messages');

    const state = {
        frozen: sessionStorage.getItem(FROZEN_KEY) === 'true',
        exited: false,
        receipts: loadReceipts(),
    };

    if (!state.receipts.length) {
        recordReceipt({
            action: 'changed',
            previousState: null,
            newState: 'private-shadow',
            summary: 'Session boundary initialized: private mode, no server conversation memory writes, and collective learning off.',
        });
    } else {
        renderLatestReceipt();
    }

    if (state.frozen) {
        applyFrozenState(true, false);
    }

    form?.addEventListener('submit', (event) => {
        if (!state.frozen && !state.exited) return;
        event.preventDefault();
        event.stopImmediatePropagation();
    }, true);

    primeRefusalButton?.addEventListener('click', () => {
        if (state.exited) return;
        if (typeof refusalDialog?.showModal === 'function') {
            refusalDialog.showModal();
        } else {
            refusalDialog?.setAttribute('open', '');
        }
    });

    freezeButton?.addEventListener('click', () => {
        applyFrozenState(true, true);
        closeRefusalDialog();
    });

    resumeButton?.addEventListener('click', () => {
        applyFrozenState(false, true);
    });

    exportButton?.addEventListener('click', exportReceipts);
    exportFromRefusalButton?.addEventListener('click', () => {
        exportReceipts();
        closeRefusalDialog();
    });

    clearExitButton?.addEventListener('click', () => {
        recordReceipt({
            action: 'revoked',
            previousState: state.frozen ? 'paused' : 'private-shadow',
            newState: 'local-session-cleared',
            summary: 'Prime Refusal cleared the local browser session and disabled further requests from this page.',
        });
        downloadReceiptBundle();
        sessionStorage.clear();
        state.exited = true;
        state.frozen = true;
        applyControlState();
        renderExitMessage();
        closeRefusalDialog();
    });

    function loadReceipts() {
        try {
            const raw = sessionStorage.getItem(RECEIPT_KEY);
            if (!raw) return [];
            const parsed = JSON.parse(raw);
            return Array.isArray(parsed) ? parsed : [];
        } catch (_error) {
            return [];
        }
    }

    function persistReceipts() {
        sessionStorage.setItem(RECEIPT_KEY, JSON.stringify(state.receipts));
    }

    function uuid() {
        if (window.crypto && typeof window.crypto.randomUUID === 'function') {
            return window.crypto.randomUUID();
        }
        const bytes = new Uint8Array(16);
        window.crypto.getRandomValues(bytes);
        bytes[6] = (bytes[6] & 0x0f) | 0x40;
        bytes[8] = (bytes[8] & 0x3f) | 0x80;
        const hex = [...bytes].map((byte) => byte.toString(16).padStart(2, '0')).join('');
        return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
    }

    function recordReceipt({ action, previousState, newState, summary }) {
        const receipt = {
            id: uuid(),
            user_id: `anonymous:${sessionId}`,
            scope: 'memory',
            action,
            previous_state: previousState,
            new_state: newState,
            created_at: new Date().toISOString(),
            summary,
            shared_with: [],
            retention: 'session',
            library_status: 'none',
            worth_impact: 'none',
            powercoin_impact: 'none',
            revoke_path: 'Prime Refusal > Clear local session & exit',
            export_path: 'Sovereignty Core > Export receipt',
            server_memory_write: 'none',
            collective_learning: false,
        };
        state.receipts.push(receipt);
        persistReceipts();
        renderLatestReceipt();
        return receipt;
    }

    function renderLatestReceipt() {
        if (receiptCount) receiptCount.textContent = String(state.receipts.length);
        if (!receiptJson) return;
        const latest = state.receipts[state.receipts.length - 1];
        receiptJson.textContent = latest ? JSON.stringify(latest, null, 2) : 'No receipt yet.';
    }

    function applyFrozenState(frozen, makeReceipt) {
        const previousState = state.frozen ? 'paused' : 'private-shadow';
        state.frozen = frozen;
        sessionStorage.setItem(FROZEN_KEY, String(frozen));
        applyControlState();

        if (makeReceipt) {
            recordReceipt({
                action: frozen ? 'paused' : 'resumed',
                previousState,
                newState: frozen ? 'paused' : 'private-shadow',
                summary: frozen
                    ? 'Prime Refusal froze new requests in this browser session.'
                    : 'The user explicitly resumed requests in this browser session.',
            });
        }
    }

    function applyControlState() {
        const disabled = state.frozen || state.exited;
        if (input) input.disabled = disabled;
        if (sendButton) sendButton.disabled = disabled;
        personaButtons.forEach((button) => {
            button.disabled = disabled;
        });
        if (resumeButton) resumeButton.hidden = !state.frozen || state.exited;
        if (primeRefusalButton) primeRefusalButton.disabled = state.exited;
        document.body.classList.toggle('session-frozen', state.frozen && !state.exited);
        document.body.classList.toggle('session-exited', state.exited);
    }

    function exportReceipts() {
        if (state.exited) return;
        recordReceipt({
            action: 'exported',
            previousState: state.frozen ? 'paused' : 'private-shadow',
            newState: state.frozen ? 'paused' : 'private-shadow',
            summary: 'The user exported the session-local boundary receipt history as JSON.',
        });
        downloadReceiptBundle();
    }

    function downloadReceiptBundle() {
        const payload = {
            schema: 'genesis-consent-receipt-preview-v0.1',
            generated_at: new Date().toISOString(),
            session_id: sessionId,
            storage_notice: 'This file was generated locally in the browser. Genesis Gate 0 does not persist the conversation or this receipt bundle server-side.',
            receipts: state.receipts,
        };
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = `genesis-boundary-receipts-${sessionId.slice(0, 8)}.json`;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
    }

    function renderExitMessage() {
        if (!messages) return;
        messages.innerHTML = '';
        const article = document.createElement('article');
        article.className = 'message system-message';
        const label = document.createElement('div');
        label.className = 'message-label';
        label.textContent = 'GENESIS';
        const body = document.createElement('div');
        body.className = 'message-body';
        body.textContent = 'Local session cleared. This page will send no more requests. Close the tab to complete exit, or reload to begin a new private session.';
        article.append(label, body);
        messages.appendChild(article);
    }

    function closeRefusalDialog() {
        if (typeof refusalDialog?.close === 'function') {
            refusalDialog.close();
        } else {
            refusalDialog?.removeAttribute('open');
        }
    }
})();