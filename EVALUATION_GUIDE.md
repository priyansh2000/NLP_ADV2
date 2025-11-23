# RAG System Evaluation Guide

## Overview

The `evaluation.ipynb` notebook provides comprehensive evaluation of the RAG system using **RAGAS** (Retrieval-Augmented Generation Assessment) framework with 5 key metrics.

---

## Evaluation Metrics

### 1. Faithfulness (0-1)

**What it measures:** How factually accurate is the answer based on the given context?

- **High Score (0.8-1.0)**: Answer contains only information from the context, no hallucinations
- **Low Score (0-0.4)**: Answer contains made-up or fabricated information

**Why it matters:** Ensures the system doesn't generate false information

---

### 2. Answer Relevancy (0-1)

**What it measures:** How relevant is the answer to the question asked?

- **High Score (0.8-1.0)**: Answer directly addresses the question
- **Low Score (0-0.4)**: Answer is off-topic, vague, or doesn't address the question

**Why it matters:** Ensures the system provides useful, on-topic responses

---

### 3. Context Precision (0-1)

**What it measures:** How precise is the retrieved context? (Signal-to-noise ratio)

- **High Score (0.8-1.0)**: All retrieved chunks are relevant and useful
- **Low Score (0-0.4)**: Many irrelevant chunks retrieved

**Why it matters:** Ensures the retrieval system finds the right information

---

### 4. Context Recall (0-1)

**What it measures:** How much of the ground truth information is captured in the retrieved context?

- **High Score (0.8-1.0)**: Context contains all information needed to answer
- **Low Score (0-0.4)**: Missing important information in retrieved context

**Why it matters:** Ensures the system retrieves complete information

---

### 5. Answer Correctness (0-1)

**What it measures:** Overall correctness of the answer compared to ground truth

- Combines factual accuracy and semantic similarity
- **High Score (0.8-1.0)**: Answer matches expected answer
- **Low Score (0-0.4)**: Answer significantly differs from ground truth

**Why it matters:** Overall quality check of the generated answer

---

## Score Interpretation

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 0.8 - 1.0 | Excellent | System performing very well |
| 0.6 - 0.8 | Good | System performing adequately |
| 0.4 - 0.6 | Fair | System needs improvement |
| 0.0 - 0.4 | Poor | System needs significant work |

---

## How to Run Evaluation

### Prerequisites

1. Backend API must be running on port 8000
2. Google API key must be configured
3. Required libraries installed (ragas, datasets, langchain-google-genai)

### Steps

```bash
# 1. Start the backend
python start.py

# 2. Open Jupyter notebook
cd /Users/prabhav.pandey_int/Desktop/NLP_ADV2/app
jupyter notebook evaluation.ipynb

# 3. Run all cells
```

Or run from command line:

```bash
cd /Users/prabhav.pandey_int/Desktop/NLP_ADV2
source venv/bin/activate
export GOOGLE_API_KEY="your-key"
jupyter nbconvert --to notebook --execute app/evaluation.ipynb
```

---

## Test Dataset

The evaluation uses 8 test questions about Julius Caesar:

1. Who is Brutus?
2. What does the Soothsayer say to Caesar?
3. Why does Brutus kill Caesar?
4. What happens at Caesar's funeral?
5. Who is Cassius?
6. What is the relationship between Caesar and Brutus?
7. What role does Mark Antony play?
8. What are Caesar's last words?

Each question has a ground truth answer for comparison.

---

## Output Files

After running the evaluation, you'll get:

1. **evaluation_results.json** - Overall scores and detailed results
2. **evaluation_results.csv** - Detailed results in CSV format

---

## Understanding Results

### Overall Scores

The notebook displays:
- Individual metric scores
- Average score across all metrics
- Performance categorization (Excellent/Good/Fair/Poor)

### Per-Question Analysis

For each question, you can see:
- Generated answer vs ground truth
- Individual metric scores
- Number of context chunks retrieved

### Sample Output

```
RAGAS EVALUATION RESULTS
================================================================================

Overall Scores (0-1 scale, higher is better):

1. Faithfulness:        0.8500
   -> How factually accurate is the answer based on context?

2. Answer Relevancy:    0.9200
   -> How relevant is the answer to the question?

3. Context Precision:   0.7800
   -> How precise is the retrieved context?

4. Context Recall:      0.8100
   -> How much ground truth is captured in context?

5. Answer Correctness:  0.8400
   -> Overall correctness of the answer

================================================================================
AVERAGE SCORE: 0.8400
================================================================================
```

---

## Using Results for Improvement

### If Faithfulness is Low:
- Check if LLM is hallucinating
- Improve prompt to stay within context
- Reduce temperature parameter

### If Answer Relevancy is Low:
- Improve question understanding
- Refine prompt engineering
- Check if retrieved context is relevant

### If Context Precision is Low:
- Improve embedding model
- Tune retrieval parameters (k value)
- Improve chunking strategy

### If Context Recall is Low:
- Increase number of retrieved chunks (k)
- Improve chunking to capture more context
- Check if important information is in the database

### If Answer Correctness is Low:
- Improve LLM model quality
- Better prompt engineering
- Ensure context contains relevant information

---

## Comparison with Other Systems

Use these metrics to:

1. **Track improvements over time** - Run evaluation after each change
2. **Compare different models** - Test different LLMs or embedding models
3. **A/B testing** - Compare different retrieval strategies
4. **Benchmark** - Compare against industry standards

---

## Technical Details

### Libraries Used

- **ragas**: Main evaluation framework
- **datasets**: Hugging Face datasets for data management
- **langchain-google-genai**: Google Gemini integration
- **pandas**: Data analysis and visualization

### Configuration

- **LLM**: Google Gemini 2.5 Flash (temperature=0 for consistency)
- **Embeddings**: Google Embedding-001
- **Retrieval**: Top-3 chunks per query
- **Timeout**: 30 seconds per API call

---

## Best Practices

1. **Run regularly**: Evaluate after each major change
2. **Use consistent test data**: Same questions for fair comparison
3. **Document changes**: Note what changed between evaluations
4. **Analyze failures**: Look at low-scoring questions individually
5. **Iterate**: Use insights to improve the system

---

## Troubleshooting

### Common Issues

**Issue**: "API key not configured"
**Solution**: Set GOOGLE_API_KEY environment variable

**Issue**: "Backend not responding"
**Solution**: Ensure backend is running on port 8000

**Issue**: "Module not found: ragas"
**Solution**: Install required packages: `pip install ragas datasets langchain-google-genai`

**Issue**: "Evaluation takes too long"
**Solution**: Reduce number of test questions or increase timeout

---

## Next Steps

After running evaluation:

1. Review the overall scores
2. Identify weak areas
3. Make targeted improvements
4. Re-run evaluation
5. Compare results
6. Iterate until satisfied

---

## Resources

- **RAGAS Documentation**: https://docs.ragas.io/
- **Evaluation Notebook**: `app/evaluation.ipynb`
- **Results**: `evaluation_results.json` and `evaluation_results.csv`

---

**Remember**: Good metrics lead to good systems. Regular evaluation is key to maintaining and improving RAG system quality!

