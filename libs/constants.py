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

NEW_COLUMN_FIELDS = """
{
  "column_name": "injury_mechanism",
  "extraction": "Use keyword matching and pattern recognition to identify common injury mechanisms like 'fell', 'cut', 'burned', 'jumped', etc.",
  "example": "From '12YR F FELL ON STAIRSDX CHI', extract 'FELL'",
},
{
  "column_name": "location_of_injury",
  "extraction": "Identify and extract phrases that indicate where the injury occurred, such as 'at home', 'at school', etc.",
  "example": "From '83YOF WITH STRAIN TO NECK AFTER FALLING DOWN THREE STEPS', extract 'STEPS'.",
},
{
  "column_name": "injury_type",
  "extraction": "Use keywords to categorize the type of injury, which might include 'fracture', 'laceration', 'burn', 'strain', etc.",
  "example": "From '8 YOM WITH ELECTRICAL BURN FROM STICKING PAPER CUP INTO ELECTRICALOUTLET DXBURNS FINGER', extract 'ELECTRICAL BURN'.",
},
{
  "column_name": "activity_at_injury",
  "extraction": "Identify phrases that describe the activity the individual was performing at the time of injury, such as 'playing basketball', 'lifting boxes', or 'doing karate'.",
  "example": "From '30YF ACC CUT LT MIDDLE FINGER ON A KNIFE CUTTING MEATLAC', extract 'CUTTING METAL'",
}
"""

PROMPT_EXTRACT_FIELDS = """
You are tasked with extracting information from a narrative field to generate 4 new fields. The entire data record will be provided including narrative field, and you must analyze it to extract relevant information for each new field.

Here is the data record you will be working with:
{data}

Your task is to extract information for the following 4 new fields:

{columns}

If any information is unclear or missing for a particular field, use "unknown" as the value.

Examples:
1. For the narrative "12YR F FELL ON STAIRS DX CHI":
   - injury_mechanism: "fell"
   - location_of_injury: "stairs"
   - injury_type: "chi" (Closed Head Injury)
   - activity_at_injury: "unknown"

2. For the narrative "8 YOM WITH ELECTRICAL BURN FROM STICKING PAPER CUP INTO ELECTRICAL OUTLET DX BURNS FINGER":
   - injury_mechanism: "sticking object into outlet"
   - location_of_injury: "unknown"
   - injury_type: "electrical burn"
   - activity_at_injury: "sticking paper cup into electrical outlet"

Remember to focus only on the information provided in the given narrative. Do not make assumptions or add information that is not explicitly stated or strongly implied in the text.


Provide your output in the following JSON format:

<output>
{{
    "injury_mechanism": "xxx",
    "location_of_injury": "xxx",
    "injury_type": "xxx",
    "activity_at_injury": "xxx"
}}
</output>

Now, analyze the provided narrative and extract the required information for each field.
"""
