Use a prompt like this:

  Before analyzing the code, query .codegraph to identify only the files and symbols relevant to this task:

  [describe the task/question]

  Do not read the whole repository. First return:
  - relevant files
  - relevant functions/classes
  - dependency path between them
  - whether the codegraph appears stale

  Then read only those files and answer the question.

  Example for your timestamp feature:

  Before analyzing the code, query .codegraph to identify only the files and symbols involved in sending a client timestamp from the frontend image capture
  through WebSockets, backend queues, and the shared-memory VLM ring buffer.

  Do not read the whole repository. First list the relevant files, functions, and data flow. Then read only those files and explain the required changes.

  For an implementation request, add:

  Only modify files confirmed relevant by the codegraph and source inspection. Do not modify unrelated files.

  Also add this safeguard because the graph can become stale:

  Compare codegraph file/index timestamps with the current source files. If stale, treat source files as authoritative.
 