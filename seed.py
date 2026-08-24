"""
Seed script — populate pgvector with the hardcoded IOE syllabus content.

This replaces the old in-memory FAISS vectorstore with persistent pgvector
rows, using the same syllabus data that was hardcoded in the original app.py.

Usage:
    python seed.py

Prerequisites:
    - Postgres running with pgvector enabled
    - DATABASE_URL and GOOGLE_API_KEY set in .env
    - Schema created (happens automatically, or run: psql $DATABASE_URL -f schema.sql)
"""

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings  # noqa: E402
from app.database import init_db  # noqa: E402
from app.rag.embeddings import embed_texts  # noqa: E402
from app.repositories import document_repository  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# The same syllabus content that was hardcoded in the old app.py
# ---------------------------------------------------------------------------

SYLLABUS_CONTENT = {
    "Programming in C": {
        "Introduction to Programming": """
Introduction to Programming:
- What is programming and why is it important?
- History of programming languages
- Overview of C programming language
- Characteristics of C: structured, portable, efficient
- Applications of C programming
- Programming paradigms: procedural vs object-oriented
- Problem-solving approach in programming
""",
        "Basic Structure of C Program": """
Basic Structure of C Program:
- Preprocessor directives (#include, #define)
- Header files and their purpose
- Main function and its significance
- Declaration section for variables
- Executable statements
- Comments in C (single-line and multi-line)
- Compilation process: preprocessing, compilation, linking
- Hello World program example
""",
        "Variables and Data Types": """
Variables and Data Types:
- What are variables? Declaration and initialization
- Data types: int, float, double, char
- Size of data types using sizeof operator
- Constant variables and literals
- Type conversion: implicit and explicit
- Scope of variables: local and global
- Storage classes: auto, static, extern, register
""",
        "Operators and Expressions": """
Operators and Expressions:
- Arithmetic operators (+, -, *, /, %)
- Relational operators (<, >, <=, >=, ==, !=)
- Logical operators (&&, ||, !)
- Assignment operators (=, +=, -=, *=, /=)
- Increment/decrement operators (++, --)
- Bitwise operators (&, |, ^, ~, <<, >>)
- Conditional operator (? :)
- Operator precedence and associativity
""",
        "Control Structures": """
Control Structures:
- Decision making: if, if-else, nested if-else
- Switch-case statement with break and default
- Loops: for, while, do-while
- Loop control statements: break, continue, goto
- Nested loops and their applications
- Examples: factorial, fibonacci, prime numbers
""",
        "Functions and Recursion": """
Functions and Recursion:
- Function definition and declaration
- Function parameters and return values
- Call by value and call by reference
- Scope of variables in functions
- Static variables in functions
- Recursion: concept and implementation
- Examples: factorial, fibonacci using recursion
- Advantages and disadvantages of recursion
""",
        "Arrays and Strings": """
Arrays and Strings:
- Array declaration and initialization
- One-dimensional and multi-dimensional arrays
- Array indexing and bounds checking
- String representation as character arrays
- String library functions: strlen, strcpy, strcat, strcmp
- String input/output: gets, puts, scanf, printf
- Array of strings
""",
        "Pointers and Memory Management": """
Pointers and Memory Management:
- Pointer concept and declaration
- Address operator (&) and dereference operator (*)
- Pointer arithmetic
- Arrays and pointers relationship
- Dynamic memory allocation: malloc, calloc, realloc, free
- Pointer to pointer (double pointer)
- Function pointers
""",
        "Structures and Unions": """
Structures and Unions:
- Structure definition and declaration
- Accessing structure members
- Array of structures
- Nested structures
- Pointer to structures
- Union concept and usage
- Difference between structures and unions
- Enumeration (enum) data type
""",
        "File Operations": """
File Operations:
- File handling concept
- File opening modes: r, w, a, r+, w+, a+
- File operations: fopen, fclose, fread, fwrite
- Character I/O: fgetc, fputc
- String I/O: fgets, fputs
- Formatted I/O: fprintf, fscanf
- File positioning: fseek, ftell, rewind
""",
    },
    "Digital Logic": {
        "Number Systems": """
Number Systems:
- Binary number system (base 2)
- Decimal number system (base 10)
- Octal number system (base 8)
- Hexadecimal number system (base 16)
- Conversion between number systems
- Binary arithmetic: addition, subtraction, multiplication
- Signed number representation: sign-magnitude, 1's complement, 2's complement
- Binary codes: BCD, Gray code, ASCII
""",
        "Boolean Algebra": """
Boolean Algebra:
- Boolean variables and constants
- Basic Boolean operations: AND, OR, NOT
- Boolean algebra laws: commutative, associative, distributive
- De Morgan's theorems
- Boolean function representation
- Canonical forms: minterms and maxterms
- Sum of Products (SOP) and Product of Sums (POS)
- Boolean function simplification
""",
        "Logic Gates": """
Logic Gates:
- AND gate: symbol, truth table, operation
- OR gate: symbol, truth table, operation
- NOT gate: symbol, truth table, operation
- NAND gate: universal gate property
- NOR gate: universal gate property
- XOR gate: exclusive OR operation
- XNOR gate: exclusive NOR operation
- Gate-level circuit design
""",
        "Combinational Circuits": """
Combinational Circuits:
- Half adder: design and truth table
- Full adder: design and truth table
- Binary adder circuits
- Subtractor circuits
- Multiplexer (MUX): 2:1, 4:1, 8:1
- Demultiplexer (DEMUX)
- Encoder and decoder circuits
- Code converters
""",
        "Karnaugh Maps": """
Karnaugh Maps:
- K-map concept and construction
- 2-variable K-map
- 3-variable K-map
- 4-variable K-map
- Grouping rules in K-map
- Don't care conditions
- Prime implicants and essential prime implicants
- Minimization using K-map
""",
        "Sequential Circuits": """
Sequential Circuits:
- Difference between combinational and sequential circuits
- Clock signals and synchronization
- State concept in sequential circuits
- State tables and state diagrams
- Mealy and Moore machines
- Analysis of sequential circuits
- Design of sequential circuits
""",
        "Flip-Flops and Latches": """
Flip-Flops and Latches:
- SR latch: operation and truth table
- Gated SR latch
- D latch: operation and applications
- SR flip-flop: clocked operation
- D flip-flop: data storage element
- JK flip-flop: no invalid state
- T flip-flop: toggle operation
- Master-slave flip-flops
""",
        "Counters and Registers": """
Counters and Registers:
- Asynchronous counters (ripple counters)
- Synchronous counters
- Up counters and down counters
- Modulo-N counters
- Shift registers: SISO, SIPO, PISO, PIPO
- Ring counters
- Johnson counters
- Applications of counters and registers
""",
        "Memory Systems": """
Memory Systems:
- Memory organization and addressing
- ROM (Read-Only Memory): PROM, EPROM, EEPROM
- RAM (Random Access Memory): SRAM, DRAM
- Memory expansion techniques
- Memory interfacing
- Programmable logic devices: PLA, PAL, FPGA
- Memory hierarchy concept
""",
    },
    "Basic Electrical Engineering": {
        "Circuit Fundamentals": """
Circuit Fundamentals:
- Electric charge, current, and voltage
- Power and energy in electrical circuits
- Passive circuit elements: resistor, inductor, capacitor
- Active circuit elements: voltage source, current source
- Sign conventions for voltage and current
- Circuit diagrams and symbols
- Basic circuit terminology: node, branch, loop, mesh
""",
        "Ohm's Law and Kirchhoff's Laws": """
Ohm's Law and Kirchhoff's Laws:
- Ohm's law: V = I × R
- Resistance and conductance
- Kirchhoff's Current Law (KCL)
- Kirchhoff's Voltage Law (KVL)
- Series and parallel resistor combinations
- Voltage divider and current divider rules
- Applications and problem solving
""",
        "Network Theorems": """
Network Theorems:
- Thevenin's theorem: concept and applications
- Norton's theorem: concept and applications
- Thevenin-Norton equivalent transformations
- Superposition theorem
- Maximum power transfer theorem
- Millman's theorem
- Reciprocity theorem
- Substitution theorem
""",
        "AC Circuit Analysis": """
AC Circuit Analysis:
- AC waveforms: sine, cosine, square, triangular
- RMS and average values
- Phasor representation
- Impedance and admittance
- AC analysis of R, L, C circuits
- Power in AC circuits: real, reactive, apparent
- Power factor and power factor correction
- Resonance in AC circuits
""",
        "Three-Phase Systems": """
Three-Phase Systems:
- Generation of three-phase voltages
- Balanced three-phase systems
- Star (Y) connection
- Delta connection
- Line and phase voltages/currents
- Power in three-phase systems
- Advantages of three-phase systems
- Three-phase power measurement
""",
        "Magnetic Circuits": """
Magnetic Circuits:
- Magnetic field and flux
- Magnetic materials: ferromagnetic, paramagnetic, diamagnetic
- B-H curve and hysteresis
- Magnetic circuit analysis
- Ampere's law
- Reluctance and permeance
- Magnetic circuit with air gap
- Electromagnets and their applications
""",
        "Transformers": """
Transformers:
- Transformer principle of operation
- Ideal transformer theory
- Transformer construction
- EMF equation of transformer
- Transformer on no-load and on-load
- Equivalent circuit of transformer
- Transformer losses and efficiency
- Types of transformers and applications
""",
        "Electrical Machines": """
Electrical Machines:
- DC generators: principle and types
- EMF equation of DC generator
- DC motors: principle and types
- Torque equation of DC motor
- Three-phase induction motors
- Rotating magnetic field concept
- Slip and rotor frequency
- Torque-speed characteristics
""",
        "Measurement and Instrumentation": """
Measurement and Instrumentation:
- Measurement systems and standards
- Errors in measurements
- Moving coil instruments
- Moving iron instruments
- Dynamometer instruments
- Measurement of voltage, current, power
- Wattmeter connections
- Energy measurement
""",
    },
    "Engineering Mathematics I": {
        "Complex Numbers": """
Complex Numbers:
- Definition and representation of complex numbers
- Cartesian form (a + bi) and polar form (r∠θ)
- Arithmetic operations: addition, subtraction, multiplication, division
- Complex conjugate and modulus
- De Moivre's theorem
- Euler's formula: e^(iθ) = cos(θ) + i·sin(θ)
- Roots of complex numbers
- Applications in engineering
""",
        "Matrices and Determinants": """
Matrices and Determinants:
- Types of matrices: square, diagonal, identity, symmetric
- Matrix operations: addition, scalar multiplication, matrix multiplication
- Determinant calculation: 2×2 and 3×3 matrices
- Properties of determinants
- Cofactor expansion (Laplace expansion)
- Inverse of a matrix using adjoint method
- Cramer's rule for solving systems of equations
""",
        "System of Linear Equations": """
System of Linear Equations:
- Homogeneous and non-homogeneous systems
- Gaussian elimination method
- Gauss-Jordan elimination
- Row echelon form and reduced row echelon form
- Rank of a matrix
- Consistency and solution types
- Applications in engineering problems
""",
        "Sequences and Series": """
Sequences and Series:
- Arithmetic sequences and series
- Geometric sequences and series
- Convergence and divergence tests
- Taylor series and Maclaurin series
- Power series representation
- Binomial series
- Applications in approximation
""",
        "Limits and Continuity": """
Limits and Continuity:
- Concept of limit of a function
- Left-hand and right-hand limits
- Properties of limits
- Indeterminate forms and L'Hôpital's rule
- Continuity of a function at a point
- Types of discontinuity
- Intermediate Value Theorem
""",
        "Differentiation": """
Differentiation:
- Definition of derivative using limits
- Rules of differentiation: power rule, product rule, quotient rule, chain rule
- Derivatives of trigonometric functions
- Derivatives of exponential and logarithmic functions
- Implicit differentiation
- Higher-order derivatives
- Parametric differentiation
""",
        "Applications of Derivatives": """
Applications of Derivatives:
- Rate of change and related rates
- Increasing and decreasing functions
- Maxima and minima (local and absolute)
- Concavity and points of inflection
- Curve sketching using derivatives
- Mean Value Theorem
- Rolle's theorem
- Optimization problems in engineering
""",
        "Integration Techniques": """
Integration Techniques:
- Indefinite integrals and antiderivatives
- Integration by substitution
- Integration by parts
- Partial fraction decomposition
- Trigonometric integrals and substitutions
- Definite integrals and the Fundamental Theorem of Calculus
- Applications: area under curves, volume of revolution
- Numerical integration: trapezoidal rule, Simpson's rule
""",
    },
    "Engineering Physics": {
        "Mechanics and Motion": """
Mechanics and Motion:
- Newton's laws of motion
- Linear motion: displacement, velocity, acceleration
- Projectile motion
- Circular motion and centripetal force
- Rotational motion and moment of inertia
- Angular momentum and torque
- Conservation laws: momentum and energy
""",
        "Work, Energy and Power": """
Work, Energy and Power:
- Work done by a force
- Kinetic energy and work-energy theorem
- Potential energy: gravitational and elastic
- Conservation of mechanical energy
- Power and efficiency
- Collisions: elastic and inelastic
- Center of mass
""",
        "Oscillations and Waves": """
Oscillations and Waves:
- Simple harmonic motion (SHM)
- Damped and forced oscillations
- Resonance phenomenon
- Transverse and longitudinal waves
- Wave equation and wave speed
- Superposition principle
- Standing waves and harmonics
- Doppler effect
""",
        "Thermodynamics": """
Thermodynamics:
- Zeroth law and temperature measurement
- First law of thermodynamics
- Heat capacity and specific heat
- Thermodynamic processes: isothermal, adiabatic, isobaric, isochoric
- Second law of thermodynamics
- Entropy and its significance
- Carnot engine and efficiency
- Heat engines and refrigerators
""",
        "Optics and Light": """
Optics and Light:
- Nature of light: wave-particle duality
- Reflection and refraction laws
- Snell's law and total internal reflection
- Interference: Young's double slit experiment
- Diffraction: single slit and grating
- Polarization of light
- Optical instruments: microscope, telescope
""",
        "Modern Physics": """
Modern Physics:
- Photoelectric effect and Einstein's explanation
- Compton scattering
- De Broglie hypothesis
- Heisenberg uncertainty principle
- Blackbody radiation and Planck's hypothesis
- Special theory of relativity basics
- Mass-energy equivalence: E = mc²
""",
        "Atomic Structure": """
Atomic Structure:
- Bohr model of the atom
- Energy levels and electron transitions
- Hydrogen spectrum: Lyman, Balmer, Paschen series
- Quantum numbers: n, l, ml, ms
- Pauli exclusion principle
- Electronic configuration
- X-ray production and properties
""",
        "Quantum Mechanics Basics": """
Quantum Mechanics Basics:
- Wave function and its interpretation
- Schrödinger equation (time-independent)
- Particle in a box (infinite potential well)
- Quantum tunneling
- Expectation values
- Operators in quantum mechanics
- Applications in semiconductor physics
""",
    },
    "Engineering Drawing I": {
        "Drawing Instruments and Materials": """
Drawing Instruments and Materials:
- Drawing board, T-square, set squares
- Compass, divider, and protractor
- Drawing pencils: grades and uses (H, HB, B)
- Drawing paper: sizes (A0-A4) and types
- Scales: plain scale, diagonal scale
- Mini-drafter and its use
- Care and maintenance of instruments
""",
        "Lettering and Dimensioning": """
Lettering and Dimensioning:
- Single-stroke vertical lettering
- Single-stroke inclined lettering
- Letter proportions and spacing
- Types of lines in engineering drawing
- Dimensioning: aligned and unidirectional systems
- Rules of dimensioning
- Tolerances and fits notation
""",
        "Geometric Constructions": """
Geometric Constructions:
- Bisection of lines and angles
- Construction of regular polygons
- Construction of tangents to circles
- Ellipse construction: concentric circle method, oblong method
- Parabola and hyperbola construction
- Involute and cycloid curves
- Applications in engineering design
""",
        "Orthographic Projections": """
Orthographic Projections:
- First angle and third angle projection
- Projection of points
- Projection of lines: true length and inclination
- Projection of planes
- Projection of solids: prism, pyramid, cylinder, cone
- Missing view problems
- Reference planes: HP, VP, PP
""",
        "Isometric Drawings": """
Isometric Drawings:
- Isometric axes and angles (30°)
- Isometric scale
- Isometric drawing vs isometric projection
- Isometric view of simple solids
- Isometric view of combined solids
- Non-isometric lines handling
- Isometric circles (ellipse construction)
""",
        "Sectional Views": """
Sectional Views:
- Purpose and need for sectional views
- Cutting plane and its representation
- Full section and half section
- Offset section
- Revolved and removed sections
- Section lining (hatching) conventions
- Sectional views of standard objects
""",
        "Auxiliary Views": """
Auxiliary Views:
- Need for auxiliary views
- Primary auxiliary views
- Secondary auxiliary views
- Partial auxiliary views
- Auxiliary view of inclined surfaces
- True shape of oblique surfaces
- Applications in engineering
""",
        "Development of Surfaces": """
Development of Surfaces:
- Concept of surface development
- Development of prisms (right and oblique)
- Development of cylinders
- Development of pyramids
- Development of cones
- Truncated solids development
- Applications: sheet metal work, duct design
""",
    },
}


def seed():
    """Seed the database with syllabus content."""

    # Ensure schema exists
    logger.info("Initialising database schema...")
    init_db()

    total_chunks = 0

    for subject, chapters in SYLLABUS_CONTENT.items():
        for chapter, content in chapters.items():
            source_filename = f"seed_{subject}_{chapter}.txt".replace(" ", "_").lower()

            # Idempotency: skip if already seeded
            if document_repository.document_exists(source_filename):
                logger.info("⏭  Already seeded: %s / %s", subject, chapter)
                continue

            logger.info("📝 Seeding: %s / %s", subject, chapter)

            # Split content into chunks (simple split for syllabus bullet points)
            content_clean = content.strip()

            # Insert document record
            doc_id = document_repository.insert_document(
                subject=subject,
                chapter=chapter,
                source_filename=source_filename,
            )

            # Embed the content
            logger.info("   Embedding...")
            embeddings = embed_texts([content_clean])

            # Insert as a single chunk (syllabus entries are small enough)
            chunks = [{
                "document_id": doc_id,
                "subject": subject,
                "chapter": chapter,
                "content": content_clean,
                "embedding": embeddings[0],
                "page": None,
            }]

            inserted = document_repository.insert_chunks(chunks)
            total_chunks += inserted
            logger.info("Inserted %d chunk(s) (doc_id=%d)", inserted, doc_id)

    if total_chunks:
        logger.info("Seeding complete — %d total chunks inserted", total_chunks)
    else:
        logger.info("No new content to seed (all already present)")


if __name__ == "__main__":
    seed()
