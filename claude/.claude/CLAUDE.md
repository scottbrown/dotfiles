# Personal CLAUDE.md File

## General

- Be concise
- Do not overly apologize

## Location

- When regulatory and laws come into effect, use Canada as the jurisdiction
- Use Canadian spelling and not American spelling
  - Good: "behaviour"
  - Bad: "behavior"

## General Software Design Conventions

- If a configuration file will be edited by a human, use YAML
- Unit tests are important to me as part of TDD
- Ensure test coverage is always at least 70%
- My personal Github account is called "scottbrown"

## Go Coding Conventions

- Use idiomatic Go for everything
- Never use third-party mocking libraries
- CLI applications MUST always use github.com/spf13/cobra for its flagging library
- CLI applications MUST put their main entrypoint in `cmd/<binary name>`
- Business logic goes into the root directory, the package name being the same as the project name (as long as it is formatted for Go's allowable module names; i.e. no hyphens)
- Use Go Task instead of Makefile, and name the file `Taskfile.yml`
- Ensure that README.md is always up to date
- The code should be self-documenting, do not add useless comments unless it helps to describe a complex piece of code
- Always avoid primitive obsession anti-patterns

## Git conventions

- When creating commits, use present tense.
  - Correct: "Adding content"
  - Incorrect: "Added content"
  - Incorrect: "Add content"

## Tooling Choices

- Use `gh` whenever you need to interact with Github
- While you can use ripgrep, I prefer `ag` for searching
