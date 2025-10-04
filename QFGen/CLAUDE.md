# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a French mathematics quiz generator application ("Questions Flash" or "QF" generator) built with Python and CustomTkinter. It creates LaTeX-formatted math quizzes for different grade levels (6ème through Terminale), compiles them to PDF, and includes AI-powered question generation using Claude (Anthropic) or OpenAI.

## Setup Commands

### Initial Installation
```bash
# Run init.bat to set up environment (Windows only)
init.bat
```

### Running the Application
```bash
# Use the run script
run.bat

# Or manually:
venv\Scripts\activate
python main.py
```

### Configuration
- **API Keys**: Both OpenAI and Claude API keys are stored in `qf_gen_config/api_key.txt`:
  ```
  OPENAI_API_KEY="sk-proj-xxxxx..."
  ANTHROPIC_API_KEY="sk-ant-api03-xxxxx..."
  ```
- **AI Provider & Models**: Configured in `qf_gen_config/ai_provider.txt`:
  ```
  PROVIDER=claude
  CLAUDE_MODEL=claude-sonnet-4-5-20250929
  OPENAI_MODEL=gpt-5-2025-08-07
  ```
  Change `PROVIDER=` to switch between `claude` (default) and `openai`
- **TCL Path**: Automatically configured by `init.bat` and stored in `qf_gen_config/tcl_path.txt`

## Architecture

### Core Application Flow
1. **main.py** - Entry point containing `QuestionnaireApp` (main Tkinter UI)
2. User creates/loads question sets organized by:
   - Grade level (classe): 6ème, 5ème, 4ème, 3ème, 2nde, 1ere, Tle
   - Date (format: JJ_MM_YYYY)
   - Question ID (format: QF_DD_MM_YYYY)

### Data Management
- **Database Structure**: `databases/database_{classe}/database_{year}_{month}.json`
  - Each grade has its own folder (e.g., `database_6eme/`, `database_5eme/`)
  - Monthly JSON files store all questions for that period
  - Questions contain: enonce (question), reponse (answer), details (detailed answer), theme, prompt
- **Last Session**: `last_questions_data.json` stores the most recent work

### LaTeX Generation & Compilation
- **Templates**:
  - `modele_QF.tex` - Template for daily quiz sheets
  - `Modele_QF_eval.tex` - Template for evaluation sheets
- **Output Structure**:
  - Generated TEX: `generated/tex/{classe}/{year}/{month}/`
  - Generated PDF: `generated/pdf/{classe}/{year}/{month}/`
  - Evaluations: `generated/eval_tex/` and `generated/eval_pdf/`
- **Compiler**: `latexcompiler.py` wraps LuaLaTeX compilation with automatic auxiliary file cleanup

### AI Integration
- **auto_question_maker.py**:
  - `QuestionGenerator` - Streams question generation from Claude or OpenAI
    - Claude: Uses `AsyncAnthropic` client with configurable model (default: `claude-sonnet-4-5-20250929`)
    - OpenAI: Uses `openai.ChatCompletion` with configurable model (default: `gpt-5-2025-08-07`)
    - Provider and models are read from `qf_gen_config/ai_provider.txt` at initialization
  - `MonoQuestionGeneratorUI` - UI for generating/editing single questions with AI
  - `MultiQuestionGeneratorUI` - Batch question generation
  - `QuestionJsonGenerator` - JSON-formatted question generation (OpenAI only)
- **prompt_system_manager.py**: Manages AI prompts (`PSManager` class)
- **qf_gen_config/cfg.py**:
  - `read_ai_provider()` - Detects which AI provider to use
  - `read_ai_model(provider)` - Returns the model name for the specified provider
  - `read_claude_api_key()` - Reads Claude API key
  - `read_api_key()` - Reads OpenAI API key
- **Ctrl+Double-Click** on any text field opens AI assistant for that specific field

### LaTeX Editing Features
- **latexhighlighter/tex_highlighter.py**: Custom `LatexText` widget with syntax highlighting
- **latexhighlighter/syntax_checker_v2.py**: Validates LaTeX before compilation (`check_latex_code()`)
- **autoindent_tex.py**: Auto-formats LaTeX files (`clean_and_indent_latex_file()`)

### Question Loading System
- **UI_question_loader/**: Implements question browser/loader from existing databases
  - `question_loader_imp_v3.py` - Latest version with dropdown interface
  - Allows loading previous questions as templates for new questions

### Evaluation Generator
- **tex_eval_maker.py**: Creates evaluations from date ranges
  - `load_json_files_in_date_range()` - Finds relevant question files
  - `extract_questions_by_date()` - Randomly selects questions for evaluation
  - Combines questions into multi-question evaluation sheets

## Key Workflows

### Creating New Questions
1. Select grade level (classe) and date
2. Click "Créer une nouvelle série" to create new question set
3. Fill in 3 questions (each with: question, answer, details, theme)
4. Use AI assistant (Ctrl+Double-Click or "Appeler l'assistant" button) to generate content
5. Click "Sauvegarder les modifications" to save to database
6. Click "Générer LaTeX" to compile to PDF

### Loading Existing Questions
1. Select grade level
2. Choose question ID from dropdown, OR
3. Click "Charger un modèle" to browse from any database, OR
4. Click "Charger un contenu précédent" for advanced search across classes/dates

### Creating Evaluations
1. Click "Créer une évaluation"
2. Specify: classe, date range (min/max), number of questions
3. System randomly selects questions from database within date range
4. Generates and compiles evaluation PDF with answer key

## Important Notes

- Application uses French UI and terminology
- LaTeX compilation requires LuaLaTeX installed on system
- Syntax validation runs before compilation to catch LaTeX errors early
- All text fields support LaTeX commands and have real-time syntax highlighting
- Question databases are organized by grade level and month for efficient loading

### AI Provider Configuration
- **Default Provider**: Claude (excellent for mathematics and LaTeX)
- **Model Configuration**: Both provider and model names are fully configurable
- **Switching Providers**: Change `PROVIDER=` in `qf_gen_config/ai_provider.txt`
- **Custom Models**: Update `CLAUDE_MODEL=` or `OPENAI_MODEL=` to use different model versions
- **Code Architecture**:
  - All AI calls go through facade methods in `QuestionGenerator`
  - Each provider has separate implementation methods (`_generate_*_claude()` vs `_generate_*_openai()`)
  - Claude uses async/await with `AsyncAnthropic` client
  - OpenAI uses synchronous calls with streaming
  - Model selection happens at initialization time via `read_ai_model()`
