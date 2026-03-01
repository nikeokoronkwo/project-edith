Here's the plan:
What you're building: Three Python modules that chain together into a pipeline. Each one is a pure function — takes input, returns output, no database dependency. You test them with the existing JSON data and print/save results to files.
Module 1: tokenizer.py — PII Tokenization
Takes a raw report text string, returns the tokenized version plus an audit log. You need spaCy for NER and Python's re for regex. The token vault is just a dictionary in memory for now — when the DB exists later, you swap the dict for a DB write.
Your inputs from the existing data: the raw_text field from field_reports.json. You already know that 34 of the 200 reports have PII in the body (the "out of" template with names and phones). Your pipeline needs to catch those, but also handle the other templates cleanly (where there's nothing to redact in the body, only in metadata).
The three layers run in sequence on the same text. Layer 1 regex catches phone patterns. Layer 2 dictionary catches known names (you load these from the metadata of all reports — build the known names list from the data itself). Layer 3 spaCy catches anything the first two missed. Each layer replaces matches with tokens like [OPERATIVE-A7F3] and [CONTACT-9B2E], and logs what it found.
Your deliverable is: given any string, return (tokenized_string, token_map, audit_log). You can test this completely standalone by running it against all 200 reports and printing results.
Module 2: llm_extractor.py — LLM Entity Extraction + Modifier Generation
Takes a tokenized report text, calls an LLM API, returns structured JSON with extracted entities AND a computed modifier. This is where you need an API key (OpenAI, Anthropic, or Gemini — whichever your team has access to).
The prompt is the critical piece. You'll craft a system prompt that tells the LLM: "You are an intelligence analyst. Given this field report, extract structured data and determine what operational modifier this implies for resource forecasting." The LLM returns JSON with sector, resource, severity, event_type, and a modifier object.
The tricky part is mapping event_types to modifier parameters reliably. You'll probably want to do a two-step approach: let the LLM extract the entities and event_type, then have deterministic Python code compute the modifier based on the event_type (rather than trusting the LLM to get the modifier math right). So the LLM does the NLP, and your code does the math.
Your deliverable is: given a tokenized text string, return (extraction_result, modifier). You can test this by running it against all 200 tokenized reports and saving the results to a JSON file.
Module 3: pipeline.py — The Full Chain
This is just the orchestrator that calls Module 1 then Module 2 in sequence and bundles the results. It takes a raw report object (the full JSON entry from the data), runs it through tokenization, then extraction, and returns a complete processed result with everything a downstream system would need.
Your deliverable is: given a raw report dict, return a complete processed result dict. You can batch-process all 200 reports and dump results to processed_reports.json — this file becomes the integration artifact that Person 3 can load into the database and Person 2 can use to test the frontend feed.
The execution order:

Install spaCy and download the model (pip install spacy && python -m spacy download en_core_web_sm)
Build and test tokenizer.py against the 200 reports — verify it catches the 34 PII-containing reports correctly
Build and test llm_extractor.py against a handful of tokenized reports — iterate on the prompt until the JSON output is clean
Wire them together in pipeline.py and batch-process all 200 reports
Save everything to processed_reports.json — this is your handoff artifact

What you DON'T need right now: PostgreSQL, FastAPI, SQLAlchemy, any frontend code, WebSockets, or even agreement on the database schema. All of that gets bolted on after. Your modules just need to be importable functions that Person 3 can call from inside an API route later.