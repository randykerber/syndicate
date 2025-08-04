import OpenAI from 'openai';
import { Agent } from '@openai/agents';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Regular OpenAI API client setup
 * For direct API calls (chat completions, embeddings, etc.)
 */
export const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

/**
 * Example: Simple chat completion using regular OpenAI API
 */
export async function simpleChatCompletion(message: string): Promise<string> {
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are a helpful assistant for the SiloSlayer Syndicate information management system." },
        { role: "user", content: message }
      ],
      max_tokens: 500,
    });

    return completion.choices[0]?.message?.content || "No response received";
  } catch (error) {
    console.error('OpenAI API error:', error);
    throw error;
  }
}

/**
 * Example: Basic agent using OpenAI Agents SDK
 * Similar to the Python project's agent patterns
 */
export function createSiloSlayerAgent() {
  try {
    const agent = new Agent({
      name: 'SiloSlayerAgent',
      model: "gpt-4o-mini",
      instructions: `You are the SiloSlayer agent, part of the SiloSlayer Syndicate system.
        Your mission is to help users liberate information from app silos and organize it intelligently.
        
        Key capabilities:
        - Analyze content and suggest optimal routing (Obsidian, Drafts, Bear, etc.)
        - Extract key information from text fragments
        - Provide intelligent categorization and tagging
        - Help with content triage and organization`,
    });

    return agent;
  } catch (error) {
    console.error('Agent creation error:', error);
    throw error;
  }
}

/**
 * Test function to verify both setups work
 */
export async function testOpenAISetup() {
  console.log('🔧 Testing OpenAI setup...');
  
  try {
    // Test regular API
    console.log('📡 Testing regular OpenAI API...');
    const chatResponse = await simpleChatCompletion("Hello! Can you help me organize my information chaos?");
    console.log('✅ Chat API response:', chatResponse.substring(0, 100) + '...');

    // Test Agents SDK
    console.log('🤖 Testing OpenAI Agents SDK...');
    const agent = createSiloSlayerAgent();
    console.log('✅ Agent created successfully, name:', agent.name);

    return { success: true, agentId: 'silo-slayer-agent' };
  } catch (error) {
    console.error('❌ Setup test failed:', error);
    return { success: false, error };
  }
}