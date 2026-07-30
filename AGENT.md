# Warren Buffett Second Brain - LLM Agent Instructions

This file contains the instructions for maintaining and expanding the Warren Buffett second brain knowledge according to the Karpathy pattern.

## System Architecture

**Layer 1 - Raw Sources**: 
- Directory `Raw/` contains markdown files of various Buffett-related materials (1977-2024)
- Naming convention: `YYYYltr.md` for annual letters, `EventNameYYYY.md` for speeches/interviews/articles
- Examples: `1977ltr.md`, `DUKE2024.md`, `CNBCInterview.md`, `ShareholderMeeting2023.md`

**Layer 2 - Wiki**:
- Directory `wiki/` with PascalCase subdirectories
- `wiki/Sources/` - structured summaries by source type and date
- `wiki/Concepts/` - thematic concepts (Moat, ManagementQuality, etc.)
- `wiki/Applications/`, `wiki/Cases/`, `wiki/People/`, `wiki/Principles/`, `wiki/Synthesis/`

**Layer 3 - Schema**:
- `wiki/SCHEMA.md` defines maintenance rules
- This file ([AGENT.md](file://c:\Users\rbaron\OneDrive%20-%20sice.com\Documentos\Cartera\Brain\AGENT.md)) contains LLM agent instructions

## Main Operations

### Ingesting New Sources
1. Add file to `Raw/` with appropriate name (not limited to annual letters)
2. Process with `type: source-summary` and corresponding frontmatter
3. Update `wiki/index.md` and `wiki/log.md`

### Updating Concepts
1. Maintain files in `wiki/Concepts/` with standard format
2. Use frontmatter: `type: concept`, `stability: high/medium/low`
3. Include sections: `## Definition`, `## Examples from Letters`, `## Contrasts & Nuances`

### Cross-Source Synthesis
1. Create files in `wiki/Synthesis/` with links to multiple `Sources/`
2. Use `type: synthesis` in frontmatter
3. Maintain traceability to original sources

## Standard Format

### Frontmatter for Sources
```yaml
---
date: YYYY-MM-DD
source: [[Raw/SourceFileName.md]]
tags: [annual-letter, interview, speech, article]
type: source-summary
year: 2024
sourcetype: annual-letter  # annual-letter, interview, speech, article, etc.
---
```

### Frontmatter for Concepts
```yaml
---
title: "Concept Name"
type: concept
stability: high
tags: [tag1, tag2]
date: YYYY-MM-DD
source: [[Sources/SourceFileName]]
---
```

### Frontmatter for Synthesis
```yaml
---
title: "Synthesis Topic"
type: synthesis
stability: medium
tags: [cross-source, theme]
date: YYYY-MM-DD
source: [[Sources/Source1]], [[Sources/Source2]]
---
```

## Important Rules
- All file and directory names in PascalCase
- All links must be bidirectional (`[[PageName]]`)
- Each insight must have specific source reference (`[[Source#pX-Y]]`)
- No content duplication between categories
- Maintain consistency in structure and format
- **ALL CONTENT MUST BE IN ENGLISH** - This applies to all new additions and modifications
- Sources are not limited to annual letters - can include interviews, speeches, articles, etc.