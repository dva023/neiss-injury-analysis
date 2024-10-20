MODEL_GPT_4_MINI = "gpt-4o-mini"
MODEL_GPT_4 = "gpt-4o"
MODEL_GEMINI = "gemini-1.5-flash-002"
MODEL_LOCAL = "llama3.2"  # 3b
MODEL_CLAUDE = "claude-3-5-sonnet-20240620"

PROMPT_CREATE_NEW_FIELDS = """

You are an expert data analyst specializing in healthcare information systems. Your task is to analyze a sample from the National Electronic Injury Surveillance System (NEISS) dataset and propose **new** columns that can be extracted from the narrative field. This analysis is part of a larger project to enhance the dataset's structure and facilitate more detailed injury analysis.


Your objective is to examine the "Narrative" field in the provided sample and identify common pieces of information that appear frequently across multiple entries. These common elements should be suitable for extraction into new columns, which will enhance the dataset's structure and facilitate more detailed analysis.

Guidelines for identifying extractable information:
1. Look for recurring types of information across multiple narratives.
2. Consider information that provides additional context to the injury or circumstances.
3. Focus on data that could be consistently extracted from most narratives.
4. Think about what information would be valuable for analysis or categorization of injuries.
5. Keep in mind that this analysis will be repeated with different sample sets, so propose columns that are likely to be consistently present.

Here is a sample of the NEISS dataset:
{dataset}

For each proposed new column, provide:
1. A clear and concise column name.
2. A description of how this information could typically be extracted from the narratives.
3. An example of how to extract this information from one of the sample narratives.

e.g.
{{
    'column_name': 'injury_mechanism',
    'extraction': "Use keyword matching and pattern recognition to identify common injury mechanisms like 'fell', 'cut', 'burned', etc.",
    'example': "From '12YR F FELL ON STAIRS DX CHI', extract 'FELL'"
}}

Respond in JSON format: {{"proposed_columns": [{{"column_name": "xxx", "extraction": "xxx", "example": "xxx"}},...]}}
"""

PROMPT_EXTRACT_CATEGORIES = """You are a Data Analytics at Lightspeed who help to choose the best evalution for the conversation between agents and customers.
    Here is the masked conversation:
    ###
    {}
    ###

    Here are the evaluations from different models:
    {}

    Please provide your answer with the best evaluation in JSON format strictly, make sure all fields are filled. Correct the fields by your best knowledge if there are any mistakes.
    For example:
    {{
        customer_sentiment: integer # from 1 to 5
        reason_for_customer_sentiment: string
        conversation_sentiment: integer # from 1 to 5
        reason_for_conversation_sentiment: string
        intent: string
        problem: string
        solved: integer # 0 means not solved, 1 means solved
        need_follow_up: integer 0 means no, 1 means yes
        root_cause: string
        suggested_solution: string
        product: string
        category: string
        keywords: array
        model_name: string # new field, the model name you choose
        reason_for_choice: string # new field, the reason why you choose this model
    }}
"""
