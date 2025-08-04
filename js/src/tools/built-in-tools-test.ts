import { openai, createSiloSlayerAgent } from '../openai-setup';

/**
 * Test built-in OpenAI tools to see what's actually available
 */
async function testBuiltInTools() {
  console.log('🔧 Testing OpenAI Built-in Tools...');
  
  try {
    // Test 1: Simple chat completion with function calling
    console.log('\n1. Testing basic function calling...');
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system", 
          content: "You are a helpful assistant that can perform various tasks. If you need to perform calculations or analysis, use the available tools."
        },
        {
          role: "user", 
          content: "Calculate the square root of 2 to 10 decimal places"
        }
      ],
      tools: [
        {
          type: "function",
          function: {
            name: "calculate",
            description: "Perform mathematical calculations",
            parameters: {
              type: "object",
              properties: {
                expression: {
                  type: "string",
                  description: "Mathematical expression to evaluate"
                }
              },
              required: ["expression"]
            }
          }
        }
      ],
      tool_choice: "auto"
    });

    const message = completion.choices[0].message;
    console.log('📝 Response:', message.content);
    
    if (message.tool_calls) {
      console.log('🔧 Tool calls requested:', message.tool_calls.map(tc => ({
        name: tc.function.name,
        args: tc.function.arguments
      })));
    }

    // Test 2: Check what tools are available in Agent SDK
    console.log('\n2. Testing OpenAI Agent SDK...');
    const agent = createSiloSlayerAgent();
    console.log('✅ Agent created with model:', agent.model);
    console.log('🔧 Available agent properties:', Object.getOwnPropertyNames(agent));
    
    return { success: true };
    
  } catch (error) {
    console.error('❌ Built-in tools test failed:', error);
    return { success: false, error };
  }
}

// Simple math tool implementation for testing
export function createMathTool() {
  return {
    name: "calculate",
    description: "Perform mathematical calculations",
    parameters: {
      type: "object",
      properties: {
        expression: {
          type: "string", 
          description: "Mathematical expression to evaluate"
        }
      },
      required: ["expression"]
    },
    function: (args: { expression: string }) => {
      try {
        // Simple eval for testing (unsafe for production)
        const result = eval(args.expression);
        return { result, expression: args.expression };
      } catch (error) {
        return { error: `Cannot evaluate: ${args.expression}` };
      }
    }
  };
}

testBuiltInTools().catch(console.error);