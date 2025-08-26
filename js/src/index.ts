import { testOpenAISetup } from '../tests/openai-setup';

async function main() {
  console.log('=� SiloSlayer Syndicate - JavaScript Edition');
  console.log('============================================');
  
  // Test OpenAI setup
  const result = await testOpenAISetup();
  
  if (result.success) {
    console.log(' All systems operational!');
    console.log(`> SiloSlayer Agent ID: ${result.agentId}`);
  } else {
    console.error('L Setup failed:', result.error);
  }
}

main().catch(console.error);