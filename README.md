===
Image Format (png, jpeg, ...)
===
Image channels (rgb, b&w, ...)
===
Image depth (8bit, 10bit, ...)
===
Image size (w\*h)
===
Channel Division
===
Based on mentioned details:

1. Statistical, Coding Redundancy
   a) Entropy
   b) Self Information
   c) Distribution
   d) Probability
   e) Huffman
   f) Golomb
   g) Golomb-Rice
   h) Arithmetic

2. Spatial Redundancy
   +) Prediction
   a) e = x - x'
   b) Lossless JPEG
   c) 2nd order
   d) 3rd order
   e) MED
   f) GAP
   g) ALCM
   h) LS-Based Adaptive Predator
   i) By using Context
   j) Bias Cancellation
   k) Error Remapping (1, 2, 3)
   l) RLE
   m) JPEG-LS
   n) Context Quantization
   o) CALIC

3. Psycho-Visual Redundancy
   a) Quantization
   b) Transform coding (DCT)
   c) JPEG Standard-Quantization
   d) JPEG Standard-Entropy coding
   e) JPEG Standard-Reconstruction
   f) JPEG Standard-Image Quality Control

4. Spectral Redundancy
   a) YCbCr

5. Temporal Redundancy
   a) Motion Vector
   b) Block Matching
   -) Full Search
   -) 3 Step Search
   -) 4 Step Search
   -) Diamond Search
   -) Hexagonal Block Search
   c) MPEG Standard E/D
   ===
   Encoder/Decoder
