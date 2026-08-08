# LangArav — A domain-specific programming language for programmable image manipulation


## What LangArav Is?

LangArav is a lightweight, interpreted domain-specific programming language (DSL) built from scratch in Python. It features a custom Lexer, AST Parser, and Tree-Walking Interpreter designed specifically for programmatic image processing, algorithmic graphics, mathematical frequency filtering, and computer vision pipelines.

## Why It Exists?

Standard image editing scripts in raw Python require juggling multiple libraries (Pillow, OpenCV, NumPy, rembg, SciPy) with constant color channel conversions (RGB vs. BGR vs. Grayscale), array reshaping, and type casting.LangArav abstracts away the glue code, letting you write intuitive, high-level code where images behave like native language objects that support math operators (img + 50, img1 + img2), procedural drawing, frequency filtering, and chainable method calls.

## 30-Second Example

Python 


    img = load("photo.jpg") # Load an image and create a custom processing pipeline

    func Cyberpunk(): # Define a custom function to apply a cyberpunk aesthetic

      img = img.vaporwave() 
  
      img = img.neon()
  
      img = img.graph("sin(x)", "cyan", 3)
  
      img.save("output.jpg")
 
    Cyberpunk() # Execute the pipeline

    img = img.circle(250, 250, 100, "cyan", 3) # Draw annotations and save
    
    img.save("output.jpg")
    
    img.show()

## Key Capabilities

1. Hybrid Vision Engine: Combines Pillow surface operations with OpenCV spatial algorithms under a single unified syntax.
2. Pixel & Array Arithmetic: Perform matrix math on images using native operators (+, -, *, /).
3. Frequency Domain Processing: Native support for FFT, DFT, Bandpass/Bandstop, and Notch filters.
4. Geometric & Mesh Distortions: Swirl, Mesh Warp, Liquify, Bulge, Pinch, and Fish-Eye lens transformations.
5. Object Detection & AI: Out-of-the-box object detection (Haar cascades), AI background removal (rembg), and non-local means denoising.
6. Equation Graphing: Plot mathematical equations (sin(x), polynomial grids) directly onto image canvases.
  
## Example Image Transformations

1. Distortions & Geometry: .meshWarp(), .liquify(), .swirl(), .pinch(), .bulge(), .lens(), .sphere()
2. Artistic Filters.cartoon(), .sketch(), .vaporwave(), .neon(), .glitch(), .pixelate(), .mosaic()
3. Vision & Edge Detection: .sobel(), .canny(), .harris(), .shiTomasi(), .detect(), .objectCount()
4. Frequency Filtering: .bandpass(), .bandstop(), .notch(), .magnitude(), .phase(), .inverseFFT()
5. Color & Science: .hsv(), .lab(), .gamma(), .exposure(), .temperature(), .whiteBalance(), .clahe()
6. Drawing Primitives: .line(), .circle(), .rectangle(), .ellipse(), .polygon(), .arrow(), .text() etc.

## Language Features

1. Block Scoping: Python-style clean indentation (INDENT / DEDENT token tracking).
2. Functions: Define custom procedural blocks using the func keyword.
3. Object-Oriented Programming: Full support for class definitions, instance creation (a = Aura()), and single inheritance.
4. Dynamic Typing: Automatic runtime handling of integers, floats, strings, lists, dictionaries, and image instances.
5. Built-in Functions: Global language primitives including load(), blend(), and print().

## Documentation

Methods.txt — Explanation on every method that can be done on an image.

Structure.txt — Lexer tokens, AST nodes etc. and how the data moves from one stage to another

LanguageFeatures.txt — Explaining every feature other than the methods of the languages going from the normal language features like variables to built-in functions.

## Installation & Setup

1. Prerequisites: Ensure you have Python 3.9+ installed along with the required engine dependencies:

   pip install pillow opencv-python numpy rembg pywavelets scikit-image
   
2. Running LangArav:

   Clone the repository and pass your raw code string into langarav.py by putting it into the triple quotes """ at the end of the code, with the        ends securely tucked in by    the quotes:
   
   git clone https://github.com/your-username/LangArav.git
   cd LangArav
   python langarav.py
   
## Current V1 Status

1. Core Engine: Fully functional Lexer, AST Parser, and Dynamic Interpreter written in Python.
2. Scope & OOP: Stable implementation of variables, class inheritance, class instantiation, and func block definitions.
3. Pipeline: Supported global functions (load, blend, print) and 80+ chainable image methods.

## V2 Roadmap

[ ] Parameter passing support for user-defined func declarations (e.g., func Aura(x, y):).

[ ] Explicit return statements for local function scopes.

[ ] For and while loops available in the language.

[ ] Allowing for files to be used for running langarav code instead of putting it in the python code itself.
