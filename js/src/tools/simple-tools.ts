import { readFileSync, writeFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';
import { join } from 'path';

/**
 * Simple custom tools that we know will work
 * These become the foundation for more complex integrations
 */

export function createFileTools() {
  return [
    {
      name: "read_project_file",
      description: "Read a file from the syndicate-js project directory",
      parameters: {
        type: "object",
        properties: {
          filepath: {
            type: "string",
            description: "Path to file relative to project root"
          }
        },
        required: ["filepath"]
      },
      function: (args: { filepath: string }) => {
        try {
          const fullPath = join(process.cwd(), args.filepath);
          if (!existsSync(fullPath)) {
            return { error: `File not found: ${args.filepath}` };
          }
          const content = readFileSync(fullPath, 'utf-8');
          return { 
            filepath: args.filepath,
            content,
            size: content.length
          };
        } catch (error) {
          return { error: `Cannot read file: ${error}` };
        }
      }
    },
    
    {
      name: "write_project_file", 
      description: "Write content to a file in the syndicate-js project",
      parameters: {
        type: "object",
        properties: {
          filepath: {
            type: "string",
            description: "Path to file relative to project root"
          },
          content: {
            type: "string",
            description: "Content to write to the file"
          }
        },
        required: ["filepath", "content"]
      },
      function: (args: { filepath: string; content: string }) => {
        try {
          const fullPath = join(process.cwd(), args.filepath);
          writeFileSync(fullPath, args.content, 'utf-8');
          return {
            filepath: args.filepath,
            size: args.content.length,
            success: true
          };
        } catch (error) {
          return { error: `Cannot write file: ${error}` };
        }
      }
    }
  ];
}

export function createSystemTools() {
  return [
    {
      name: "run_command",
      description: "Execute a shell command and return the output",
      parameters: {
        type: "object", 
        properties: {
          command: {
            type: "string",
            description: "Shell command to execute"
          },
          safe: {
            type: "boolean",
            description: "Only allow safe read-only commands",
            default: true
          }
        },
        required: ["command"]
      },
      function: (args: { command: string; safe?: boolean }) => {
        // Whitelist of safe commands if safe mode is on
        const safeCommands = ['ls', 'pwd', 'whoami', 'date', 'echo', 'cat', 'head', 'tail'];
        
        if (args.safe !== false) {
          const commandWord = args.command.split(' ')[0];
          if (!safeCommands.includes(commandWord)) {
            return { error: `Command '${commandWord}' not allowed in safe mode` };
          }
        }
        
        try {
          const output = execSync(args.command, { 
            encoding: 'utf-8',
            timeout: 5000 // 5 second timeout
          });
          return {
            command: args.command,
            output: output.trim(),
            success: true
          };
        } catch (error) {
          return { 
            command: args.command,
            error: `Command failed: ${error}`,
            success: false
          };
        }
      }
    },

    {
      name: "get_env_var",
      description: "Get an environment variable value",
      parameters: {
        type: "object",
        properties: {
          name: {
            type: "string", 
            description: "Environment variable name"
          }
        },
        required: ["name"]
      },
      function: (args: { name: string }) => {
        const value = process.env[args.name];
        return {
          name: args.name,
          value: value || null,
          exists: value !== undefined
        };
      }
    }
  ];
}

// Export all tools as a combined toolkit
export function createBasicToolkit() {
  return [
    ...createFileTools(),
    ...createSystemTools()
  ];
}