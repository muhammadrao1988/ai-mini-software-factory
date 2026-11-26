# AI mini software factory

A small software factory you can run on a laptop. A task goes in, an AI agent builds it alone, and hidden tests
judge the result.

![A task goes to an AI agent, hidden tests judge the work, a report comes out](docs/how-it-works.png)

## The problem

Everyone is talking about "software factories": AI agents that take a task and build it without a person typing
each step.

The hard part is not getting an agent to write code. The hard part is knowing if the code is right when nobody
reads it.

- An agent writes its own tests. They pass. It says "done".
- But its tests only check what the agent thought of.
- So work can look finished and still be wrong.

## What this tool does

It is a factory in one file, small enough to read in ten minutes.

1. **A task goes in.** A short text, like a ticket.
2. **An agent builds it alone**, in its own fresh copy of a small shop project.
3. **Hidden tests judge it.** The agent never sees them.
4. **If something is wrong, a short note goes back**, like "an empty cart must have no shipping cost". Never the
   test itself. The agent gets 3 tries at most.
5. **A report comes out:** passed or failed, tries, time and cost.

## What you can use it for

| You want to | Do this |
|---|---|
| **Understand how a software factory works** | Read `factory.py`. It is one file. Then run one task and watch the agent work. |
| **See how good your tickets are** | Write a ticket and the hidden tests for it. If the agent fails on the first try, the ticket left something out. |
| **Compare AI models** | Run the same ten tasks with two models and compare passes, time and cost. |
| **Try it on your own code** | Point it at your own Python project with `--project`, and give it your own task. |

## What you get

While it runs, you see every step the agent takes:

```
Task 06-shipping
  try 1: agent is working ...
      agent reads shop/cart.py
      agent reads tests/test_cart.py
      agent changes shop/cart.py
      agent changes tests/test_cart.py
      agent runs: python3 -m pytest -q
    tests the agent can see: 5 passed, 0 failed
    hidden tests:            4 passed, 3 failed
  try 2: agent is working ...
      agent changes shop/cart.py
      agent changes tests/test_cart.py
      agent runs: python3 -m pytest -q
    tests the agent can see: 8 passed, 0 failed
    hidden tests:            7 passed, 0 failed
```

At the end, one table (also saved as `out/report.md`):

| Task | Result | Tries | Time | Cost (API price) |
|---|---|---|---|---|
| 05-sales-tax | Passed | 1 | 27 s | $0.18 |
| 06-shipping | Passed | 2 | 41 s | $0.30 |
| 07-receipt | Passed | 1 | 32 s | $0.08 |

For every try, four files are saved in `out/logs/<task>/`:

| File | What is in it |
|---|---|
| `try-1-agent.txt` | What the agent was told, every step it took, and what it said at the end |
| `try-1-change.diff` | The exact lines the agent added and removed |
| `try-1-visible.txt` | The result of the tests the agent can see |
| `try-1-hidden.txt` | The verdict of the hidden tests |

## What I found

I ran the same 10 small tasks twice. The only difference was how the task was written.

| How the task was written | Passed on the first try | Passed after retries | Time | Cost (API price) |
|---|---|---|---|---|
| A full spec, every rule written out | 10 of 10 | 10 of 10 | 213 s | $1.60 |
| A one-line ticket | 6 of 10 | 10 of 10 | 284 s | $2.08 |

In the 4 tasks that failed first, **every test the agent wrote for itself had passed**:

| Task | The agent's own tests | Hidden tests | What was really wrong |
|---|---|---|---|
| Refuse bad input | 18 passed | 1 failed | A quantity like 1.5 was accepted |
| Merge same items | 5 passed | 2 failed | The same item at a different price was accepted |
| Shipping | 5 passed | 3 failed | Shipping was not added to the total, and an empty cart was charged |
| Save and load | 5 passed | 4 failed | Broken saved data was not refused |

After one short note for each wrong point, all four passed on the second try. No person was needed.

What I take from it:

- A short ticket costs a retry. Time and cost went up by about a third.
- An agent's own tests are not proof.
- A hidden judge and a short note are enough to fix small mistakes.

The full results are in [`results/`](results/).

## How to use it

### Step 1: Install two things

- **uv**, which runs the tool: [install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Claude Code**, the AI agent: [install Claude Code](https://code.claude.com/docs). Then type `claude` in a
  terminal once and sign in with your Claude account.

### Step 2: Download this project

```bash
git clone https://github.com/muhammadrao1988/ai-mini-software-factory.git
cd ai-mini-software-factory
```

### Step 3: Check the judge (no AI, a few seconds)

```bash
uv run check_tasks.py
```

For every task this proves two things: the untouched project fails the hidden tests, and a correct answer written
by hand passes them.

### Step 4: Run one task

```bash
uv run factory.py tasks/01-discount-code
```

### Step 5: Run all ten

```bash
uv run factory.py tasks              # each task as a full spec
uv run factory.py tasks --tickets    # each task as a one-line ticket
```

### Step 6: Use it on your own project

Your project must be a Python project with a `tests/` folder.

1. Make a folder for your task, for example `my-tasks/add-login/`.
2. Put the task in `task.md`, in plain words.
3. Put your hidden tests in `hidden/test_hidden.py`. Start each test with one sentence that says what must be true.
   That sentence is the note the agent gets when the test fails.
4. Run it:

```bash
uv run factory.py my-tasks/add-login --project path/to/your/project
```

The agent works on a copy. Your project is never changed. If you like the result, the change is in
`out/logs/add-login/try-1-change.diff`.

### No Claude subscription? Use an API key

An API key is a paid key from Anthropic. Create one in the [Claude Console](https://platform.claude.com/), then:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv run factory.py tasks --api-key
```

Without `--api-key`, the factory uses your Claude sign-in and ignores any API key, so you never get a bill by
accident. A full run of ten tasks costs about $2 at API prices.

## A lesson from building it

On my very first run, the judge was wrong, not the agent. It failed a correct answer, and the agent spent two more
tries fixing a problem that did not exist.

So the judge now works in a clean copy and saves a log of every verdict, and `check_tasks.py` tests the judge
itself before any agent runs. A factory is only as good as its judge.

## Good to know

It is teaching-size: ten small tasks on one tiny project, run with one model. It stops at the report and never
merges or publishes anything by itself.

<details>
<summary>More details: the files, writing your own task, settings</summary>

**The files**

| File or folder | What it is |
|---|---|
| `factory.py` | The factory: workspace, agent, judge, retry, report |
| `check_tasks.py` | Tests the judge itself, without AI |
| `demo/` | The small shop project every agent starts from |
| `tasks/<name>/task.md` | The task as a full spec |
| `tasks/<name>/ticket.md` | The same task as one line |
| `tasks/<name>/hidden/` | The hidden tests. The first line of text in each test is the note the agent gets on a fail |
| `reference/` | A correct answer for each task, written by hand, used only by `check_tasks.py` |
| `results/` | The results and judge logs of my runs |

**Write your own task**

1. Make a folder in `tasks/` with a `task.md` and a `ticket.md`.
2. Put tests in `hidden/test_hidden.py`. Give each test a first line of text that says, in plain words, what must
   be true.
3. Put a correct `cart.py` in `reference/<task name>.py`.
4. Run `uv run check_tasks.py`.

**What the agent is allowed to do**

Read, write and search files in its own folder, and run the tests. Its folder is a temporary copy outside this
project, so the tasks, the hidden tests and the reference answers are not in it.

**Smaller notes**

- The agent is kept in its folder by Claude Code's permission rules.
- The hidden tests show what I think is right for each task.
- Tested on a Mac, with the demo shop. The `--api-key` option is not yet run with a paid key.

**Settings**

| Setting | Default | What it does |
|---|---|---|
| `--tickets` | off | Give the agent `ticket.md` instead of `task.md` |
| `--project` | the demo shop | The Python project the agents work on |
| `--api-key` | off | Pay with `ANTHROPIC_API_KEY` instead of the Claude sign-in |
| `FACTORY_MODEL` | `sonnet` | The AI model the agent uses |

</details>

Built by [Muhammad Rao](https://github.com/muhammadrao1988) with Claude Code. MIT licence.
