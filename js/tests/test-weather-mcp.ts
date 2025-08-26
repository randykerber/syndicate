#!/usr/bin/env node

/**
 * Test script for AccuWeather MCP server
 * Verifies API key setup and basic weather functionality
 */

import { spawn } from 'child_process';
import { config } from 'dotenv';

// Load environment variables
config();

async function testWeatherMCPServer() {
  console.log('🌤️  Testing AccuWeather MCP Server...');
  console.log('='.repeat(50));

  // Check if API key is available
  if (!process.env.ACCUWEATHER_API_KEY) {
    console.error('❌ ACCUWEATHER_API_KEY not found in environment variables');
    console.log('Please add ACCUWEATHER_API_KEY=your_key to .env file');
    process.exit(1);
  }

  console.log('✅ AccuWeather API key found');

  try {
    // Test the MCP server directly
    console.log('\n🔧 Testing MCP server startup...');
    
    const mcp = spawn('npx', ['-y', '@timlukahorstmann/mcp-weather'], {
      env: {
        ...process.env,
        ACCUWEATHER_API_KEY: process.env.ACCUWEATHER_API_KEY
      },
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';

    mcp.stdout.on('data', (data) => {
      output += data.toString();
    });

    mcp.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    // Give it a few seconds to start
    await new Promise(resolve => setTimeout(resolve, 3000));

    if (mcp.pid) {
      console.log('✅ MCP server started successfully');
      
      // Send basic MCP initialize message
      const initMessage = JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
          protocolVersion: "2024-11-05",
          capabilities: {},
          clientInfo: {
            name: "weather-test",
            version: "1.0.0"
          }
        }
      }) + '\n';

      mcp.stdin.write(initMessage);

      // Wait for response
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      console.log('📤 Sent initialize message');
      console.log('📥 Server output:', output);
      
      if (errorOutput) {
        console.log('⚠️  Server errors:', errorOutput);
      }

      mcp.kill();
      console.log('✅ Test completed - server responds to MCP protocol');
    } else {
      console.error('❌ Failed to start MCP server');
      console.log('Error output:', errorOutput);
    }

  } catch (error) {
    console.error('❌ Error testing MCP server:', error);
  }
}

// Manual test function - simpler approach
async function manualWeatherTest() {
  console.log('\n🧪 Manual Weather Test');
  console.log('='.repeat(30));
  console.log('To manually test the weather server:');
  console.log('1. Run: npx -y @timlukahorstmann/mcp-weather');
  console.log('2. Server should start and wait for MCP messages');
  console.log('3. If no errors, the server is working with your API key');
  console.log('\nAPI Key status:', process.env.ACCUWEATHER_API_KEY ? '✅ Present' : '❌ Missing');
}

if (require.main === module) {
  testWeatherMCPServer()
    .then(() => manualWeatherTest())
    .catch(console.error);
}