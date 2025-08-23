[[biofoundry]]

### An Integrated AI and Robotics Research Platform to Advance Protein Engineering

This time, I'm reviewing a paper that showcases how AI and a Biofoundry were used to boost efficiency in protein engineering. Unlike the biofoundry process paper I posted about before, this one delves into a real-world case in life science research, so it might be a bit challenging for those not in the field. To help with that, I'll try to break things down as simply as possible and define any difficult terms. It's also perfectly fine to focus on the overall flow rather than getting caught up in every detail. Understanding the gist of this post will give you a deeper appreciation for why AI and biofoundries are set to play such a crucial role in the future of biotechnology.

## Protein Engineering

In the field of biotechnology, protein engineering is a core technology that not only helps us understand biological phenomena but also drives innovation across diverse industries like medicine, chemistry, manufacturing, energy, and agriculture. When we hear the word "protein," we might think of the nutritional category alongside carbohydrates and fats. But in reality, proteins perform countless essential functions within living organisms, acting as enzymes to catalyze chemical reactions, as antibodies in immune responses, or as structural proteins that form biological tissues. However, the process of improving or optimizing the functions of these vital proteins in a desired direction has traditionally been fraught with difficulties.

### 1. The Traditional Limits of Protein Engineering: Slow and Inefficient

One of the main strategies for improving protein function, `directed evolution`, has been recognized as an effective method.

---

**What is directed evolution?** Directed evolution is a technique where scientists artificially manipulate the evolutionary process of an organism to achieve a specific goal. This technique is used to rapidly develop organisms with specific traits through methods like gene editing or induced mutation. Unlike natural evolution (variation, selection), which occurs randomly over thousands of years, directed evolution is designed to achieve desired outcomes in a short period. It proceeds in two main ways:

- **Mutagenesis:** Researchers use chemicals or radiation to introduce random changes (mutations) into an organism's genes. This creates a diverse pool of individuals with various traits.
    
- **Selection:** From the newly created individuals, researchers select only those that possess the desired characteristic (e.g., an enzyme that is resistant to a specific drug). They then multiply these selected individuals to create the next generation.
    
- **Amplification:** The variants that are selected and screened through the above process are amplified using techniques like PCR. This step is performed to prepare for the next round of mutagenesis.
    

By repeating this process multiple times, an organism with an increasingly enhanced desired trait can be obtained!

---

However, this method has several inherent limitations.

First, it is **excessively time-consuming and labor-intensive**. The process of randomly modifying a protein's amino acid sequence and then screening for variants with the desired function is as inefficient as searching for a needle in a vast haystack. Because it's based on inherently random, trial-and-error `iterative cycles`, it's bound to be inefficient when exploring a vast space of possibilities. (Just thinking about it is exhausting).

Second, there is a risk of getting trapped in a `local optima`. Traditional methods typically proceed by introducing one amino acid variation at a time. While this approach can find improved proteins in the short term, it often settles for a sub-optimal solution, failing to discover the globally best protein.

A `local optima` refers to a point that is better than its immediate surroundings but is not the absolute best point (the global optimum) in the entire search space.

Third, there's the **difficulty of predicting mutation sites**. Due to the complex structure and functional interdependencies of proteins, accurately predicting the effect of a specific amino acid change on protein function is extremely difficult. Consequently, researchers have had to rely on the brute-force method of introducing mutations and then experimenting. (Again, exhausting to even imagine). These slow and labor-intensive characteristics directly hinder the pace of innovation in industries where proteins are essential.

### 2. The Advent of PLMeAE: The Synergy of AI and Robotics

The `PLMeAE` (Protein Language Model-enabled Automatic Evolution) platform was developed to overcome these traditional limitations of protein engineering. PLMeAE can be likened to an "intelligent robot scientist" for protein engineering.

The core goal of PLMeAE is to make the protein evolution process faster and more accurate. The system integrates two key technologies: an AI-based "brain" called the `Protein Language Model (PLM)` and a robotics-based "laboratory" called the `Automated Biofoundry`. The true innovation of PLMeAE isn't just the individual advancements in AI or robotics, but the fact that these two are integrated into a `closed-loop system`, creating a complementary synergy. The PLM handles intelligent protein design, while the automated biofoundry executes rapid experiments and generates data, creating a continuous virtuous cycle between the two.

PLMeAE operates as a `closed-loop system`: the PLM designs proteins, the biofoundry robots build and test those designs, and the experimental results are fed back to the PLM to learn from, making the next design cycle more refined. This is akin to a robot that learns, experiments, and learns again, all on its own. Such a platform signifies a fundamental shift in scientific research methodology, moving away from human-centric manual experiments toward autonomous, AI-driven discovery. This can be seen as the beginning of the "self-driving laboratory," a new paradigm that reduces the time scientists spend on manual lab work and allows them to focus on more creative and critical research.

### 3. How PLMeAE Works: The DBTL Cycle

PLMeAE evolves proteins by repeating a special cycle called `Design-Build-Test-Learn (DBTL)`. This cycle is similar to the process of taking a test, learning from your mistakes, and achieving a better score on the next one.

![Overview of protein language model-enabled automatic protein evolution. In the Desing-Build-Test-Learn loop of protein engineering, PLMs are applied to facilitate the learning and design phases, while the build and test phases are executed by a biofoundry. Created in BioRender. Yu, H. (2024)](/resources/c8bbc8820431389b6b1c935baac79e77.png)

- Step 1: Design – Intelligent Planning
    
    In this stage, the AI analyzes the "language" of proteins using a PLM to predict and plan which amino acid sequences will optimize the protein's function. The PLM proposes new protein variant candidates using a special method called zero-shot prediction. Zero-shot prediction is the ability of a model to make predictions on new data it has not been directly trained on. Even without knowing specific mutation sites on a protein, the PLM can identify and design the most promising variants.
    
- Step 2: Build – Robotic Fabrication
    
    The protein variants designed by the PLM are then physically created in an automated robotic laboratory called a biofoundry. This process is carried out with high precision and speed.
    
- Step 3: Test – Robotic Functional Evaluation
    
    The biofoundry robots automatically test and evaluate how well the newly created protein variants actually work—for example, by measuring an enzyme's activity. All experimental data is systematically collected during this phase.
    
- Step 4: Learn – AI Knowledge Accumulation
    
    The data obtained from the robotic experiments is fed back to the PLM. The PLM analyzes this data to learn why certain protein variants were superior and which amino acid changes contributed to functional improvement. Through this learning process, the PLM can perform more accurate and efficient predictions in the next "Design" phase.
    

This `DBTL cycle` repeats continuously. Like climbing a spiral staircase, it finds a better protein with each iteration, continuing until the desired optimal protein is developed. This iterative process is very similar to the `active learning` strategy in machine learning, where a model intelligently selects which experiments to perform next to maximize information gain. This is a far more efficient approach than random or brute-force experimentation.

### 4. An In-depth Analysis of the Protein Language Model (PLM)

The most intelligent part of PLMeAE is the `Protein Language Model (PLM)`. The PLM is the core AI brain that understands the language of proteins and "designs" new ones.
![Resources: The conceptual similarities and hierarchical structure as seen in natural languages and proteins, https://pipebio.com/blog/protein-language-models](/resources/28666d3c41c2aa8f3066b97c94bef47a.png)

The PLM is trained on vast datasets of protein sequences. Just as a human learns the rules of a language by reading countless books, the PLM analyzes diverse protein sequences to figure out on its own which amino acid combinations form functional proteins and the fundamental principles of how proteins work and evolve. Thanks to this pre-trained knowledge, the PLM can predict the performance of a specific protein even without prior experimental data, a capability known as `zero-shot prediction`.

The way the PLM "designs" proteins is divided into two main modules.

![Protein language model used for protein automatic evolution. (a) Module I for engineering proteins without identified mutation sites. (b) Module II for engineering proteins with previously identified mutation sites. (c) Module I and Module II used in combination or independently. Created in BioRender. Yu, H. (2025)](/resources/b10aceb11c6d64983d7e1e8009ec5676.png)

- Module I (When Mutation Sites are Unknown)
    
    When the goal is to improve a protein but there's no prior information about specific mutation sites, the PLM steps in to help. The PLM individually "masks" (like a fill-in-the-blank question) each amino acid in the original protein sequence and predicts how much the protein's function would improve if it were replaced with other amino acids. The PLM then scores the potential functional improvement for each modified protein. The top 96 modified proteins with the highest scores are selected and "designed" for actual experimentation. This approach allows for a much more efficient search for superior modified proteins compared to random mutation. In experiments with the UBC9 and ubiquitin proteins, variants predicted by a PLM called ESM-2 showed significantly higher activity than randomly selected variants.
    
- Module II (When Mutation Sites are Already Known)
    
    If prior experiments or other information have already identified that mutations at specific locations in a protein are effective for improving function, the PLM is utilized differently. In this case, the PLM predicts which combination of amino acids at these known mutation sites would be most effective. It uses a special metric called Information Transport Complexity (ITC) to select the most "information-rich" (i.e., the most useful and diverse) modified proteins for experimentation. Based on the experimental data from these selected variants, the PLM trains a supervised machine learning model to predict protein performance with even greater accuracy. For example, in an experiment with the GB1 protein dataset, the ESM-2 model showed the highest accuracy in predicting the performance of single, double, and triple mutations.
    

Module I focuses on **'exploration'** (finding new, unknown mutation sites), while Module II focuses on **'exploitation'** (optimizing known sites). Using these two modules in combination allows the system to effectively navigate the protein `fitness landscape`, reflecting a deliberate strategy to balance finding entirely new solutions with improving existing promising ones. The `fitness landscape` is a concept that visualizes the functional fitness of each sequence in the protein sequence space as a topographical map.

![Visualization of two dimensions of a NK fitness landscape, Wikipedia](/resources/e15c92f5f07242d270d3cdb8057f8722.png)

### 5. The Hands and Feet of PLMeAE: The Role of the Automated Biofoundry

Another critical component of PLMeAE is the `Automated Biofoundry`. This is the robotic laboratory where the protein variants designed by the PLM are actually built and tested. Like a state-of-the-art factory, every process is automated.

The biofoundry is equipped with a variety of advanced robotic instruments, such as robotic arms for precise liquid handling (`liquid handler`), machines for temperature control (`thermocycler`), and equipment for DNA analysis (`fragment analyzer`). All these instruments are perfectly interconnected and operated by robotic arms and intelligent software. The efficiency of the biofoundry comes from its ability to process numerous experiments simultaneously (96 variants per round) and automate labor-intensive steps. This parallel processing and minimization of human intervention are key.


![Overview of automatic protein variants build and test. (a) Workflow for protein variants build and test using biofoundry.](/resources/a73308b756d06bc539412f6cfa32deb8.png)

- Automation of the Protein 'Build' Step
    
    Once the PLM provides 96 protein sequences, a computer code (Python programming) automatically designs the DNA fragments (primers) and orders them from a synthesis company. An automated robotic workstation (Evo) precisely mixes the necessary reagents for the PCR (gene amplification) reaction, a plate sealer (ALPS) seals the experimental plates, and an automated thermocycler runs the gene amplification reaction at precise temperatures. A robot unseals the plates (Xpeel), and a liquid handler using sound waves (Echo) removes unwanted DNA. Next, another robotic workstation (Evo) introduces the fabricated DNA into cells (E. coli) that will produce the proteins. A different workstation (Fluent) spreads the cells onto agar plates with nutrients, a labeler (Agilent Labeler) attaches tags to the plates, and the cells are cultured in an incubator to grow.
    
- Automation of the Protein 'Test' Step
    
    The next day, a robotic colony picker (Fluent) picks individual cell clusters (colonies) from the agar plates and transfers them to liquid nutrient media, where they are cultured again in an incubator. A robotic centrifuge (Rotanta) collects the cell cultures, a reagent dispenser (Multidrop Combi) replaces the old media with new, and the cells are incubated again to express the proteins. Finally, an automated microplate reader (CLARIOstar) automatically measures the enzymatic activity of each protein variant, and a computer software (Momentum DataMiner) analyzes the data.
    


![Overview of automatic protein variants build and test. <br>(c) Multiple layers of exception handling and data quality control for failed experimental steps.](/resources/16b6c69b385169da88f2abdd39748506.png)

This robotic system does more than just perform tasks; it also has intelligent functions to check for and handle errors on its own. For instance, it automatically verifies whether the PCR reaction proceeded correctly and if the cells grew well. If a problem occurs, the system automatically re-attempts the step, increasing the `reliability` of the experiment. The entire process of creating and testing 96 protein variants takes about 59 hours (including primer delivery time), which is much faster and more accurate than manual work. This automation not only speeds up experiments but also minimizes human error and significantly enhances `reproducibility` through comprehensive metadata tracking and real-time data sharing. The built-in "exception handling and data quality control" ensures reliable data, which is essential for effective machine learning model training.

### 6. A Real-World Success Story of PLMeAE: The Evolution of the pCNF-RS Enzyme

The outstanding performance of PLMeAE was proven through actual experimental results. The researchers tested the platform's capabilities using an enzyme called `pCNF-RS` as a model.

`pCNF-RS` is an enzyme that incorporates `non-canonical amino acids (ncAAs)` into proteins. Although this enzyme can recognize several types of ncAAs, its efficiency in incorporating them into proteins was low. For example, the expression level of a protein with a specific ncAA (pAcF) was only 60% of that of a normal protein. The researchers aimed to use PLMeAE to increase the efficiency of this pCNF-RS enzyme.

First, the researchers used PLMeAE's `Module II` to focus on improving four amino acid positions (H283, P284, M285, D286) in the pCNF-RS enzyme that were known from previous studies to be important.

![Protein language model used for engineering proteins with identified mutations. <br>(a) A scheme illustrating application of PLM for sampling informative mutants at one mutation site, assuming that four amino acids are selected. (b) A flow chart illustrating the process of PLMeAE Module II. FP, fitness predictor.](/resources/f8afa20cd108d17b1be7fbe073e3eee7.png)

- **Round 1 (Module II):** The PLM (ESM-2) predicted 96 variant candidates, which the biofoundry robots built and tested. The best variant (M-R1) showed a 1.3-fold improvement in activity compared to the original enzyme.
    
- **Round 2 (Module II):** After learning from the Round 1 data, the PLM predicted another 96 variants. This time, the best variant (M-R2) was 2.0 times more active than the original enzyme, and the number of variants with higher activity than the original was much larger than in Round 1.
    
- **Round 3 (Module II):** Based on the data from Rounds 1 and 2, the PLM predicted another 96 variants. These variants had more diverse amino acid combinations, and the proportion of highly active variants increased to 62.5%. However, the maximum activity improvement was 2.1-fold, not a significant jump from Round 2. The observation that the third round of Module II did not yield significant improvement illustrates the phenomenon of `diminishing returns`. This was a signal that major improvements were unlikely with the current search strategy.
    

-> **Diminishing Returns:** The principle that as you increase one input of production, while keeping other inputs fixed, the marginal output you get from that additional input will eventually start to decrease.

- **Round 4 (Switch to Module I):** Concluding from Round 3 that further significant improvements were unlikely with Module II alone, the researchers decided to switch to PLMeAE's `Module I` to explore new mutation sites. Using the best variant from Round 3 (M-R3) as a base, the PLM (ESM-2) predicted 96 new single variants. Surprisingly, these new mutations were not at the sites focused on in the previous rounds but were found in various other locations across the enzyme. This strategic shift to Module I to explore new mutation sites demonstrates the platform's `adaptive intelligence` and its ability to overcome `local optima`.
    
- **Final Result:** The best variant found in Round 4 (M-R4) was a remarkable 2.4 times more active than the original enzyme and 1.2 times better than the best variant from Rounds 1-3. Thanks to this M-R4 enzyme, the production of a protein called sfGFP with an incorporated ncAA was 12.1 times higher than when using the original enzyme. The M-R4 enzyme also showed higher efficiency in simultaneously suppressing multiple `amber codons` (signals that stop protein production) and improved the incorporation efficiency of 10 different types of ncAAs into proteins. It even successfully improved ncAA incorporation efficiency in other important proteins like `transketolase (TK)` and `nanobody`. The success with the pCNF-RS enzyme, and its applicability to multiple `amber codons`, various ncAAs, and even other target proteins (TK, nanobody), suggests that this platform is broadly applicable beyond a specific model system.
    

### 7. The Innovativeness of PLMeAE: A Comparison with Traditional Methods

The innovative nature of PLMeAE becomes even clearer when compared to traditional protein engineering methods.

- Speed and Time Efficiency
    
    PLMeAE completed four rounds of protein evolution in just 10 days. This 10-day period included the delivery time for primers (DNA fragments), so the actual robotic experimentation time was even shorter. In contrast, the conventional positive/negative selection method took a staggering 38 days for just two rounds of evolution. Moreover, the high probability of experimental failure meant it could often take even longer. This shows that PLMeAE is nearly four times faster.
    
- Efficiency and Success Rate (Positive Rate)
    
    PLMeAE achieved a very high positive rate (the proportion of variants found to have the desired improved function) of 50% in the second round and 62.5% in the third round. This is thanks to the intelligent predictions of the PLM. In contrast, methods that rely on random mutation and screening have a positive rate of a mere 2.2%. This means only about 2 out of 100 attempts are successful, highlighting just how efficient PLMeAE is.
    
- Difference in Search Strategy
    
    Through the PLM's zero-shot prediction and its ability to "learn" from experimental data, PLMeAE intelligently designs and explores the most promising variants based on information. Therefore, it can efficiently navigate the broader and more complex protein sequence space without getting trapped in local optima. Sequence space refers to the set of all possible protein sequences. Traditional methods relied on trial-and-error, creating random mutations and testing them one by one, which often resulted in getting stuck at suboptimal solutions.
    
- Automation and Reproducibility
    
    In PLMeAE, robots automatically perform most of the experimental process. This reduces human error and ensures a high level of reproducibility, meaning the experimental results are consistent. Additionally, the system is equipped with a data quality control mechanism where robots detect and re-run failed steps. Traditional methods involve a lot of manual labor, making them labor-intensive and susceptible to human error, which can lead to inconsistent results and low reproducibility.
    

|Feature|Traditional Methods|PLMeAE|
|---|---|---|
|**Speed**|Slow and time-consuming (e.g., 38 days for 2 rounds)|Much faster (e.g., 10 days for 4 rounds)|
|**Effort**|Highly labor-intensive, requires much manual work|Mostly automated by robots, minimal human intervention|
|**Accuracy**|Inefficient with much trial-and-error, risk of `local optima`|High accuracy with smart prediction (PLM), broader space exploration|
|**Discovery**|Limited and difficult, low `positive rate` (approx. 2.2%)|Efficient info-based design, high `positive rate` (up to 62.5%)|
|**Overall Efficiency**|Low|Very high|
|**Data Reliability**|Prone to errors from manual work|Automated quality control, high `reproducibility`|

### 8. The Future of Synthetic Biology Through the Lens of PLMeAE

PLMeAE holds immense potential for the field of protein engineering. We can imagine what this technology will make possible in the future.

- Expansion to Diverse Enzyme Engineering
    
    Currently, PLMeAE has been successfully applied mainly to enzymes whose activity can be measured by fluorescence. In the future, it could be applied to other types of enzymes whose activities are measured by various methods like liquid chromatography (LC), gas chromatography (GC), and mass spectrometry (MS). This means PLMeAE could improve a much wider range of proteins. As these automated platforms become more sophisticated, they could provide researchers without expertise in complex manual lab techniques access to cutting-edge protein engineering, accelerating the overall pace of discovery.
    
- Advancement of Genetic Code Expansion (GCE) Technology
    
    The success of PLMeAE in improving the efficiency of tRNA synthetases like pCNF-RS is highly significant. Building on this success, other tRNA synthetases can be further improved, which could greatly expand the applications of GCE technology. GCE is a crucial technique for imparting novel functions to proteins.
    
- Accelerating Innovation in Industrial Sectors
    
    Proteins are essential in a wide range of industries, including pharmaceuticals (new drug development, cancer therapies), chemicals (more efficient catalysts), energy, agriculture, and even everyday consumer goods. By increasing the speed and accuracy of protein engineering, PLMeAE can help produce more efficient proteins in all these fields, ultimately accelerating progress across the board.
    
- The Dawn of the "Self-Driving Laboratory" Era
    
    PLMeAE presents a future where proteins can be evolved highly efficiently with minimal human intervention. This will allow scientists to spend less time on manual lab work and focus more on creative and critical research. It's as if the self-driving laboratory is becoming a reality.
    
    The Automated Biofoundry generates massive amounts of data. This data is, in turn, crucial for training more advanced AI models, creating a positive feedback loop for future scientific AI development. The biofoundry not only consumes AI designs but also produces the data for the AI of the future.
    
- Challenges and the Importance of Collaboration
    
    Of course, developing such a cutting-edge system is not easy. Collaboration is essential at the intersection of various fields like biology, computer science, and robotics, and building a biofoundry requires significant investment. Therefore, it will be crucial for researchers from diverse fields to collaborate more closely and to train a new generation of scientists who understand both AI and robotic technologies.
    

In short, the PLMeAE platform integrates the intelligent "brain" of the `Protein Language Model (PLM)` with the powerful robotic technology of the `Automated Biofoundry` to make the process of protein evolution much faster and more efficient.

I know this review was quite long, but I felt every part was too valuable to omit. It lays out crucial information and processes that point to the future direction of biotechnology research, so I intentionally included all the details.

The most important takeaway for me from this paper was the impressive virtuous cycle created by using AI and robotics together for maximum synergy. The model where AI serves as the brain and robots act as the hands and feet for experiments clearly addresses the limitations of traditional biotechnology. This strongly suggests that biotech research can make significant leaps forward through this approach. Furthermore, platforms like PLMeAE not only upgrade existing proteins but also accelerate and streamline the exploration of the protein fitness landscape. This enables scientists to explore much larger and more complex sequence spaces that were previously impossible or too difficult to tackle. This means we can discover proteins with properties once considered impossible or too hard to find. I believe this platform will be a tremendous help in discovering and utilizing new proteins in various fields such as medicine, industry, and agriculture in the future.

**Reference:** Zhang, Qiang, et al. "Integrating protein language models and automatic biofoundry for enhanced protein evolution." _Nature Communications_ 16.1 (2025): 1553.