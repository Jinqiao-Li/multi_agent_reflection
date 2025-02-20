import spacy
import re
from spacy_llm.util import assemble

load_dotenv()

config_path = "fewshot.cfg"
config_path_no_irrelevant = "fewshot_no_irrelevant.cfg"


def check_api_key():
    if not os.getenv("OPENAI_API_KEY", None):
        logging.info(
            "OPENAI_API_KEY env variable was not found. "
            "Set it by running 'export OPENAI_API_KEY=...' and try again."
        )


check_api_key()
nlp = assemble(config_path, overrides={})


def categorize_text_quotations(df, nlp):
    # Prepare batch size for processing
    batch_size = min(50, max(10, len(df) // 10))

    # Initialize results storage for category columns
    category_results = {
        cat: [] for cat in ["factual", "cognitive", "emotional", "irrelevant"]
    }

    # Process quotations in batches
    for doc in tqdm(
            nlp.pipe(df["quotation"].astype(str), batch_size=batch_size),
            total=len(df),
            desc="Categorizing",
    ):
        # Append binary results for each category to respective lists
        for category in category_results.keys():
            category_results[category].append(
                1 if doc.cats.get(category, 0) >= 0.5 else 0
            )

    # Add results to DataFrame as new columns
    for category, results in category_results.items():
        df[category] = results

    return df.copy()