PROMPT_TEMPLATES = {
    "FormalLanguageStyle": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response meets the formal language style requirements.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response uses a formal tone and appropriate formal expressions.
2. Score 0.7: The response is generally formal but contains some minor informal elements or occasional less formal expressions.
3. Score 0.0: The response completely fails to demonstrate "formal tone" or "formal expressions".

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

"InformalLanguageStyle": """
You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response meets the informal language style requirements.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response uses an informal tone.
2. Score 0.7: The response can generally be considered informal.
3. Score 0.0: The response mainly uses a formal tone.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "ProfessionalTerminology": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response meets the professional technical language style requirements.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The overall writing style of the response is professional technical, using professional terminology.
2. Score 0.7: The response can generally be considered professional, but uses little or no professional terminology.
3. Score 0.0: The response completely fails to meet the requirements of "professional technical language style".

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "PoeticStyle": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response meets the poetic language style requirements.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The overall writing style of the response can be called "poetic", employing poetic techniques or methods.
2. Score 0.7: The response generally follows a poetic style or format, but uses few or no poetic techniques or methods.
3. Score 0.0: The response completely fails to meet the requirements of "poetic language style".

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "FormalLetterFormat": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response meets the formal letter format requirements.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response meets the requirements of "formal letter format", including various elements of a letter, such as greetings, signatures, etc.
2. Score 0.7: The response can generally be recognized as a letter, but the format is not rigorous.
3. Score 0.0: The response shows no indication of being in a formal letter format.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "HumorousTone": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response meets the humorous tone requirements.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: Contains humorous elements and uses witty ways of expression.
2. Score 0.7: No clear humorous techniques, but still brings a smile to one's face.
3. Score 0.0: The response shows no indication of any "humorous tone".

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "PositiveTone": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response's main tone expresses positive or optimistic emotions.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response content conveys positive emotions or attitudes, such as optimism, confidence, etc.
2. Score 0.7: The response is generally positive, containing only a few negative or pessimistic words.
3. Score 0.0: The response shows no indication of positive or optimistic emotions.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "NegativeTone": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response's main tone expresses negative or pessimistic emotions.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response content conveys negative, pessimistic, disappointed, or depressed emotions.
2. Score 0.7: The overall tone tends to be negative rather than neutral or positive.
3. Score 0.0: The response shows no indication of negative or pessimistic emotions.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "SarcasticTone": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response's main tone expresses sarcastic or mocking emotions.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response content uses irony, mockery, or sarcasm, or the tone carries sentiments of ridicule, belittlement, or disdain.
2. Score 0.7: The overall response feels sarcastic or mocking, but perhaps not obviously.
3. Score 0.0: The response shows no indication of sarcastic or mocking emotions.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "AngryTone": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response's main tone expresses angry or furious emotions.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response content conveys strong emotions of anger, fury, or dissatisfaction, or the tone carries obvious aggression, impatience, or indignation.
2. Score 0.7: The overall tone tends to express anger rather than calm, gentle, or neutral emotions.
3. Score 0.0: The response shows no indication of "anger or fury".

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "IncludeJokes": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response includes at least 3 jokes.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response clearly contains at least 3 jokes. There is no length restriction for "jokes" - even if it's as short as one word, as long as it has joke elements, it can be counted as a joke.
2. Score 0.7: The "jokes" in the response are somewhat forced, or they appear but only two in number.
3. Score 0.0: The response contains only one joke, or none at all.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "IncludeQuotes": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response includes at least 3 famous quotes.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response clearly cites at least 3 different famous quotes. Note that even for the same famous person, two different quotes should be counted separately. The "famous person" or "quote" doesn't necessarily need to be well-known - as long as it's a quote from someone relevant to the topic, it can be considered a "famous quote".
2. Score 0.7: The response contains only two famous quotes, or the famous quotes that appear in the response are not obvious.
3. Score 0.0: The response contains only one quote, or no famous quotes at all.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "MentionFamousPerson": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response mentions a famous person related to the topic and briefly introduces their achievements.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response mentions a person relevant to the topic and briefly introduces their main achievements or contributions, even if the person is not that "famous".
2. Score 0.7: The response mentions a famous person, but they are not very relevant to the topic, or their achievements are not introduced.
3. Score 0.0: The response does not mention any famous person at all.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "ThreeLanguages": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response includes at least three different languages.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: The response clearly uses three or more different languages.
2. Score 0.7: The response uses two different languages.
3. Score 0.0: The response is output in a single language and does not include any other languages.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
""",

    "RepeatInDifferentLanguage": """You are an AI multilingual evaluation expert who is precise and impartial. You need to help me assess whether the following model responses comply with the requirements in the instructions and return a score of 0, 0.7, or 1.

Please evaluate whether the following response repeats once and uses a different language the second time.

Instruction:
{instruction}

Model Response:
{response}

Detailed Scoring Criteria:
1. Score 1.0: Whether the response contains two languages and both languages express the same content. The descriptions in the two languages do not necessarily need to express exactly the same meaning, as long as the general content expressed is similar.
2. Score 0.7: The response contains two languages, but the expressions in the two languages differ greatly.
3. Score 0.0: The response does not repeat at all, or only uses one language.

Please note that as a fair and objective evaluator, you should not adhere to an "ambiguous" principle and give a score of 0.7 regardless of circumstances, nor should you be too lenient or too strict. Your scoring must strictly follow the above scoring criteria!

You must only respond with one of these three numbers: 0, 0.7, or 1. Do not provide any explanations or additional text! Do not provide any explanations beyond these three numbers, do not make any narratives! Even if you have questions or want to discuss further, please remain restrained and output only one number!
"""
}