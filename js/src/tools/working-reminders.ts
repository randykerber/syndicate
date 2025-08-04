import { execFileSync } from 'child_process';

export interface WorkingReminderOptions {
  title: string;
  notes?: string;
}

export interface WorkingReminderResult {
  success: boolean;
  message: string;
  reminderId?: string;
}

/**
 * Create a reminder using the working AppleScript approach
 */
export function createWorkingReminder(options: WorkingReminderOptions): WorkingReminderResult {
  try {
    const { title, notes } = options;
    
    // Use the exact format that worked in terminal
    let script = `tell application "Reminders" to make new reminder with properties {name:"${title}"`;
    
    if (notes) {
      script += `, body:"${notes}"`;
    }
    
    script += `}`;
    
    console.log('🔄 Executing AppleScript:', script);
    
    // Use execFileSync with osascript directly
    const result = execFileSync('osascript', ['-e', script], { 
      encoding: 'utf8',
      timeout: 3000
    }).trim();
    
    console.log('✅ AppleScript result:', result);
    
    return {
      success: true,
      message: `Reminder "${title}" created successfully`,
      reminderId: result
    };
    
  } catch (error: any) {
    console.log('❌ AppleScript error:', error.message);
    return {
      success: false,
      message: `Failed to create reminder: ${error.message}`
    };
  }
}

/**
 * Test the working reminder functionality
 */
export function testWorkingReminderTool() {
  console.log('🧪 Testing Working Apple Reminders Tool\n');
  
  const testReminder = createWorkingReminder({
    title: 'SSS Working Test',
    notes: 'Created by working reminder tool'
  });
  
  console.log('📝 Final Result:', testReminder);
  return testReminder;
}

// Run test if this file is executed directly
if (require.main === module) {
  testWorkingReminderTool();
}