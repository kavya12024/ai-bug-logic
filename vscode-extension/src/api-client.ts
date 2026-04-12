// API client for communication with backend
import * as vscode from 'vscode';

export class BugFixerAPIClient {
    private baseUrl: string;
    private outputChannel: vscode.OutputChannel;

    constructor(baseUrl: string, outputChannel: vscode.OutputChannel) {
        this.baseUrl = baseUrl;
        this.outputChannel = outputChannel;
    }

    async checkHealth(): Promise<any> {
        return this.makeRequest('GET', '/health');
    }

    async fixFile(
        filePath: string,
        language: string,
        maxAttempts: number,
        timeout: number
    ): Promise<any> {
        return this.makeRequest('POST', '/api/fix-file', {
            file_path: filePath,
            language: language,
            max_attempts: maxAttempts,
            timeout: timeout
        });
    }

    async cloneRepository(repoUrl: string, repoName?: string): Promise<any> {
        return this.makeRequest('POST', '/api/clone-repo', {
            repo_url: repoUrl,
            repo_name: repoName
        });
    }

    async getFile(repoPath: string, filePath: string): Promise<any> {
        return this.makeRequest('GET', '/api/get-file', null, {
            repo_path: repoPath,
            file_path: filePath
        });
    }

    async updateFile(repoPath: string, filePath: string, content: string): Promise<any> {
        return this.makeRequest('POST', '/api/update-file', {
            repo_path: repoPath,
            file_path: filePath,
            content: content
        });
    }

    async listFiles(repoPath: string, extensions?: string): Promise<any> {
        const params: { [key: string]: string } = {
            repo_path: repoPath
        };
        if (extensions) {
            params.extensions = extensions;
        }
        return this.makeRequest('GET', '/api/list-files', null, params);
    }

    private async makeRequest(
        method: string,
        endpoint: string,
        body?: any,
        queryParams?: { [key: string]: string }
    ): Promise<any> {
        try {
            let url = `${this.baseUrl}${endpoint}`;

            // Add query parameters
            if (queryParams) {
                const params = new URLSearchParams(queryParams);
                url += `?${params.toString()}`;
            }

            const options: any = {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            if (body) {
                options.body = JSON.stringify(body);
            }

            const response = await fetch(url, options);

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText} (${response.status})`);
            }

            return await response.json();
        } catch (error: any) {
            this.outputChannel.appendLine(`API Error: ${error.message}`);
            throw error;
        }
    }
}
