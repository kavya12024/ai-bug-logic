// Commands implementation
import * as vscode from 'vscode';
import { BugFixerAPIClient } from './api-client';
import * as path from 'path';
import * as fs from 'fs';

export function registerCommands(
    context: vscode.ExtensionContext,
    apiClient: BugFixerAPIClient,
    outputChannel: vscode.OutputChannel
) {
    // Fix current file
    context.subscriptions.push(
        vscode.commands.registerCommand('aiBugFixer.fixFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No file is currently open');
                return;
            }

            const filePath = editor.document.uri.fsPath;
            const language = getLanguageFromFile(filePath);

            if (!language) {
                vscode.window.showErrorMessage('Unsupported file type');
                return;
            }

            outputChannel.appendLine(`\n${'='.repeat(60)}`);
            outputChannel.appendLine(`Fixing file: ${filePath}`);
            outputChannel.appendLine(`Language: ${language}`);
            outputChannel.appendLine('='.repeat(60));

            try {
                // Save current file
                await editor.document.save();

                // Show progress
                vscode.window.showInformationMessage('🔧 Starting code fix...');

                const config = vscode.workspace.getConfiguration('aiBugFixer');
                const maxAttempts = config.get<number>('maxAttempts', 5);
                const timeout = config.get<number>('timeout', 30);

                // Call API
                const result = await apiClient.fixFile(filePath, language, maxAttempts, timeout);

                // Display results
                displayFixResults(result, filePath, outputChannel);

                // Reload file if fixed
                if (result.summary.successful) {
                    await vscode.commands.executeCommand('workbench.action.revertAndCloseActiveEditor');
                    await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(filePath));
                    vscode.window.showInformationMessage('✓ Code fixed successfully!');
                } else {
                    vscode.window.showWarningMessage('⚠ Could not automatically fix all errors');
                }

            } catch (error: any) {
                outputChannel.appendLine(`Error: ${error.message}`);
                vscode.window.showErrorMessage(`Failed to fix file: ${error.message}`);
            }
        })
    );

    // Fix all files in workspace
    context.subscriptions.push(
        vscode.commands.registerCommand('aiBugFixer.fixWorkspace', async () => {
            const config = vscode.workspace.getConfiguration('aiBugFixer');
            const maxAttempts = config.get<number>('maxAttempts', 5);
            const timeout = config.get<number>('timeout', 30);

            outputChannel.appendLine(`\n${'='.repeat(60)}`);
            outputChannel.appendLine('Fixing all files in workspace...');
            outputChannel.appendLine('='.repeat(60));

            // Find all supported files
            const pythonFiles = await vscode.workspace.findFiles('**/*.py');
            const jsFiles = await vscode.workspace.findFiles('**/*.{js,ts}');
            const cppFiles = await vscode.workspace.findFiles('**/*.{cpp,c,h,hpp}');

            const allFiles = [...pythonFiles, ...jsFiles, ...cppFiles];

            if (allFiles.length === 0) {
                vscode.window.showInformationMessage('No supported code files found');
                return;
            }

            outputChannel.appendLine(`Found ${allFiles.length} files to fix`);

            let fixedCount = 0;
            let failedCount = 0;

            for (const fileUri of allFiles) {
                const filePath = fileUri.fsPath;
                const language = getLanguageFromFile(filePath);

                if (!language) continue;

                try {
                    outputChannel.appendLine(`\nProcessing: ${path.basename(filePath)}`);
                    const result = await apiClient.fixFile(filePath, language, maxAttempts, timeout);

                    if (result.summary.successful) {
                        fixedCount++;
                        outputChannel.appendLine(`  ✓ Fixed`);
                    } else {
                        failedCount++;
                        outputChannel.appendLine(`  ✗ Could not fix`);
                    }
                } catch (error: any) {
                    failedCount++;
                    outputChannel.appendLine(`  ✗ Error: ${error.message}`);
                }
            }

            outputChannel.appendLine(`\n${'='.repeat(60)}`);
            outputChannel.appendLine(`Summary: ${fixedCount} fixed, ${failedCount} failed`);
            outputChannel.appendLine('='.repeat(60));

            vscode.window.showInformationMessage(
                `Workspace fix complete: ${fixedCount} fixed, ${failedCount} failed`
            );
        })
    );

    // Show logs
    context.subscriptions.push(
        vscode.commands.registerCommand('aiBugFixer.showLogs', () => {
            outputChannel.show();
        })
    );

    // Stop operation
    context.subscriptions.push(
        vscode.commands.registerCommand('aiBugFixer.stopFixer', () => {
            outputChannel.appendLine('Stop command received');
            vscode.window.showInformationMessage('Operation stopped');
        })
    );
}

function getLanguageFromFile(filePath: string): string | null {
    const ext = path.extname(filePath).toLowerCase();

    const languageMap: { [key: string]: string } = {
        '.py': 'python',
        '.js': 'nodejs',
        '.ts': 'nodejs',
        '.jsx': 'nodejs',
        '.tsx': 'nodejs',
        '.cpp': 'cpp',
        '.c': 'cpp',
        '.h': 'cpp',
        '.hpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
    };

    return languageMap[ext] || null;
}

function displayFixResults(result: any, filePath: string, outputChannel: vscode.OutputChannel) {
    const summary = result.summary;

    outputChannel.appendLine(`\nResults:`);
    outputChannel.appendLine(`  Total Attempts: ${summary.total_attempts}`);
    outputChannel.appendLine(`  Status: ${summary.successful ? '✓ SUCCESS' : '✗ FAILED'}`);
    outputChannel.appendLine(`  Total Errors Found: ${summary.total_errors_found}`);
    outputChannel.appendLine(`  Final Exit Code: ${summary.final_exit_code}`);

    // Display iterations
    if (summary.iterations && summary.iterations.length > 0) {
        outputChannel.appendLine('\nIteration Details:');
        for (const iter of summary.iterations) {
            outputChannel.appendLine(
                `  Attempt ${iter.iteration}: ${iter.success ? '✓' : '✗'} (${iter.errors_count} errors)`
            );
            for (const error of iter.errors) {
                outputChannel.appendLine(`    - ${error.type}: ${error.message}`);
            }
        }
    }
}
