# RGS-Intro-to-Machine-Learning

**Machine Learning and Data Science for Policy Analysis**, taught by Carter Price and Gabe Hassler at the [RAND School of Public Policy](https://www.rand.edu).

This is the GitHub repository where materials for this class will be posted.
It is a living repository, and will be continuously updated throughout the course.
See the full [syllabus](RGS-intro-to-ml-syllabus_final.pdf) for the schedule, readings, grading, and course policies.

## Please complete before the first day of class

It's fine if you run into challenges and are not able to complete all of these.
We will help sort through some of them on the first day of class.
These can all be completed independently.
If you cannot get one step to work, continue on to the others.

### 1. Install a programming language on your computer

You will have to write, run, and execute code for this course.
You are free to work in any programming language you would like, and do not have to stick to a single language.
Popular languages for machine learning workflows include:
- Python
- R
- Julia

**If you are new to programming, I recommend that you use Python.**
Most class examples will be in Python, and it is the most commonly used language for machine learning tasks.
There are lots of ways to install Python, many of which are specific to particular operating systems.
The two below are, in my opinion, the easiest, but feel free to try alternatives.
- [Install Python on Windows](https://learn.microsoft.com/en-us/windows/dev-environment/python?tabs=winget).
- [Install Python on MacOS](https://docs.python.org/3/using/mac.html)

For those who use a virtual desktop to access class materials, I do not recommend you install a programming language to the virtual desktop.
Generally, it will be easier to write and run code outside of the virtual desktop.

### 2. Set up a GitHub account
If you do not already have one, set up an account on [github.com](https://github.com).
GitHub is a place for storing, sharing, and distributing code.
While RAND maintains an internal GitLab code repository at code.rand.org, this is only available inside the RAND network.

### 3. Install Git

Git is the version control tool that GitHub is built on; you'll need it locally to clone repositories and submit homework.
- [Install Git on Windows](https://git-scm.com/install/windows)
- [Install Git on MacOS](https://git-scm.com/install/mac): the simplest approach is to just run `git --version` in Terminal, which will prompt you to install the Xcode Command Line Tools if Git isn't already present.

### 4. Install an Integrated Development Environment (IDE)

IDEs are fancy text editors that make it easier to write and run code.
You may use whichever editor you like, but I recommend [Visual Studio Code (VS Code)](https://code.visualstudio.com/download).

### 5. (Recommended) Set up an AI programming assistant
AI programming agents (e.g., Claude Code) are quickly becoming the norm for machine learning practitioners.
Part of this course will be developing skills on the responsible use of AI for implementing and evaluating machine learning pipelines.
While browser-based chatbots like ChatGPT or Claude can help write and debug code, they are limited to what you can copy/paste into the chat.

AI programming assistants like Claude Code or OpenAI Codex can read data on your computer, write and execute code, and examine the results with much less human effort than is required with browser-based chatbots.
I recommend that students in this course learn to use an AI programming assistant.

If you are a RAND employee / student in some RAND programs, you should have access to Claude Code and Codex through RAND.

If you are not, then some free options include:
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) (Google, generous free tier)
- [GitHub Copilot](https://github.com/features/copilot) free tier (limited monthly usage, available to students via the [GitHub Student Developer Pack](https://education.github.com/pack))


Paid options include:
- [Claude Code](https://www.anthropic.com/claude-code) (Anthropic), usable via a Claude Pro/Max subscription or pay-as-you-go API usage
- [OpenAI Codex CLI](https://github.com/openai/codex), usable via a ChatGPT Plus/Pro subscription or pay-as-you-go API usage
- [Cursor](https://cursor.com), an AI-native IDE built on VS Code
- [GitHub Copilot](https://github.com/features/copilot) paid individual plan


The examples I use in class will be based on Claude Code, but most AI programming assistants have similar setups.