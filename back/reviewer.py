from gcp import GCP
from pydantic import BaseModel, Field
from typing import List, Optional

class SMInstructionValidation(BaseModel):
    """
    Represents the validation status and classification of a single System Message instruction.
    """
    sm_id: str = Field(..., description="The ID of the System Message instruction, e.g., 'SM-1'.")
    instruction: str = Field(..., description="The full text of the SM instruction.")
    classification: str = Field(..., description="The classification of the SM instruction (e.g., 'Context & Domain Awareness', 'Tool Usage Guidelines', 'Assistant Behavior & Tone').")
    followed: bool = Field(..., description="True if the instruction was followed, False otherwise.")

class ModelFailureDetails(BaseModel):
    """
    Detailed information for a turn identified as a Model Failure.
    """
    error_labels: List[str] = Field(..., description="List of error labels for the failure, e.g., ['wrong_param_value', 'required_param_missing'].")
    critic_comment: str = Field(..., description="A detailed critic comment in the third person, describing what went wrong in this specific model failure instance. Example: 'The model incorrectly called `search_spotify_tracks` and `search_spotify_top_results` in parallel.'")
    reasoning_response: Optional[str] = Field(None, description="The model's hypothetical internal reasoning or explanation for the failure, in the first person. Example: 'I misinterpreted the user's request and incorrectly used a calendar title where a place ID was expected.'")

class TurnDetail(BaseModel):
    """
    Detailed information for a single turn in the conversation, including pass/fail status.
    A turn is considered 'passed: True' if it functions as expected, even if it's a designed 'Model failure'
    that the user is meant to correct, thereby fulfilling the task's failure criteria.
    """
    turn_number: int = Field(..., description="The sequential number of the turn.")
    turn_type: str = Field(..., description="The type of turn, e.g., 'Default clarification', 'Sequential tool call', 'Model failure'.")
    description: str = Field(..., description="A brief narrative description of what happened in this turn.")
    passed: bool = Field(..., description="True if the turn passed its evaluation (including legitimate model failures), False otherwise (for unacceptable errors).")
    cited_sm_instructions: List[str] = Field(..., description="List of SM instruction IDs that are relevant to this turn's actions or failures, e.g., ['SM-16', 'SM-12'].")
    model_failure_details: Optional[ModelFailureDetails] = Field(None, description="Details specific to a model failure, if this turn type is 'Model failure'.")

class EvaluationResponse(BaseModel):
    """
    Represents the comprehensive structured response for evaluating an Agent Completion task,
    including detailed System Message validation, turn-by-turn breakdown, and task-level metrics.
    """
    inferred_task_category: str = Field(..., description="The primary task category inferred from the secondary_category in the task metadata, either 'Search Refinement' or 'Contextual Information'.")
    starting_remark: str = Field(..., description="An introductory remark for the evaluation response.")

    # Fields for the initial SM and Turn-by-Turn Breakdown from prompt
    overall_sm_directives: List[str] = Field(
        ...,
        description="List of overall System Message directives from the prompt, e.g., 'Search refinement is present.'."
    )
    sm_instruction_validations: List[SMInstructionValidation] = Field(
        ...,
        description="Detailed validation for each individual numbered SM instruction, including its classification and pass/fail status."
    )
    turn_breakdown_list: List[TurnDetail] = Field(
        ...,
        description="A detailed breakdown of each turn in the conversation, including its type, description, pass/fail status, and relevant SM citations."
    )

    # Task-level metrics and summaries derived from the prompt
    sequential_tool_call_summary: str = Field(
        ...,
        description="Summary of turns involving sequential tool calls from the prompt, e.g., 'Turn2 ,turn6, turn7'."
    )
    parallel_tool_call_summary: str = Field(
        ...,
        description="Summary of turns involving parallel tool calls from the prompt, e.g., 'turn 4'."
    )
    model_failure_summary: str = Field(
        ...,
        description="Summary of turns identified as model failures from the prompt, e.g., 'turn 6, turn 8, turn 10'."
    )
    flow_break_status: str = Field(
        ...,
        description="Indicates if any flow breaks occurred in the conversation from the prompt, e.g., 'No'."
    )
    sr_turn: str = Field(
        ...,
        description="Indicates the turn number where Search Refinement (SR) is expected from the prompt, e.g., 'turn 7'."
    )

    # New task-level numerical summaries (these will be calculated during evaluation)
    total_model_failures: int = Field(..., description="The total calculated count of model failure turns in the conversation.")
    total_parallel_tool_calls: int = Field(..., description="The total calculated count of turns that included parallel tool calls.")
    total_sr_turns: int = Field(..., description="The total calculated count of turns where Search Refinement was utilized.")
    total_contextual_turns: int = Field(..., description="The total calculated count of turns categorized as 'Contextual'.")
    total_sequential_tool_calls: int = Field(..., description="The total calculated count of turns that included sequential tool calls.") # Added for clarity in pass/fail

    # Fields for the final evaluation checklist from prompt, now as booleans
    respecting_sub_categories: bool = Field(..., description="True if sub-categories were respected (e.g., SR in the specified turn), otherwise False.")
    no_flow_breaks: bool = Field(..., description="True if there were no flow breaks, otherwise False.")
    three_model_failures: bool = Field(..., description="True if exactly three model failures occurred as per the prompt's summary, and are legitimate, otherwise False.")
    at_least_3_user_prompts_that_trigger_tool_chains: bool = Field(..., description="True if at least 3 user prompts triggered tool chains, otherwise False.")
    default_clarification_behavior_followed: bool = Field(..., description="True if the default clarification behavior was followed, otherwise False.")

    # Task-level Pass/Fail and Reasoning (these will be calculated during evaluation)
    task_level_pass_fail: str = Field(..., description="Overall pass/fail status for the entire task. Can be 'PASS', 'REWORK / PARTIAL UNDERSTANDING', or 'FAIL'.")
    task_level_reasoning: str = Field(..., description="Detailed reasoning for the overall task-level pass/fail status, explaining which criteria were met or missed according to the new logic.")

    ending_remark: str = Field(..., description="A concluding remark for the evaluation response.")

    def to_markdown(self) -> str:
        """
        Convert the EvaluationResponse to YAML format using PyYAML.
        This is a simple and reliable conversion from JSON to YAML.
        
        Returns:
            str: A YAML representation of the evaluation response.
        """
        import yaml
        
        # Convert the Pydantic model to a dictionary
        data = self.model_dump()
        
        # Convert to YAML with nice formatting
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, indent=2, allow_unicode=True)
        
        return yaml_str


class Reviewer:
    def __init__(self):
        self.gcp = GCP()
        self.config()


    def config(self):
        self.load_system_message()
        self.schema = EvaluationResponse

    def load_system_message(self):
      self.system_message = """
      You are an expert evaluator for Agent Completion tasks. Your goal is to generate a comprehensive evaluation report in JSON format, strictly following the provided Pydantic schema EvaluationResponse. The evaluation must be based on the provided task metadata, the concise ruleset, and the explicit turn-by-turn breakdown given in the user prompt. Pay extremely close attention to the definitions and examples provided in the ruleset.

      CRITICAL METADATA PARSING: First, carefully extract the number_of_turns from the task metadata. This is the authoritative source for how many turns should be evaluated. The number_of_turns field in the metadata determines the total number of turns to analyze, regardless of what might be shown in the turn-by-turn breakdown.

      CRITICAL TURN DEFINITION: A turn is defined as one complete interaction cycle from one user message to the next user message. This means:
      - 1 turn = 1 user message → all assistant responses and tool calls (regardless of count) → next user message
      - All tool calls, assistant responses, and any intermediate actions that occur between two user messages are considered part of the same turn
      - Multiple tool calls within a single turn should be captured as part of that turn's description and evaluation
      - The turn_type should reflect the primary or most significant action within that turn, but the description should capture all activities
      - IMPORTANT: When evaluating model failures, remember that a turn designated as "Model failure" in the task design is INTENTIONAL and should be marked as passed: True if it correctly demonstrates the expected failure behavior. The model failure is part of the task's learning objectives, not an error.

      MODEL FAILURE EVALUATION RULES (from Agent Completion Playbook):
      - Model failures are INTENTIONAL design elements to test the assistant's error recovery capabilities
      - A turn marked as "Model failure" should be evaluated as passed: True if it demonstrates the expected failure behavior
      - Model failures should include appropriate error_labels such as wrong_param_value, required_param_missing, wrong_tool_selected, etc.
      - The critic_comment should explain why the model failed in that specific turn, drawing from the playbook's error definitions
      - The reasoning_response should provide a first-person explanation of the model's mistake
      - Model failures are NOT actual errors in evaluation - they are successful demonstrations of failure scenarios

      Inference of Task Category: The inferred_task_category for a given task will always be inferred from the input task's Metadata -> Fundamental -> secondary_category field. If "Context Information System Prompt" is present in secondary_category, the inferred_task_category is "Contextual Information". If "Search Refinement" is present (which is explicitly indicated in the SR: turn X field of the prompt's summary if applicable), the inferred_task_category is "Search Refinement". In cases where both are implicitly present (e.g., "Context Information System Prompt" in secondary category and an SR: turn X in the summary), prioritize the primary focus as indicated by the use_case or the more dominant behavior described. For this specific task, prioritize "Contextual Information" due to "Context Information System Prompt" being explicitly in secondary_category.

      Evaluation Criteria for Task-Level Pass/Fail: A task's overall status (task_level_pass_fail) is determined as follows:
      PASS:
      - The assistant respected the inferred_task_category.
      - total_model_failures is exactly 3, and these are "legit" (i.e., designed failures that the user would correct, as implied by the three_model_failures checklist item being True in the prompt's summary).
      - No unacceptable turns: All turns in turn_breakdown_list have passed: True, except for the 3 legitimate model failure turns (which should also be marked as passed: True).
      - At least 1 parallel tool call occurred (total_parallel_tool_calls >= 1).
      - At least 1 sequential tool call occurred (total_sequential_tool_calls >= 1).
      REWORK / PARTIAL UNDERSTANDING: If at least 50% of the above "PASS" criteria are met.
      FAIL: If less than 50% of the above "PASS" criteria are met.

      Instructions for Populating the EvaluationResponse Schema:
      inferred_task_category: Determine based on the "Inference of Task Category" rules above.
      starting_remark: Provide a friendly and concise introductory remark.
      overall_sm_directives: Extract only the two initial high-level SM directives: "Search refinement is present." and "SM respect the first category." from the "Overall Task Metadata" section of the user prompt.
      sm_instruction_validations: For each of the 19 numbered System Message Adherence (Citable Statements) from the "System Message Adherence (Citable Statements)" section of the concise ruleset, create an SMInstructionValidation object.
        - sm_id: Extract the ID (e.g., "SM-1", "SM-2").
        - instruction: Copy the full text of the instruction.
        - classification: Assign an appropriate classification (e.g., 'Context & Domain Awareness', 'Tool Usage Guidelines', 'Assistant Behavior & Tone', 'System Settings', 'Search Refinement').
        - followed: Determine if the assistant's behavior throughout the conversation adhered to this specific instruction.
      turn_breakdown_list: For each turn from 1 to the number_of_turns specified in the task metadata (e.g., if number_of_turns: 11, then evaluate turns 1 through 11), create a TurnDetail object. Use the "Turn-by-Turn Breakdown for Evaluation" section of the user prompt as guidance, but ensure you evaluate exactly the number of turns specified in the metadata.
        - turn_number: The turn number.
        - turn_type: The type of turn (e.g., "Default clarification", "Sequential tool call", "Model failure", "Parallel tool call"). Remember that multiple tool calls within a single turn should be captured as part of that turn.
        - description: Provide a comprehensive description of all actions/outcomes within that turn, including all tool calls and assistant responses that occurred between the user messages. This should capture the complete interaction cycle.
        - passed: This is True if the turn executed as expected. This includes turns designated as "Model failure" in the prompt's summary if they are indeed legitimate failures that fulfill the task's criteria for testing failure handling. Model failure turns should be marked as passed: True when they correctly demonstrate the intended failure scenario.
        - cited_sm_instructions: A list of sm_ids (e.g., "SM-16", "SM-12") from the "System Message Adherence (Citable Statements)" that are relevant to the turn's actions or failures.
        - model_failure_details: If turn_type is "Model failure", you must provide ModelFailureDetails.
          - error_labels: A list of the most appropriate error labels from the playbook (e.g., wrong_param_value, required_param_missing, wrong_tool_selected, unsatisfactory_summary, no_tool_triggered, tool_over_triggered, parallel_calls_missing, tool_call_not_parsable, others). These should be inferred based on the Model Failure definition and the provided context.
          - critic_comment: A detailed explanation in the third person of why the model failed in that specific turn, drawing upon the playbook's error definitions and turn type definitions.
          - reasoning_response: A hypothetical first-person explanation from the model's perspective about why it made the mistake.
      
      IMPORTANT: If the turn-by-turn breakdown in the prompt shows fewer turns than the number_of_turns in metadata, you must still evaluate all turns up to the number_of_turns specified in metadata. For any missing turns in the breakdown, infer the turn type and description based on the conversation flow and context.
      
      sequential_tool_call_summary, parallel_tool_call_summary, model_failure_summary, flow_break_status, sr_turn: Extract these values directly from the "Overall Task Metadata" section of the user prompt.
      New task-level numerical summaries (total_model_failures, total_parallel_tool_calls, total_sr_turns, total_contextual_turns, total_sequential_tool_calls):
        - total_model_failures: Count the number of turns in turn_breakdown_list where turn_type is "Model failure". This count should be based on the actual turns evaluated (up to number_of_turns from metadata).
        - total_parallel_tool_calls: Count the number of turns in turn_breakdown_list where turn_type includes "Parallel tool call". This count should be based on the actual turns evaluated (up to number_of_turns from metadata).
        - total_sr_turns: If the inferred_task_category is "Search Refinement" (or "SR" is explicitly indicated in a turn type), this count should reflect the actual number of turns where Search Refinement was genuinely attempted and applied. If SR: Turn X is specified in the prompt, this should generally be at least 1, but confirm if actual turns reflect this.
        - total_contextual_turns: If the inferred_task_category is "Contextual Information", count turns where the primary action involves retrieving context-specific data (e.g., get_current_location, get_wifi_status). This count should be based on the actual turns evaluated (up to number_of_turns from metadata).
        - total_sequential_tool_calls: Count the number of turns in turn_breakdown_list where turn_type includes "Sequential tool call". This count should be based on the actual turns evaluated (up to number_of_turns from metadata).
      Final Evaluation Checklist Fields (respecting_sub_categories, no_flow_breaks, three_model_failures, at_least_3_user_prompts_that_trigger_tool_chains, default_clarification_behavior_followed): Set these boolean fields based on your comprehensive analysis of the conversation and adherence to the prompt's Overall Task Metadata and rules.
      task_level_pass_fail: Determine the overall pass/fail status for the task based on the "Evaluation Criteria for Task-Level Pass/Fail" above.
      task_level_reasoning: Provide a detailed explanation for the task_level_pass_fail status, clearly stating which criteria were met or missed according to the new logic.
      ending_remark: Provide a friendly and concise concluding remark.
      
      VALIDATION CHECK: Before finalizing the response, verify that:
      1. The turn_breakdown_list contains exactly the number of turns specified in the metadata's number_of_turns field
      2. All turn numbers from 1 to number_of_turns are present and sequential
      3. The numerical summaries accurately reflect the counts from the evaluated turns
       """
        
    async def review(self, content: str):
        self.gcp.config(self.system_message, self.schema)
        
        async for chunk in self.gcp.generate_stream(content):
            print(chunk, end="", flush=True)
            pass  # Consume all chunks
        
        return self.gcp.clean_response()



