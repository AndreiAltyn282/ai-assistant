const vscode = require('vscode');
const axios = require('axios');

const API_URL = 'http://localhost:8000/ask';

function activate(context) {
    console.log('✅ AI Assistant активирован!');

    let askCommand = vscode.commands.registerCommand('ai-assistant.ask', async function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('❌ Нет активного редактора!');
            return;
        }

        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);

        if (!selectedText) {
            vscode.window.showErrorMessage('❌ Выделите код или текст!');
            return;
        }

        const question = await vscode.window.showInputBox({
            prompt: 'Что вы хотите спросить?',
            placeHolder: 'Например: Что делает этот код?',
            title: 'AI Assistant'
        });

        if (!question) return;

        await askAI(selectedText, question);
    });

    context.subscriptions.push(askCommand);
}

async function askAI(code, question) {
    try {
        vscode.window.showInformationMessage('🤖 Отправка запроса...');

        const response = await axios.post(API_URL, {
            code: code,
            question: question
        }, { timeout: 60000 });

        const answer = response.data.answer || 'Нет ответа';

        const panel = vscode.window.createWebviewPanel(
            'aiAssistant',
            '🤖 AI Assistant',
            vscode.ViewColumn.Beside,
            { enableScripts: true }
        );

        panel.webview.html = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: 'Segoe UI', sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
                .code { background: #2d2d2d; padding: 15px; border-radius: 8px; white-space: pre-wrap; }
                .answer { background: #2d2d2d; padding: 15px; border-radius: 8px; margin-top: 10px; }
                .label { color: #888; font-size: 12px; margin-top: 10px; }
                pre { background: #2d2d2d; padding: 15px; border-radius: 8px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <h2>🤖 AI Assistant</h2>
            <div class="label">📝 Код:</div>
            <div class="code"><pre>${escapeHtml(code)}</pre></div>
            <div class="label">❓ Вопрос: ${question}</div>
            <div class="answer">${escapeHtml(answer)}</div>
        </body>
        </html>
        `;

        vscode.window.showInformationMessage('✅ Готово!');

    } catch (error) {
        vscode.window.showErrorMessage(`❌ Ошибка: ${error.message}`);
    }
}

function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/\n/g, '<br>');
}

function deactivate() {}

module.exports = { activate, deactivate };
