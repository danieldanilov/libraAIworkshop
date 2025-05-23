---
title:
  - Libra AI Workshop
date_created_at: 2025-04-23
related:
  - "[[Ideas]]"
  - "[[2025-04-22 Split, Croatia - Libra Meetup 2025-04-29]]"
  - "[[Instructions for Generating Responses]]"
  - "[[2025-04-23]]"
type:
  - "[[Ideas]]"
  - "[[Courses]]"
tags:
  - "#ideas"
  - course
---
# Libra AI Workshop

## Learning Objectives

By the end of this workshop, you should be able to:
- Understand the capabilities and limitations of key AI tools (ChatGPT, Perplexity, Cursor) for support tasks.
- Apply basic prompt engineering techniques (like CARE) to generate helpful draft responses.
- Use Perplexity for reliable information gathering.
- Recognize the value of Cursor for scripting and complex troubleshooting organization.
- Identify potential AI pitfalls and apply verification strategies.

Repository: [danieldanilov/libraAIworkshop](https://github.com/danieldanilov/libraAIworkshop)

## ChatGPT (or Claude or Gemini..)

- How many of you are using AI already?
- Do you think there's a better way that they can utilize AI?

### Making Prompts

> There's no one single best approach. Just play around with it.

- General instructions:
	- CRAFT: Context, Role, Action, Format, Target Audience
	- RTF: Role, Task, Format
	- PGTC: Persona, Goal, Task, Context.
	- CARE: Context, Action, Result, Example
	- PAR: Problem, Action, Result.
- Prompt Maker GPT:
	- Example:
		- `I need a prompt for developing a presentation about using ai in day to day life for a support engineer.`
- Reddit: [r/ChatGPTPromptGenius](https://www.reddit.com/r/ChatGPTPromptGenius/)

***Brief Interactive Moment (Demo/Think-Pair-Share if time):***
- **Scenario:** A customer reports their checkout page is showing a generic error after updating WooCommerce, but provides no specific error message.
- **Task (1-2 min):** Think about/Draft a prompt using CARE to ask the AI for potential troubleshooting steps or clarifying questions to ask the customer.
- *(Briefly show or discuss 1-2 example prompts)*

#### Drafting Support Replies + Notes

- [[Instructions for Generating Responses]]
- [[CRAFT Based Instructions for Generation Answers]]
- [[ChatGPT Mega Meta Prompt]]

#### Export Documentation For Deeper Details

- Scheduling University
- Subscriptions University
- Public documentation
- Public Woo posts
- etc..

### ChatGPT Projects

- What are projects?
	- Custom Instructions
	- Ability to upload files

## Perplexity

### We all have access for free

- Automattic provides the Pro Account for everyone.
- The main benefit is that it is far less prone to hallucination. It's based on information it finds from actual links.

## Cursor

### All of the above, plus...

- You have access to all other models directly for the same subscription cost (20$ per month).
- Specifically, code-tasks are much better there.
- However, other things are less convenient (e.g. image generation).
- Plus, we do not have an agreement with Cursor directly (but we do with OpenAI).
### Writing Scripts

#### Automate Repetitive and Boring Tasks

- Examples:
	- Analyzing a link and extracting plugin/theme information: [[woo_analysis_with_ai.py]]
	- Automatically organize files and folders according to predefined rules: [[organize_obsidian_attachments.py]]
		- *Show [actual recent example](obsidian://open?vault=Obsidian&file=99%20-%20Meta%2F99%20-%20Files%2F2025-04-20%202025-04-22-1.pdf) if there's time*
	- Clean up and convert documentation into different formats (more below)

#### Scripts For Better Support

- Woo Support With Documentation:
	- [Finder link](file:///Users/danildanilov/Documents/GitHub/webImportsWoo)

### [[Vibe Coding]]

- https://www.youtube.com/watch?v=SS5DYx6mPw8
- https://cursor.directory/
- https://www.codeguide.dev/#faq

***Brief Demo Moment:***
- *(Share screen in Cursor)*
- **Goal:** Quickly find all `.log` files within a sample 'Support Interactions' folder structure.
- **Vibe Prompt Example:** "Write a python script to find all files ending in `.log` recursively within the './Support Interactions/' directory and print their full paths."
- *(Show Cursor generating and running the script)*

#### Build your own apps!
- There are many online tools that do this: lovable.dev, bolt.new, v0.dev, base44.com, and a whole lot more
- However, they do not give you as much control as you would have using a code editor like Cursor or Windsurf.


#### Examples:

- [Introducing StatSync: Your personal Zendesk time tracker! – Stellar](https://stellarp2.wordpress.com/2025/04/20/introducing-statsync-your-personal-zendesk-time-tracker/)
- [Introducing Skills Matrix Automator Chrome Extension – We Have the Answers](https://wehavetheanswers.wordpress.com/2025/03/13/introducing-skills-matrix-automator-chrome-extension/)

### Complex Support Troubleshooting

#### Open up a new folder in Cursor..

Repository: [danieldanilov/libraAIworkshop](https://github.com/danieldanilov/libraAIworkshop)

- Add all relevant interaction details in that folder. For example:
	- Error logs
	- Customer screenshots
	- Markdown files with the full interaction of the ticket
	- PDFs, or related documents from support that can help resolve it
	- Slack interactions where this error is explained to you
	- Export P2s that can help resolve this issue
	- Once resolved: create a final document that summarizes everything (using AI) so that it can learn from itself over time.

- This has the added benefit of having a "track record" of all similar issues. So for example, over time, you would build a database of all similar issues and how they were resolved.

## Warnings

### Verify, verify, verify.

Often, things go wrong. Remember AI can hallucinate or be confidently incorrect.

**Examples of Potential Issues:**
- Wrong links (archived or broken links)
- Incorrect naming (e.g. Google for WooCommerce vs. Google Ads & Listings)
- Incorrect dashboard steps (e.g. WooCommerce > Settings > Logs vs WooCommerce > Settings > Status > Logs)
- Misunderstanding of context (e.g. "please contact WooCommerce support" instead of realizing the customer is already talking with us)
- Lack of knowledge of internal workflows (e.g. scope of support)
- *Concrete Example:* (Optional: Share a brief, anonymized example where AI gave incorrect advice specific to your work, if readily available)
- {add your own here}

**How to Verify (Actionable Steps):**
1.  **Check URLs:** Does the link work? Does it go to the expected official source?
2.  **Cross-reference:** Does the info match our internal docs, P2s, or official product documentation?
3.  **Test Steps:** If it suggests UI steps, quickly try them in a test environment if possible.
4.  **Ask a Colleague:** If unsure, quickly sanity-check with a teammate.
5.  **Track Your Work:** Using a system like `TASK.md` or notes helps document *what* you asked the AI and *what* outcome you used, creating accountability and a learning loop.

### Feeding information (privately)

#### [CustomGPT for Goals Setting](https://chatgpt.com/g/g-67ece15b59e48191a550562d61344641-stellar-goal-setting)

Maria shared it in Slack. [[Ivona]] really enjoyed the conversation with it. She thinks we can use that for tracking replies or something else.
	- How would you feed this information to the AI so that they can help us in specific conversations.

![[2025-04-25 Libra AI Workshop-1.png]]
#### Private information

Automattic has an arrangement with OpenAI where they are not being trained on any of our materials.
	- Manual deletion of passwords and emails. If that is the case.
	- WooPayments account IDs.
	- Personal address.
	- The last 4 digits of a card.
	- [OpenAI & ChatGPT « Automattic Field Guide](https://fieldguide.automattic.com/openai/)

## Other tools (if there's time..)

#### Generating Graphs

- [Example chat](https://chatgpt.com/share/680b5a28-d3bc-8005-9cb4-d022f8859958)
- You can also do the same in Cursor (show example)

#### Creating Presentations!

- [Example chat](https://chatgpt.com/share/680b70a3-e27c-8005-abdb-c75bd83d97ab)
- [App Script](https://script.google.com/u/0/home/projects/1a3cq-nIWK-tJ6f3TNol1XQKL3xLPYEyUicBHcY-CAlfB0EcHZQ8ubi_m/edit)
- [Google Slides](https://docs.google.com/presentation/d/1gJsRv-ulFc50zCmH0aEIUIPjuC2AtDiCNLMnwy0vCyw/edit)

#### MCPs: https://github.com/modelcontextprotocol/servers

> **MCP (Model Context Protocol)** is a framework that lets AI models not only remember useful context about the user across conversations (like preferences, goals, or work history), but also **take specific actions on the user's behalf**—such as updating documents, running scripts, or managing tasks—based on that context. It's designed to make the AI a more helpful, proactive assistant over time.

#### Taskmaster: [eyaltoledano/claude-task-master](https://github.com/eyaltoledano/claude-task-master)

1. https://www.youtube.com/watch?v=1L509JK8p1I
2. https://www.youtube.com/watch?v=dF4uCZAY1tk

## We're at the end. What's next for you?

Think about the tools and techniques discussed.
- **What is *one specific way* you plan to try using one of these tools or techniques in your work this week?**
- *(Optional Suggestion: Try setting up Cursor, or use the CARE prompt framework on your next complex ticket.)*

