#!/usr/bin/env python3
"""Reference outputs from Claude (Sonnet 4.6) for quality evaluation.

These are ideal responses for each prompt. Quality of quantized outputs
is measured as cosine similarity to these references.
"""

REFERENCES = {
    "The capital of France is": """The capital of France is Paris. Paris is a major European city located in northern France on the Seine River. It is the political, economic, and cultural center of the country, home to iconic landmarks such as the Eiffel Tower, the Louvre Museum, and Notre-Dame Cathedral.""",

    "Explain photosynthesis in one paragraph.": """Photosynthesis is the biological process by which green plants, algae, and some bacteria convert light energy from the sun into chemical energy stored in glucose molecules. Using chlorophyll pigments in chloroplasts, organisms absorb sunlight and combine water (H2O) absorbed from the soil with carbon dioxide (CO2) taken in from the air, producing glucose (C6H12O6) and releasing oxygen as a byproduct. The overall reaction is 6CO2 + 6H2O + light energy → C6H12O6 + 6O2. Photosynthesis is the foundation of most food chains on Earth and is responsible for the oxygen in our atmosphere.""",

    "Write a Python function to compute the nth Fibonacci number.": """Here is a Python function to compute the nth Fibonacci number:

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

This iterative implementation uses two variables a and b to track consecutive Fibonacci numbers, updating them in a loop. It runs in O(n) time and O(1) space, making it efficient for large values of n. The base cases handle n=0 (returns 0) and n=1 (returns 1).""",

    "What are the main symptoms of a stroke?": """The main symptoms of a stroke include sudden numbness or weakness in the face, arm, or leg, especially on one side of the body. Other common signs are sudden confusion, trouble speaking, or difficulty understanding speech. Vision problems in one or both eyes, sudden trouble walking, dizziness, loss of balance or coordination, and severe headache with no known cause are also warning signs. The acronym FAST is widely used: Face drooping, Arm weakness, Speech difficulty, Time to call emergency services. Immediate medical attention is critical because early treatment with clot-dissolving drugs or mechanical thrombectomy can greatly improve outcomes.""",

    "Describe the structure of a haiku with an example.": """A haiku is a traditional Japanese poetic form consisting of three lines with a specific syllable pattern: 5 syllables in the first line, 7 syllables in the second line, and 5 syllables in the third line, for a total of 17 syllables. Haiku traditionally capture a moment in nature and often include a seasonal reference called a kigo. Here is a classic example by Matsuo Basho:

An old silent pond
A frog jumps into the pond—
Splash! Silence again.

This haiku evokes stillness interrupted by a fleeting action, characteristic of the form's meditative and observational qualities."""
}


if __name__ == "__main__":
    import json
    print(json.dumps(REFERENCES, indent=2))
