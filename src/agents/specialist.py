"""Specialist agent: executes its allow-listed tools and answers."""


class DataSpecialistAgent:
    def __init__(self, llm, registry_entry: dict, tools: dict):
        self.llm = llm
        self.system_prompt = registry_entry["system_prompt"]
        self.tool_names = registry_entry["tool_names"]
        self.tools = {name: tools[name] for name in self.tool_names}  # enforce allow-list

    def answer(self, user_query: str, call: dict):
        """Run the requested tool (if allow-listed) and answer from its result."""
        tool_name = call.get("tool")
        if tool_name not in self.tools:
            return f"Error: tool '{tool_name}' is not in my allow-listed surface.", None
        tool_result = self.tools[tool_name](**call.get("arguments", {}))
        msg = (f"User query: {user_query}\n"
               f"TOOL RESULT: {tool_result}\n"
               "Answer the user query from this result only.")
        result = self.llm.chat(self.system_prompt, msg)
        return result.content, {"tool": tool_name, "result": tool_result, "usage": result.usage}
