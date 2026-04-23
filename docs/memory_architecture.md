# Memory Architecture

1. Memory Input Layer  
   Normalize user input, agent replies, tool results, and feedback into `memory_event`.

2. Storage Layer  
   Store information across Base Memory, Project Memory, and Short-Term Memory.

3. Updating Layer  
   Supports append, update, migration, archiving, and conflict logging.

4. Retrieval Layer  
   Supports retrieval by project name, field, tags, date, and keywords.

5. Context Builder  
   Extract relevant content from multiple memory layers and package it for the agent.

6. Governance Layer  
   Manage privacy, duplicates, conflicts, expiration, sanitization, and archiving.
