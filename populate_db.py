import os
import uuid
import requests
import argparse
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from app import create_app
from app.models import db, Publication, Author, PublicationType
from app.routes.utils import ensure_upload_folder
from app.embeddings import process_pdf_for_publication

app = create_app()

REAL_PAPERS = [
    {
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Lukasz Kaiser", "Illia Polosukhin"],
        "pdf_url": "https://arxiv.org/pdf/1706.03762v7.pdf",
        "keywords": ["transformer", "attention", "nlp", "cs.CL", "real_paper"],
        "content": "Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train."
    },
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
        "pdf_url": "https://arxiv.org/pdf/1810.04805v2.pdf",
        "keywords": ["bert", "language representation", "nlp", "cs.CL", "real_paper"],
        "content": "Abstract: We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers. As a result, the pre-trained BERT model can be fine-tuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial task-specific architecture modifications."
    },
    {
        "title": "An Open Natural Language Processing Development Framework for EHR-based Clinical Research",
        "authors": ["Hongyi Yang", "Yanshan Wang"],
        "pdf_url": "https://arxiv.org/pdf/2110.10780v3.pdf",
        "keywords": ["nlp", "ehr", "clinical research", "n3c", "cs.CL", "real_paper"],
        "content": "Abstract: Electronic health records (EHRs) contain rich clinical narratives. Natural Language Processing (NLP) is a key technology to unlock clinical data for research. We present an open-source clinical NLP development framework designed for EHR-based clinical research. We demonstrate its utility using the National COVID Cohort Collaborative (N3C) data, showing how it supports collaborative development, validation, and deployment of clinical NLP pipelines."
    },
    {
        "title": "A Comprehensive Review of State-of-The-Art Methods for Java Code Generation from Natural Language Text",
        "authors": ["Siddharth S.", "Anand S."],
        "pdf_url": "https://arxiv.org/pdf/2306.06371v1.pdf",
        "keywords": ["java", "code generation", "nlp", "deep learning", "cs.SE", "real_paper"],
        "content": "Abstract: Code generation from natural language text has gained significant attention. In this paper, we present a comprehensive review of state-of-the-art methods for generating Java source code from natural language descriptions. We analyze various approaches, including rule-based techniques, retrieval-based methods, and deep learning architectures like Sequence-to-Sequence models and Large Language Models. We evaluate their performance and discuss challenges such as syntax validity and code semantic correctness."
    },
    {
        "title": "Towards the Study of Morphological Processing of the Tangkhul Language",
        "authors": ["Reimi A. S.", "S. R. Singh"],
        "pdf_url": "https://arxiv.org/pdf/2006.16212v1.pdf",
        "keywords": ["tangkhul", "morphology", "linguistics", "nlp", "cs.CL", "real_paper"],
        "content": "Abstract: Tangkhul is a Tibeto-Burman language spoken in Northeast India. In this paper, we initiate the study of morphological processing for the Tangkhul language. We discuss the morphological structure of verbs and nouns, highlighting prefixation and suffixation processes. We develop a rule-based morphotactic analyzer and evaluate its accuracy, representing the first computational work on this under-resourced language."
    },
    {
        "title": "An Automated Multiple-Choice Question Generation Using Natural Language Processing Techniques",
        "authors": ["Pooja B.", "G. S. S."],
        "pdf_url": "https://arxiv.org/pdf/2103.14757v1.pdf",
        "keywords": ["nlp", "mcq generation", "education technology", "cs.CL", "real_paper"],
        "content": "Abstract: Multiple-Choice Questions (MCQs) are widely used for student assessment. Manually creating MCQs is time-consuming. We propose an automated system for generating MCQs from text corpora using natural language processing techniques. Our system extracts key concepts, generates distractors using wordnet and word embeddings, and filters out low-quality questions. Evaluation results show that the generated questions are semantically valid and useful for educational testing."
    },
    {
        "title": "Changing Data Sources in the Age of Machine Learning for Official Statistics",
        "authors": ["Marco P.", "Fritz S."],
        "pdf_url": "https://arxiv.org/pdf/2306.04338v1.pdf",
        "keywords": ["machine learning", "official statistics", "data sources", "cs.LG", "real_paper"],
        "content": "Abstract: Official statistics agencies are transitioning from traditional survey methods to machine learning approaches. This paper explores the opportunities and challenges of utilizing new data sources, such as satellite imagery, mobile phone logs, and web scraping, for official statistics. We present case studies on inflation estimation and agricultural yield prediction using supervised machine learning algorithms, highlighting issues of data quality and representativeness."
    },
    {
        "title": "DOME: Recommendations for supervised machine learning validation in biology",
        "authors": ["J. N. A.", "David J."],
        "pdf_url": "https://arxiv.org/pdf/2006.16189v4.pdf",
        "keywords": ["machine learning", "validation", "biology", "dome", "cs.LG", "real_paper"],
        "content": "Abstract: Supervised machine learning is widely applied in biology, but model validation is often inconsistent. We present DOME (Data, Optimization, Model, Evaluation) recommendations, a set of guidelines for reporting and validating supervised machine learning studies in biological research. We discuss key aspects such as data division, hyperparameter tuning, leakage prevention, and robust performance metrics to ensure reproducibility."
    },
    {
        "title": "Learning Curves for Decision Making in Supervised Machine Learning: A Survey",
        "authors": ["Felix L.", "Jan N."],
        "pdf_url": "https://arxiv.org/pdf/2201.12150v2.pdf",
        "keywords": ["learning curves", "supervised learning", "decision making", "cs.LG", "real_paper"],
        "content": "Abstract: Learning curves plot model performance against training set size. This survey reviews the literature on learning curves in supervised machine learning. We discuss their application in decision making, such as determining whether collecting more data will improve performance, selecting models, and optimizing computational resource allocation. We analyze theoretical properties and empirical behaviors across different algorithms."
    },
    {
        "title": "On Hyperparameter Optimization of Machine Learning Algorithms: Theory and Practice",
        "authors": ["L. S.", "T. W."],
        "pdf_url": "https://arxiv.org/pdf/2007.15745v3.pdf",
        "keywords": ["hyperparameter", "optimization", "machine learning", "cs.LG", "real_paper"],
        "content": "Abstract: Hyperparameter optimization (HPO) is critical for maximizing the performance of machine learning algorithms. We present a comprehensive review of HPO methods, covering grid search, random search, Bayesian optimization, evolutionary algorithms, and gradient-based approaches. We analyze their theoretical convergence rates and compare their empirical performance on deep learning tasks."
    }
]

SYNTHETIC_PAPERS = [
    # --- Computer Vision ---
    {
        "title": "Deep Convolutional Networks for Accurate Image Classification",
        "authors": ["Yann LeCun", "Yoshua Bengio"],
        "keywords": ["computer vision", "image classification", "cnn", "deep learning", "cs.CV"],
        "content": "Abstract: Convolutional Neural Networks (CNNs) have established themselves as the dominant method for image classification. This paper presents an architecture that achieves state-of-the-art accuracy on ImageNet. We discuss convolutional layers, pooling, and fully connected layers. Computer vision systems rely on these networks to detect features and classify images automatically."
    },
    {
        "title": "Real-Time Object Detection in Videos using YoloV8",
        "authors": ["Joseph Redmon", "Alexey Bochkovskiy"],
        "keywords": ["computer vision", "object detection", "yolo", "video analysis", "cs.CV"],
        "content": "Abstract: Detecting objects in real-time is crucial for autonomous driving and video surveillance. We propose an updated YOLO model that improves both speed and precision. The network processes video frames at 60 FPS while maintaining high mean average precision (mAP). Object detection is a core computer vision task, and this architecture optimizes resource usage on edge devices."
    },
    {
        "title": "Generative Adversarial Networks for Image Synthesis",
        "authors": ["Ian Goodfellow", "Jean Pouget-Abadie"],
        "keywords": ["computer vision", "generative models", "gan", "image generation", "cs.CV"],
        "content": "Abstract: We introduce a framework for estimating generative models via an adversarial process. We train two models: a generative model that captures the data distribution, and a discriminative model that estimates the probability that a sample came from the training data. This is widely used in computer vision for image synthesis, super-resolution, and image-to-image translation."
    },
    {
        "title": "Vision Transformers for Large Scale Image Recognition",
        "authors": ["Alexey Dosovitskiy", "Lucas Beyer"],
        "keywords": ["computer vision", "transformer", "attention", "image recognition", "cs.CV"],
        "content": "Abstract: While the Transformer architecture has become the de facto standard for natural language processing tasks, its applications to computer vision remain limited. In this work, we show that applying a pure transformer directly to sequences of image patches works well for image classification. When pre-trained on large datasets, Vision Transformers (ViT) yield excellent results in computer vision benchmarks."
    },
    # --- NLP ---
    {
        "title": "Attention Is All You Need: The Transformer Architecture",
        "authors": ["Ashish Vaswani", "Noam Shazeer"],
        "keywords": ["nlp", "transformer", "attention", "language models", "cs.CL"],
        "content": "Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms. This model achieves superior quality in machine translation and various natural language processing (NLP) tasks, establishing a new standard for large-scale language models."
    },
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": ["Jacob Devlin", "Ming-Wei Chang"],
        "keywords": ["nlp", "bert", "language representation", "transformer", "cs.CL"],
        "content": "Abstract: We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train bidirectional representations from unlabeled text. As a result, it achieves state-of-the-art performance on a wide range of natural language processing tasks, including question answering and text classification."
    },
    {
        "title": "Language Models are Few-Shot Learners: GPT-3",
        "authors": ["Tom Brown", "Benjamin Mann"],
        "keywords": ["nlp", "gpt-3", "large language models", "few-shot learning", "cs.CL"],
        "content": "Abstract: We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance. We train GPT-3, an autoregressive language model with 175 billion parameters. We evaluate GPT-3 on a set of natural language processing benchmarks and show it achieves strong performance on translation, question-answering, and text completion without any fine-tuning."
    },
    {
        "title": "Evaluating Large Language Models on Text Summarization",
        "authors": ["Hugo Touvron", "Thibaut Lavril"],
        "keywords": ["nlp", "text summarization", "large language models", "evaluation", "cs.CL"],
        "content": "Abstract: Text summarization is a key challenge in natural language processing (NLP). We evaluate several large open-source language models on their ability to generate concise, coherent, and factual summaries of news articles. We discuss evaluation metrics and the challenges of alignment in modern LLMs for NLP workloads."
    },
    # --- Optimization / Machine Learning ---
    {
        "title": "Stochastic Gradient Descent with Adaptive Learning Rates",
        "authors": ["Diederik Kingma", "Jimmy Ba"],
        "keywords": ["optimization", "gradient descent", "adam", "machine learning", "cs.LG", "stat.ML"],
        "content": "Abstract: We introduce Adam, an algorithm for first-order gradient-based optimization of stochastic objective functions, based on adaptive estimates of lower-order moments. It is highly suited for machine learning optimization, requiring little tuning and scaling well to large datasets. We compare it to traditional stochastic gradient descent (SGD) and show superior convergence."
    },
    {
        "title": "A Method for Stochastic Optimization in Deep Networks",
        "authors": ["John Duchi", "Elad Hazan"],
        "keywords": ["optimization", "stochastic gradient", "adagrad", "machine learning", "cs.LG", "stat.ML"],
        "content": "Abstract: We present a family of subgradient methods for stochastic optimization, Adagrad, that dynamically adapt the learning rate to the geometry of the data. This approach is highly effective for training neural networks and sparse machine learning problems. It improves the convergence rate of stochastic gradient descent on complex, non-convex loss surfaces."
    },
    {
        "title": "Understanding the Convergence of Gradient Descent in Deep Learning",
        "authors": ["Sanjeev Arora", "Noah Golowich"],
        "keywords": ["optimization", "convergence", "gradient descent", "deep learning theory", "cs.LG"],
        "content": "Abstract: Gradient descent is the workhorse of deep learning, but its theoretical convergence properties in non-convex regimes remain poorly understood. This paper analyzes the optimization dynamics of gradient descent for overparameterized neural networks. We prove that under reasonable assumptions, SGD converges to a global minimum with a high probability."
    },
    {
        "title": "Convex Optimization and its Applications in Machine Learning",
        "authors": ["Stephen Boyd", "Lieven Vandenberghe"],
        "keywords": ["optimization", "convex optimization", "machine learning", "algorithms", "cs.LG", "stat.ML"],
        "content": "Abstract: Convex optimization problems arise frequently in machine learning, signal processing, and control theory. This paper surveys classical convex optimization algorithms, including interior point methods, proximal gradient methods, and coordinate descent. We demonstrate how machine learning formulations like Support Vector Machines (SVMs) and Lasso are solved efficiently via convex optimization."
    },
    # --- Medicine ---
    {
        "title": "Immunotherapy Advancements in Cancer Treatment",
        "authors": ["James Allison", "Tasuku Honjo"],
        "keywords": ["cancer", "immunotherapy", "oncology", "medicine"],
        "content": "Abstract: Immunotherapy has revolutionized oncology by using the body's immune system to target cancer cells. This study evaluates immune checkpoint inhibitors in lung cancer and melanoma patient cohorts. We analyze T-cell activation and side effects compared to chemotherapy."
    },
    {
        "title": "Gene Expression Profiling in Cardiovascular Diseases",
        "authors": ["Eric Topol", "Francis Collins"],
        "keywords": ["cardiovascular", "gene expression", "heart", "medicine"],
        "content": "Abstract: Coronary artery disease remains a leading cause of mortality. We perform RNA sequencing on cardiac tissue samples to identify gene expression profiles associated with atherosclerosis. Key pathways in inflammation and lipid metabolism are identified."
    },
    {
        "title": "Efficacy of mRNA Vaccines in Modern Pharmacology",
        "authors": ["Katalin Kariko", "Drew Weissman"],
        "keywords": ["vaccine", "mrna", "pharmacology", "medicine"],
        "content": "Abstract: mRNA technology represents a paradigm shift in vaccine development and pharmacology. This paper explains the lipid nanoparticle delivery mechanism and immune responses triggered by mRNA encoding viral spike proteins. Safety profiles and efficacy data are reviewed."
    },
    {
        "title": "Neurological Impact of Alzheimer's Disease on Cognitive Function",
        "authors": ["Stanley Prusiner", "Alois Alzheimer"],
        "keywords": ["alzheimer", "brain", "neurology", "medicine"],
        "content": "Abstract: Alzheimer's disease is characterized by amyloid-beta plaques and neurofibrillary tangles. We examine the correlation between plaque density in the hippocampus and cognitive decline in clinical trials. Therapeutic approaches targeting tau proteins are discussed."
    },
    {
        "title": "CRISPR-Cas9 Therapeutics for Genetic Disorders",
        "authors": ["Jennifer Doudna", "Emmanuelle Charpentier"],
        "keywords": ["gene editing", "crispr", "disease", "medicine"],
        "content": "Abstract: The CRISPR-Cas9 system has enabled precise genome editing. This article outlines current clinical trials using CRISPR for sickle cell anemia and beta-thalassemia. We analyze off-target mutation rates and progress in delivering CAS9 proteins into human cells."
    },
    {
        "title": "Microbiome Diversity and its Impact on Human Gut Health",
        "authors": ["Jeffrey Gordon", "Rob Knight"],
        "keywords": ["microbiome", "gut", "health", "medicine"],
        "content": "Abstract: The human gut microbiome plays a vital role in digestion, immunity, and metabolic homeostasis. Using 16S rRNA sequencing, we show that high bacterial diversity is correlated with lower incidences of inflammatory bowel disease and obesity."
    },
    {
        "title": "Artificial Intelligence Applications in Clinical Radiology",
        "authors": ["Curtis Langlotz", "Keith Dreyer"],
        "keywords": ["radiology", "imaging", "clinical", "medicine", "ai"],
        "content": "Abstract: Deep learning models have shown high sensitivity in detecting abnormalities in chest X-rays and brain CT scans. We discuss the clinical integration of AI tools as a second-read assistant for radiologists, examining performance and validation protocols."
    },
    {
        "title": "Pharmacokinetics of Novel Antiviral Drugs",
        "authors": ["Anthony Fauci", "David Ho"],
        "keywords": ["antiviral", "pharmacology", "drug", "medicine"],
        "content": "Abstract: Developing effective antiviral drugs requires understanding their absorption, distribution, metabolism, and excretion. We present pharmacokinetic parameters of a novel small-molecule inhibitor targeting viral replication enzymes in animal models."
    },
    # --- Biology / Ecology ---
    {
        "title": "Photosynthesis Efficiency under Elevated Carbon Dioxide Levels",
        "authors": ["Melvin Calvin", "Robert Hill"],
        "keywords": ["photosynthesis", "carbon dioxide", "plants", "biology", "ecology"],
        "content": "Abstract: Climate change is increasing atmospheric CO2. We measure the photosynthetic rate and stomatal conductance of C3 and C4 crop species in controlled environments. Results indicate that C3 plants show initial biomass increases but suffer from nutrient limitations."
    },
    {
        "title": "Marine Ecosystem Biodiversity in Coral Reefs",
        "authors": ["Jane Lubchenco", "Sylvia Earle"],
        "keywords": ["marine", "coral reefs", "biodiversity", "biology", "ecology"],
        "content": "Abstract: Coral reefs support massive marine biodiversity but face severe threats from ocean acidification and warming. We survey fish species richness and coral cover across the Indo-Pacific. Conservation policies must prioritize marine protected areas."
    },
    {
        "title": "Evolutionary Adaptations of Arctic Fauna to Climate Change",
        "authors": ["Charles Darwin", "Alfred Wallace"],
        "keywords": ["arctic", "climate change", "fauna", "biology", "ecology"],
        "content": "Abstract: Arctic animals are experiencing rapid habitat loss due to melting sea ice. We document behavioral changes and population genetics of polar bears and ringed seals, demonstrating rapid selective pressures acting on foraging strategies."
    },
    {
        "title": "Mitosis Regulation and Cell Cycle Checkpoints",
        "authors": ["Paul Nurse", "Leland Hartwell"],
        "keywords": ["mitosis", "cell cycle", "checkpoints", "biology"],
        "content": "Abstract: Cell division is strictly regulated by cyclin-dependent kinases (CDKs) and checkpoints. We detail the spindle assembly checkpoint (SAC) which prevents chromosome segregation errors during mitosis, highlighting its relevance in cancer biology."
    },
    {
        "title": "Nitrogen Fixation in Legume-Rhizobium Symbiosis",
        "authors": ["Martinus Beijerinck", "Hermann Hellriegel"],
        "keywords": ["nitrogen", "soil", "plants", "symbiosis", "biology"],
        "content": "Abstract: Legumes form symbiotic relationships with Rhizobium bacteria to convert atmospheric nitrogen into bioavailable ammonia. We identify host plant signals that trigger bacterial nodulation genes, which could reduce reliance on synthetic fertilizers."
    },
    {
        "title": "Genomic Sequencing of Extremophile Bacteria in Hydrothermal Vents",
        "authors": ["Craig Venter", "Carl Woese"],
        "keywords": ["bacteria", "genome", "extremophile", "biology"],
        "content": "Abstract: Deep-sea hydrothermal vents present extreme temperatures and pressures. We isolate a novel thermophilic bacterium and sequence its genome, discovering unique heat-shock proteins and enzymes that remain stable above 100 degrees Celsius."
    },
    {
        "title": "Impact of Microplastics on Freshwater Aquatic Organisms",
        "authors": ["Rachel Carson", "Richard Thompson"],
        "keywords": ["microplastics", "pollution", "freshwater", "biology", "ecology"],
        "content": "Abstract: Microplastics pollute freshwater systems worldwide. We expose Daphnia magna to varying concentrations of polyethylene microparticles. Observed impacts include reduced reproductive output, physical blockage of digestive tracts, and oxidative stress."
    },
    {
        "title": "Foraging Behaviors of Migratory Birds in North America",
        "authors": ["John Audubon", "Roger Tory Peterson"],
        "keywords": ["birds", "migration", "foraging", "biology", "ecology"],
        "content": "Abstract: Migratory birds depend on stopover sites to refuel. We track the stopover duration and foraging efficiency of warbler species during spring migration, highlighting the ecological importance of preserving hardwood forests along migration routes."
    },
    # --- Physics ---
    {
        "title": "Superconductivity in High-Temperature Materials",
        "authors": ["John Bardeen", "Leon Cooper"],
        "keywords": ["superconductivity", "materials", "condensed matter", "physics"],
        "content": "Abstract: Finding room-temperature superconductors is a major goal of condensed matter physics. We report superconductivity in hydrides under extreme pressures of 150 GPa. The transition temperature (Tc) reaches 250 Kelvin, supporting theoretical predictions."
    },
    {
        "title": "Quantum Computing using Trapped Ion Qubits",
        "authors": ["Richard Feynman", "David Wineland"],
        "keywords": ["quantum", "qubits", "trapped ion", "physics", "computing"],
        "content": "Abstract: Trapped ions offer long coherence times and high-fidelity gates for quantum computing. We demonstrate entangling gates between Calcium-40 ions in a micro-fabricated trap. Noise sources and scaling limitations are analyzed."
    },
    {
        "title": "Gravitational Wave Detection and Black Hole Mergers",
        "authors": ["Kip Thorne", "Rainer Weiss"],
        "keywords": ["gravitational waves", "black hole", "relativity", "physics", "astronomy"],
        "content": "Abstract: The Laser Interferometer Gravitational-Wave Observatory (LIGO) has detected transient gravitational waves. The observed signals match templates of binary black hole inspirals and mergers predicted by Einstein's General Theory of Relativity."
    },
    {
        "title": "Cosmic Microwave Background Radiation and Early Universe Evolution",
        "authors": ["Arno Penzias", "Robert Wilson"],
        "keywords": ["cosmology", "universe", "cmb", "physics", "astronomy"],
        "content": "Abstract: The Cosmic Microwave Background (CMB) radiation provides a snapshot of the early universe 380,000 years after the Big Bang. We present precision temperature anisotropy measurements, constraining cosmological parameters and inflation models."
    },
    {
        "title": "Quantum Entanglement and Information Theory Applications",
        "authors": ["Albert Einstein", "John Bell"],
        "keywords": ["entanglement", "quantum", "bell inequality", "physics"],
        "content": "Abstract: Quantum entanglement challenges classical notions of local realism. We perform a loophole-free test of Bell's inequalities, verifying non-local correlations. Applications for quantum cryptography and teleportation protocols are explored."
    },
    {
        "title": "Thermodynamic Limits of Nanoscale Thermoelectric Generators",
        "authors": ["Nicolas Carnot", "Thomas Seebeck"],
        "keywords": ["thermodynamics", "nanotechnology", "thermoelectric", "physics"],
        "content": "Abstract: Thermoelectric devices convert waste heat into electrical energy. We model the efficiency of quantum dot generators, determining the thermodynamic limits of power output. Nanostructuring is shown to improve the Seebeck coefficient."
    },
    {
        "title": "Search for Dark Matter Candidates at the Large Hadron Collider",
        "authors": ["Fabiola Gianotti", "Peter Higgs"],
        "keywords": ["dark matter", "lhc", "higgs", "physics", "particle"],
        "content": "Abstract: Dark matter constitutes most of the universe's mass, but its particle nature remains unknown. We present search results for Weakly Interacting Massive Particles (WIMPs) in proton-proton collisions at 13 TeV at the Large Hadron Collider."
    },
    {
        "title": "Laser Spectroscopy of Highly Charged Ions",
        "authors": ["Arthur Schawlow", "Theodor Hänsch"],
        "keywords": ["laser", "spectroscopy", "ions", "physics"],
        "content": "Abstract: Highly charged ions are sensitive probes of quantum electrodynamics (QED) and nuclear size effects. We perform high-precision laser spectroscopy on Hydrogen-like Lead ions, comparing experimental transition energies to QED calculations."
    },
    # --- Mathematics ---
    {
        "title": "Prime Number Distribution and the Riemann Hypothesis",
        "authors": ["Bernhard Riemann", "Leonhard Euler"],
        "keywords": ["prime numbers", "riemann", "number theory", "mathematics"],
        "content": "Abstract: The distribution of prime numbers is closely tied to the non-trivial zeros of the Riemann zeta function. We present new analytical bounds on the prime counting function, assuming the validity of the Riemann Hypothesis."
    },
    {
        "title": "Elliptic Curve Cryptography for Secure Communication",
        "authors": ["Neal Koblitz", "Victor Miller"],
        "keywords": ["cryptography", "elliptic curves", "security", "mathematics"],
        "content": "Abstract: Elliptic Curve Cryptography (ECC) offers equivalent security to RSA but with significantly smaller key sizes. We describe efficient algorithms for point multiplication on elliptic curves over finite fields, evaluating resistance to side-channel attacks."
    },
    {
        "title": "Topological Data Analysis for Complex Datasets",
        "authors": ["Gunnar Carlsson", "Herbert Edelsbrunner"],
        "keywords": ["topology", "data analysis", "persistent homology", "mathematics"],
        "content": "Abstract: Topological Data Analysis (TDA) extracts shape features from high-dimensional datasets. We use persistent homology to study the structural patterns of biological neural networks, demonstrating that TDA reveals properties missed by clustering."
    },
    {
        "title": "Nash Equilibrium and Strategy in Evolutionary Game Theory",
        "authors": ["John Nash", "John Maynard Smith"],
        "keywords": ["game theory", "nash equilibrium", "strategy", "mathematics"],
        "content": "Abstract: Evolutionary game theory models strategic interactions between agents. We analyze the stability of Nash equilibria in multi-agent populations, defining evolutionary stable strategies (ESS) and showing applications in ecology and economics."
    },
    {
        "title": "Probabilistic Methods in Combinatorics and Graph Theory",
        "authors": ["Paul Erdős", "Alfréd Rényi"],
        "keywords": ["combinatorics", "graphs", "probability", "mathematics"],
        "content": "Abstract: The probabilistic method is a powerful tool in combinatorics. We construct random graphs and prove the existence of graphs with high girth and high chromatic number, demonstrating how probability bounds deterministic properties."
    },
    {
        "title": "Numerical Methods for Solving Partial Differential Equations",
        "authors": ["John von Neumann", "Richard Courant"],
        "keywords": ["pde", "numerical analysis", "finite element", "mathematics"],
        "content": "Abstract: Solving partial differential equations (PDEs) analytically is often impossible. We evaluate finite element methods and finite difference schemes for solving the Navier-Stokes equations, analyzing convergence rates and numerical stability."
    },
    {
        "title": "Chaos Theory and Non-Linear Dynamic Systems",
        "authors": ["Edward Lorenz", "Henri Poincaré"],
        "keywords": ["chaos", "dynamic systems", "attractors", "mathematics"],
        "content": "Abstract: Non-linear dynamic systems can exhibit sensitive dependence on initial conditions, commonly known as chaos. We simulate the Lorenz attractor and calculate Lyapunov exponents to quantify chaotic behavior in atmospheric models."
    },
    {
        "title": "Linear Algebra Techniques in High-Dimensional Optimization",
        "authors": ["Gene Golub", "Gilbert Strang"],
        "keywords": ["optimization", "linear algebra", "matrices", "mathematics"],
        "content": "Abstract: High-dimensional optimization problems require fast matrix computations. We review Singular Value Decomposition (SVD) and conjugate gradient methods, showing how linear algebra abstractions speed up machine learning training loops."
    },
    # --- Chemistry ---
    {
        "title": "Catalytic Hydrogenation using Transition Metal Complexes",
        "authors": ["Ryoji Noyori", "William Knowles"],
        "keywords": ["catalysis", "transition metals", "hydrogenation", "chemistry"],
        "content": "Abstract: Transition metal complexes act as highly efficient catalysts for asymmetric hydrogenation. We synthesize novel Ruthenium complexes and evaluate their catalytic activity in reducing ketones, achieving high enantiomeric excess."
    },
    {
        "title": "Synthesis of Biodegradable Polymers for Eco-Friendly Packaging",
        "authors": ["Robert Langer", "Wallace Carothers"],
        "keywords": ["polymer", "biodegradable", "green chemistry", "chemistry"],
        "content": "Abstract: Synthetic plastics cause severe environmental damage. We synthesize polylactic acid (PLA) copolymers with improved tensile strength and faster biodegradation profiles, proposing them as viable replacements for polystyrene packaging."
    },
    {
        "title": "Nanoparticle Synthesis for Targeted Drug Delivery",
        "authors": ["Paul Alivisatos", "Michael Grätzel"],
        "keywords": ["nanoparticle", "drug delivery", "chemistry"],
        "content": "Abstract: Functionalized gold nanoparticles can carry therapeutic payloads directly to cancer cells. We describe a chemical synthesis method using PEGylation to improve biocompatibility and test drug release profiles under acidic tumor conditions."
    },
    {
        "title": "Spectroscopic Analysis of Organic Compounds",
        "authors": ["Robert Woodward", "Richard Ernst"],
        "keywords": ["spectroscopy", "nmr", "organic chemistry", "chemistry"],
        "content": "Abstract: Nuclear Magnetic Resonance (NMR) spectroscopy is indispensable for structural elucidation. We analyze NMR spectra of complex natural products, detailing how coupling constants and multi-dimensional NMR experiments confirm stereochemistry."
    },
    {
        "title": "Electrochemical Properties of Graphene-Based Anodes in Lithium Batteries",
        "authors": ["Akira Yoshino", "John Goodenough"],
        "keywords": ["battery", "graphene", "electrochemistry", "chemistry"],
        "content": "Abstract: Modern batteries require higher energy densities. We synthesize nitrogen-doped graphene sheets and test them as anodes in lithium-ion batteries. Results show improved rate capability and cyclic stability over graphite anodes."
    },
    {
        "title": "Covalent Organic Frameworks for Carbon Capture",
        "authors": ["Omar Yaghi", "Richard Smalley"],
        "keywords": ["carbon capture", "covalent frameworks", "materials", "chemistry"],
        "content": "Abstract: Porous crystalline materials can selectively adsorb carbon dioxide. We construct a novel covalent organic framework (COF) with high thermal stability and evaluate its carbon capture capacity under flue gas conditions."
    },
    # --- Astronomy / Space ---
    {
        "title": "Atmospheric Composition Analysis of Hot Jupiter Exoplanets",
        "authors": ["Michel Mayor", "Didier Queloz"],
        "keywords": ["exoplanet", "hot jupiter", "atmosphere", "astronomy"],
        "content": "Abstract: Hot Jupiters are gas giants orbiting very close to their host stars. We use transmission spectroscopy from space telescopes to detect water vapor, carbon monoxide, and cloud decks in the exoplanet atmospheres, modeling thermal structures."
    },
    {
        "title": "Spectral Classification of Stellar Populations in Andromeda",
        "authors": ["Edwin Hubble", "Henrietta Leavitt"],
        "keywords": ["stellar", "galaxies", "andromeda", "astronomy"],
        "content": "Abstract: Classifying stars helps trace galactic history. We analyze optical spectra of thousands of stars in the Andromeda galaxy, determining metallicities and ages to map stellar populations and reconstruct early merger events."
    },
    {
        "title": "Interstellar Dust Characterization in Star-Forming Regions",
        "authors": ["Carl Sagan", "Subrahmanyan Chandrasekhar"],
        "keywords": ["interstellar", "stars", "nebula", "astronomy"],
        "content": "Abstract: Interstellar dust grains obscure optical light but emit in the infrared. We model dust extinction curves in the Orion Nebula, showing that grain size distributions vary significantly between dense cores and diffuse outer regions."
    },
    {
        "title": "Asteroid Deflection Strategies using Kinetic Impactors",
        "authors": ["Neil deGrasse Tyson", "Carl Sagan"],
        "keywords": ["asteroid", "deflection", "impactors", "astronomy", "space"],
        "content": "Abstract: Mitigating asteroid impact hazards is a key focus of planetary defense. We simulate the orbital deflection of a 100-meter asteroid using a kinetic impactor spacecraft, demonstrating that early detection is critical for successful deflection."
    },
    {
        "title": "Active Galactic Nuclei and Supermassive Black Holes",
        "authors": ["Donald Lynden-Bell", "Andrea Ghez"],
        "keywords": ["black hole", "galaxies", "agn", "astronomy"],
        "content": "Abstract: Active Galactic Nuclei (AGN) are powered by accretion onto supermassive black holes. We analyze X-ray and radio emissions from nearby AGNs, modeling jet launch mechanisms and feedback processes that regulate star formation in host galaxies."
    }
]

def download_pdf(url, output_path):
    print(f"Descargando PDF real desde {url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    retries = 3
    backoff = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=25)
            if response.status_code == 429:
                print(f"HTTP 429 al descargar PDF. Reintentando en {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
        except Exception as e:
            print(f"Error descargando PDF (intento {attempt+1}): {e}")
            time.sleep(backoff)
            backoff *= 2
    return False

def generate_pdf_fallback(title, authors, content, output_path):
    """Genera un archivo PDF local usando PyMuPDF si falla la descarga."""
    import fitz
    try:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), f"Title: {title}", fontsize=14)
        page.insert_text((50, 80), f"Authors: {', '.join(authors)}", fontsize=10)
        page.insert_text((50, 110), content, fontsize=9)
        doc.save(output_path)
        doc.close()
        return True
    except Exception as e:
        print(f"Error en fallback PDF para '{title}': {e}")
        return False

def generate_synthetic_pdfs(clear_db=True):
    """Genera papers sintéticos usando PyMuPDF localmente para evitar rate-limits."""
    import fitz # PyMuPDF
    
    with app.app_context():
        # Limpieza opcional para tener el benchmark limpio
        if clear_db:
            print("\n[INFO] Limpiando base de datos antes de poblar...")
            from app.models import DocumentChunk
            try:
                db.session.query(DocumentChunk).delete()
                db.session.execute(db.text("DELETE FROM author_publication"))
                Publication.query.delete()
                Author.query.delete()
                db.session.commit()
                print("Base de datos limpia.")
            except Exception as e:
                db.session.rollback()
                print(f"Error limpiando base de datos: {e}")

        pub_type = PublicationType.query.filter_by(type_name="Paper").first()
        if not pub_type:
            pub_type = PublicationType(type_name="Paper")
            db.session.add(pub_type)
            db.session.commit()

        upload_folder = ensure_upload_folder()

        # 1. Cargar papers reales (descargando PDFs o usando fallback local con abstract)
        print(f"\n[INFO] Procesando {len(REAL_PAPERS)} papers reales (descarga + fallback)...")
        for idx, paper in enumerate(REAL_PAPERS):
            existing = Publication.query.filter_by(title=paper['title']).first()
            if existing:
                continue
                
            print(f"\n--- Procesando Real [{idx+1}/{len(REAL_PAPERS)}]: {paper['title']} ---")
            
            # Crear autores
            author_objs = []
            for author_name in paper['authors']:
                names = author_name.split()
                first_name = names[0] if names else "Autor"
                last_name = " ".join(names[1:]) if len(names) > 1 else "Desconocido"
                
                a = Author.query.filter_by(first_name=first_name, last_name=last_name).first()
                if not a:
                    a = Author(first_name=first_name, last_name=last_name)
                    db.session.add(a)
                    db.session.commit()
                author_objs.append(a)

            unique_filename = f"{uuid.uuid4()}_real_paper.pdf"
            pdf_path = os.path.join(upload_folder, unique_filename)

            # Intentar descargar PDF real
            download_success = download_pdf(paper['pdf_url'], pdf_path)
            
            if not download_success:
                print("Descarga fallida. Generando PDF de contingencia local con el abstract real...")
                generate_pdf_fallback(paper['title'], paper['authors'], paper['content'], pdf_path)
                
            # Guardar Publicación
            pub = Publication(
                title=paper['title'],
                type_id=pub_type.type_id,
                publish_date=datetime.now(timezone.utc),
                resource_url=unique_filename,
                keywords=paper['keywords']
            )
            for a in author_objs:
                pub.authors.append(a)
            db.session.add(pub)
            db.session.commit()
            
            # Generar embeddings (ya sea del PDF descargado o del de contingencia)
            print("Generando embeddings...")
            try:
                chunks_count = process_pdf_for_publication(pub.publication_id, pdf_path)
                print(f"Éxito! Indexado con {chunks_count} chunks.")
            except Exception as e:
                db.session.rollback()
                print(f"Error generando embeddings: {e}")
                
            # Dormir 2 segundos entre descargas para no levantar sospechas de ArXiv
            if download_success:
                time.sleep(2.5)

        # 2. Cargar papers sintéticos de diversidad
        print(f"\n[INFO] Generando {len(SYNTHETIC_PAPERS)} papers sintéticos locales...")
        for paper in SYNTHETIC_PAPERS:
            existing = Publication.query.filter_by(title=paper['title']).first()
            if existing:
                continue
                
            # Crear autores
            author_objs = []
            for author_name in paper['authors']:
                names = author_name.split()
                first_name = names[0] if names else "Autor"
                last_name = " ".join(names[1:]) if len(names) > 1 else "Desconocido"
                
                a = Author.query.filter_by(first_name=first_name, last_name=last_name).first()
                if not a:
                    a = Author(first_name=first_name, last_name=last_name)
                    db.session.add(a)
                    db.session.commit()
                author_objs.append(a)

            # Generar PDF sintético
            unique_filename = f"{uuid.uuid4()}_synthetic_paper.pdf"
            pdf_path = os.path.join(upload_folder, unique_filename)
            
            generate_pdf_fallback(paper['title'], paper['authors'], paper['content'], pdf_path)
            
            # Guardar
            pub = Publication(
                title=paper['title'],
                type_id=pub_type.type_id,
                publish_date=datetime.now(timezone.utc),
                resource_url=unique_filename,
                keywords=paper['keywords']
            )
            for a in author_objs:
                pub.authors.append(a)
            db.session.add(pub)
            db.session.commit()
            
            # Generar embeddings
            try:
                process_pdf_for_publication(pub.publication_id, pdf_path)
            except Exception as e:
                db.session.rollback()
                print(f"Error generando embeddings: {e}")
        
        print(f"[INFO] Finalizada la población completa. Total: {len(REAL_PAPERS)} reales, {len(SYNTHETIC_PAPERS)} sintéticos.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poblar BD con papers sintéticos y reales")
    parser.add_argument("--synthetic", action="store_true", default=True, help="Generar datos sintéticos y reales locales")
    parser.add_argument("--no-clear", action="store_true", help="Evitar limpiar la BD antes de poblar")
    
    args = parser.parse_args()
    generate_synthetic_pdfs(clear_db=not args.no_clear)
