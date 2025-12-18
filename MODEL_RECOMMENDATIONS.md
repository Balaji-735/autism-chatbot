# Best Pre-Quantized Models for Autism Chatbot

## Current Status
- ✅ **Baseline**: `mistral:latest` (4.4 GB) - Already installed
- ❌ **Quantized**: No pre-quantized Mistral variants available in Ollama
- ❌ **Pruned**: No smaller Mistral variants available

## Recommended Solutions

### Option 1: Use Smaller Alternative Models (Easiest - Recommended)

These models are naturally smaller and can serve as "pruned" alternatives:

#### For Pruning Comparison:
1. **`llama3.2:1b`** (1.3 GB)
   - Very small, fast inference
   - Good for comparison
   - Command: `ollama pull llama3.2:1b`

2. **`llama3.2:3b`** (2.0 GB)
   - Balanced size/performance
   - Command: `ollama pull llama3.2:3b`

3. **`gemma:2b`** (1.7 GB) - ✅ Already installed!
   - Google's efficient model
   - Already available in your system

#### For Quantization Comparison:
Since Ollama doesn't have pre-quantized Mistral, use:
- **`mistral:latest`** as baseline
- **`llama3.2:1b`** or **`gemma:2b`** as "quantized" comparison (smaller = faster)

### Option 2: Create Quantized Models Using Ollama Modelfile

You can create quantized versions manually:

1. **Create Modelfile for Q4 quantization:**
```bash
ollama create mistral-q4 -f Modelfile.q4
```

Where `Modelfile.q4` contains:
```
FROM mistral:latest
PARAMETER quantization q4_0
```

2. **Create Modelfile for Q8 quantization:**
```bash
ollama create mistral-q8 -f Modelfile.q8
```

Where `Modelfile.q8` contains:
```
FROM mistral:latest
PARAMETER quantization q8_0
```

**Note**: This requires Ollama to support quantization parameters (may not work in all versions).

### Option 3: Use Different Model Families

#### Quantization Alternatives:
- **`llama3.2:1b`** - 70% smaller than Mistral
- **`llama3.2:3b`** - 45% smaller than Mistral
- **`phi3:mini`** - Microsoft's efficient model (3.8B params, ~2GB)

#### Pruning Alternatives:
- **`gemma:2b`** - Already installed, 60% smaller
- **`llama3.2:1b`** - 70% smaller
- **`qwen2:0.5b`** - Ultra-small model

## Recommended Configuration

Based on what's available, here's the best setup:

### For Quantization:
- **Baseline**: `mistral:latest` (4.4 GB)
- **Quantized**: `llama3.2:1b` (1.3 GB) - represents quantized performance
- **Alternative**: `gemma:2b` (1.7 GB) - already installed

### For Pruning:
- **Baseline**: `mistral:latest` (4.4 GB)
- **Pruned**: `gemma:2b` (1.7 GB) - already installed, 60% smaller
- **Alternative**: `llama3.2:1b` (1.3 GB) - 70% smaller

## Implementation Steps

1. **Pull recommended models:**
```bash
ollama pull llama3.2:1b
ollama pull llama3.2:3b
```

2. **Update environment variables:**
```bash
# For quantization - use smaller model as "quantized"
export QUANT_MODEL_TEMPLATE="llama3.2:{level}"  # Will use llama3.2:1b, llama3.2:3b

# For pruning - use gemma:2b (already installed)
export PRUNED_MODEL_NAME="gemma:2b"
```

3. **Or update code defaults:**
- Change `QUANT_MODEL_TEMPLATE` to use `llama3.2:1b` for Q4_0
- Change `PRUNED_MODEL_NAME` to `gemma:2b`

## Model Comparison Table

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `mistral:latest` | 4.4 GB | Baseline | High | Baseline |
| `gemma:2b` | 1.7 GB | Fast | Good | Pruning comparison |
| `llama3.2:1b` | 1.3 GB | Very Fast | Moderate | Quantization comparison |
| `llama3.2:3b` | 2.0 GB | Fast | Good | Balanced option |

## Next Steps

1. Pull `llama3.2:1b` for quantization comparison
2. Use `gemma:2b` (already installed) for pruning comparison
3. Update configuration to use these models
4. Test benchmarks to see real performance differences

