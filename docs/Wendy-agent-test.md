# Wendy the Weather Agent test scenario

This is a prototype test scenario setup to explore whether an AI Agent can be defined to cooperate 
with a Human Agent to solve a Tool-calling task.

Here are the participants in this staged test:

Participants:
- WeatherTool: Weather forecast Tool provided via Accuweather MCP Server
- Wendy: An OpenAI Agent instantiation that is initialized with the WeatherTool as its 'Tool' 
  component, and an 'instruction' that instructs the Agent to obtain a forecast of today's high 
  forecasted temperature (in Fahrenheit) from the 'location' passed into the weather tool. Wendy is 
  to determine the location from the input prompt. However, if the location provided in the initial 
  prompt is ambiguous, missing, or in any way unclear, Wendy is instructed to engage in a 
  conversation with the Human Agent in order to resolve the uncertainty and agree on a location to 
  pass to the weather tool. This will either suceed, or else either the AI Agent (Wendy) or the 
  Human Agent (Randy) will declare failure and the process will terminate with a failure result.
- Randy: Me, the Human Agent.
- CC: Claude Code. In this initial version of the scenario, there is no means for Wendy and Randy to 
  communicate, CC will act as a go-between, analogous to a translator at the United Nations, to pass 
  English text messages (prompts & responses) between Wendy and Randy. This interaction would take 
  place in the Claude Code terminal interaction window here in JetBrains IntelliJ. CC is not to 
  alter the message text in any way, other than to monitor the messages for keywords that would terminate the 
  conversation.

After the initial weather request, Wendy should ask Randy for either another location to obtain 
temperature forecast for, or end the conversation with the stop-word "Bye", which would terminate 
the weather forecast conversation.

