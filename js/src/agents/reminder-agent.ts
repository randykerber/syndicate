import { Agent, run, tool } from '@openai/agents';
import { z } from 'zod';
import { createWorkingReminder } from '../tools/working-reminders.js';

/**
 * Tool function that the OpenAI agent can call to create reminders
 */
const createReminderTool = tool({
  name: 'create_reminder',
  description: 'Create a new reminder in Apple Reminders app',
  parameters: z.object({
    title: z.string().describe('The title/name of the reminder'),
    notes: z.string().nullable().describe('Optional notes/body text for the reminder')
  }),
  execute: async (args) => {
    console.log('🔧 Reminder tool called with:', args);
    const reminderOptions = {
      title: args.title,
      notes: args.notes || undefined
    };
    const result = createWorkingReminder(reminderOptions);
    console.log('📋 Reminder tool result:', result);
    return result;
  }
});

/**
 * Create an O-Agent specialized for reminder management
 */
export function createReminderAgent() {
  const agent = new Agent({
    name: 'ReminderAgent',
    model: 'gpt-4o-mini',
    instructions: `You are a helpful assistant that can create reminders in Apple Reminders app.
    
    When a user asks you to create a reminder, use the create_reminder tool with:
    - title: A clear, concise title for the reminder
    - notes: Optional additional details or context
    
    Always confirm when you've successfully created a reminder.`,
    tools: [createReminderTool]
  });
  
  return agent;
}

/**
 * Test the reminder agent
 */
export async function testReminderAgent() {
  console.log('🤖 Testing Reminder O-Agent\n');
  
  const agent = createReminderAgent();
  
  // Test with a simple request
  const testRequest = "Create a reminder to 'Call mom tomorrow' with a note saying 'Birthday planning discussion'";
  
  console.log('📝 Sending request to agent:', testRequest);
  
  try {
    const response = await run(agent, testRequest);
    console.log('🎯 Agent response:', response);
    return response;
  } catch (error: any) {
    console.log('❌ Agent error:', error);
    return { error: error.message };
  }
}

// Run test if this file is executed directly
if (require.main === module) {
  testReminderAgent().then(() => {
    console.log('✅ Reminder agent test complete');
  });
}