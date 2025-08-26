# The Plan

Next steps ideas:

### Integrate Input Note into Obsidian

Create a Syndicate Agent (OpenAI Agent).
Inputs
- An input note (a chunk of text). Could be a Drafts note, transcribed text from superWhisper, 
  something via Siri. The source of the text generally shouldn't matter.
- Text instruction or guidance as to what to extract or what to do with it.
Result
- One of the Obsidian vaults is updated with the new content. Might be a new Obsidian note, or might 
  be integrated into existing notes.
- One possible fallback is that a new note with the input note content is added to a specified 
  "Inbox" folder, and the note name added to an "Inbox" note.
- In case of failure, the Input Note is placed into a Failure Bucket at Obsidian or Drafts, and 
  annotated with what was determined and what failed to be determined in order to integrate into 
  Obsidian.
How
- Various Obsidian capabilities will be exposed as Agent Tools, likely via MCP. I know I've seen one 
  or more existing tools that promise something like this. These tools would have capabilities such 
  as adding a new Obsidian note, adding text to an existing obsidian note after a specified section, 
  adding tags or properties, etc.
- The Syndicate Agent would be instructed to engage with the Human Agent to resolve ambiguities, 
  obtain missing pieces of information, or ask for advice, in order to obtain proper values for the 
  parameters needed in order to complete the chosen Tool call.

### Add Entity to Obsidian

Background

Currently, when I add a new entity or chunk of information to Obsidian, there are often a number of 
boilerplate actions that I take for which it would be nice to have much of it automated. For example,
if there's a new stock or ETF that I encounter that I want to add to Obsidian, here's an example of 
steps I often take. First, in order to add a stock, I need to determine the Ticker Symbol. Sometimes 
I already know it. Other times I go to koyfin.com and search by name. Say for example I'm adding a 
page for Block, Inc, which has Ticker Symbol "XYZ". I'll often start by creating a blank page in the 
'Fin' vault. I then name it "XYZ.md". I then move it to the "Tickers" folder. The first line of the 
page is the company name (or Fund name) as a H1 header. If the stock is an ETF, I add the '#etf' tag.
If it's an equity, I add a line with the Sector and Industry, followed by a line with the company 
location. That is followed by the canned company or fund description, which is preceded by '> ' 
markdown formatting. This description text I generally copy and paste from Koyfin, but the same text 
descrition is provided by pretty much every service that provides investing data, such as Koyfin, 
Yahoo Finance, FMP (Financial Modeling Prep), Polygon, and other investing sites. The Sector and 
Industry are also available from such sources. I then create a link to the new stock from the page 
for that Industry, and from the page for that state, province, country to the stock. And sometimes 
add a few other bits of info about the company or fund like Market Cap, P/E ratio, annual sales, 
dividend, expense ratio (for ETFs) etc. All of this info is available from investing sources, but 
currently I enter it all by hand. Would like an Agent to do a lot of this work for me.

How

Would need to implement or import tools that can interact with the API of an investing site, such as 
FMP or Yahoo Finance.

Would need to expose Tools that can make the needed modifications to Obsidian vaults and pages.

Would need a Syndicate Agent could extract the company from the input text, query the investing data 
tools to obtain the needed pieces of information (e.g., Industry, market cap, description, etc.), be 
able to carry out the steps, and be able to cooperate with the human agent to resolve gaps.

### Task Management Helper

Background

Currently, managing tasks, reminders, to-dos, deadlines, calendar events, and saved notes is a major 
annoyance and a mess. The artifacts are spread across multiple apps that are individual silos, each 
with their own weaknesses. In order to do something, I have to remember which app it's in. Tasks are 
frequently forgotten until it's too late to do something about them. Important things are missed. 
Some can't be adequately addressed until you're in a certain location or require a piece of info I 
don't have yet. Important tasks are lost in a pile of less important. Some are best addressed as a 
batch of similar minor tasks to be dealt with all at once, but to existing apps it's just a big pile 
of indistinguishable independent tasks. The apps have no natural languate understanding. In order to 
not miss some task, you decide to turn it into a reminder. Now you keep getting nagged with it at 
the wrong times, where you're either forced to deal with it, and interrupt what flow you have with 
the current task, or dismiss it and risk forgetting about it completely.

### Content Consumption Management


