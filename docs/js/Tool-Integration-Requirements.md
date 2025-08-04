# Tool Integration Requirements - Definitive Specification

## Minimal Tool Schema Requirements

### OpenAI Function Tool Format (REQUIRED FIELDS)
```typescript
{
  type: "function",                    // REQUIRED: Must be "function"
  function: {                         // REQUIRED: Function definition
    name: "tool_name",                // REQUIRED: Unique identifier
    description: "What it does",      // REQUIRED: Max 1024 chars
    parameters: {                     // REQUIRED: Parameter schema
      type: "object",                 // REQUIRED: Must be "object"
      properties: {                   // REQUIRED: Parameter definitions
        param: {
          type: "string",
          description: "Parameter desc"
        }
      },
      required: ["param"]             // OPTIONAL: Required params array
    }
  }
}
```

### MCP Tool Format (REQUIRED FIELDS)
```typescript
{
  name: "tool_name",                  // REQUIRED: Unique identifier
  inputSchema: {                      // REQUIRED: JSON Schema
    type: "object",                   // REQUIRED: Must be "object"
    properties: {                     // OPTIONAL: Parameter definitions
      param: {
        type: "string",
        description: "Parameter desc"
      }
    },
    required: ["param"]               // OPTIONAL: Required params array
  },
  description: "What it does"         // OPTIONAL: Human-readable description
}
```

## Tool Registration Process

### OpenAI - Static Registration
```typescript
// Tools passed directly in API call
const completion = await openai.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [...],
  tools: [toolDefinition],           // Tools registered here
  tool_choice: "auto"
});
```

### MCP - Dynamic Discovery  
```typescript
// Tools discovered from server
const client = new Client({...});
await client.connect(transport);
const { tools } = await client.listTools();    // Discovery
const result = await client.callTool({...});   // Invocation
```

## Security Requirements (2025 Standards)

### Authentication
- **OpenAI**: API keys via environment variables only
- **MCP**: OAuth 2.1 with PKCE for production systems
- **Never**: Hard-code credentials in source code

### Validation
```typescript
// REQUIRED: Input validation pattern
function safeTool(args: any) {
  // 1. Validate inputs
  if (!args.param || typeof args.param !== 'string') {
    return { error: "Invalid parameter" };
  }
  
  // 2. Implement timeout (5 seconds default)
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Timeout')), 5000)
  );
  
  // 3. Process with error handling
  try {
    const result = await Promise.race([
      actualProcessing(args.param),
      timeoutPromise
    ]);
    return { success: true, result };
  } catch (error) {
    return { error: `Processing failed: ${error.message}` };
  }
}
```

## Quality Standards

### Error Response Format
```typescript
// SUCCESS response
{ success: true, result: "data" }

// ERROR response  
{ error: "Descriptive error message", success: false }
```

### Required Practices
1. **Input Validation**: Check all parameters before processing
2. **Timeout Management**: 5-second default timeout for operations
3. **Error Handling**: Consistent error object structure
4. **Security Sanitization**: Especially for file/system operations
5. **Logging**: Audit trail for tool invocations

## Current Implementation Status

### ✅ Working (In Your Codebase)
- OpenAI function calling schema ✓
- Basic input validation ✓ 
- Error handling patterns ✓
- Safe mode for system commands ✓

### ⚠️ Needs Enhancement
- Timeout handling for system commands
- Remove `eval()` usage (noted as unsafe)
- Add MCP tool schema support
- Implement OAuth 2.1 for production MCP

## Tool Source Evaluation Criteria

### NPM/NPX Packages ✅ 
- **Pros**: Pre-built, tested, maintained
- **Evaluation**: Check download stats, last update, maintainer reputation
- **Security**: Review package.json for suspicious dependencies

### Vendor Tools ✅
- **Pros**: Official support, likely reliable
- **Evaluation**: Check vendor reputation, documentation quality
- **Security**: Verify authentic vendor packages

### Third-Party Websites ⚠️
- **Pros**: Variety, community contributions
- **Evaluation**: Code review required, test thoroughly
- **Security**: High scrutiny needed, sandbox testing recommended

### Custom Tools ✅
- **Pros**: Full control, specific to needs
- **Requirements**: Follow schemas above, implement quality standards
- **Security**: Your responsibility for validation and safety

## Implementation Checklist

- [ ] Tool follows correct schema (OpenAI or MCP)
- [ ] Input validation implemented
- [ ] Timeout handling (5 seconds)
- [ ] Consistent error response format
- [ ] Security sanitization for sensitive operations
- [ ] Environment variables for credentials
- [ ] Comprehensive error handling
- [ ] Logging/audit trail capability