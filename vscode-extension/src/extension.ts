// Main extension file
import * as vscode from 'vscode';
import { registerCommands } from './commands';
import { BugFixerAPIClient } from './api-client';

let bugFixerClient: BugFixerAPIClient;
let outputChannel: vscode.OutputChannel;

export async function activate(context: vscode.ExtensionContext) {
    // Initialize output channel
    outputChannel = vscode.window.createOutputChannel('AI Bug Fixer');
    outputChannel.show(true);
    outputChannel.appendLine('AI Bug Fixer extension activated!');

    // Get backend URL from configuration
    const config = vscode.workspace.getConfiguration('aiBugFixer');
    const backendUrl = config.get<string>('backendUrl', 'http://localhost:5000');

    // Initialize API client
    bugFixerClient = new BugFixerAPIClient(backendUrl, outputChannel);

    // Check if backend is available
    try {
        const health = await bugFixerClient.checkHealth();
        outputChannel.appendLine(`✓ Connected to AI Bug Fixer backend at ${backendUrl}`);
    } catch (error) {
        outputChannel.appendLine(`✗ Failed to connect to backend at ${backendUrl}`);
        outputChannel.appendLine('Make sure backend is running: python backend/app.py');
        vscode.window.showWarningMessage(
            'AI Bug Fixer backend not available. Make sure it is running at ' + backendUrl
        );
    }

    // Register commands
    registerCommands(context, bugFixerClient, outputChannel);

    outputChannel.appendLine('Ready to fix code errors!');
}

export function deactivate() {
    outputChannel.appendLine('AI Bug Fixer extension deactivated');
    outputChannel.dispose();
}
