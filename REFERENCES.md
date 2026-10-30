# References and attribution

No external dataset is used: all networks, loads and future demand sequences are generated synthetically. Generator settings and seeds are recorded with the results.

## Mathematical and network background

1. A. E. Motter and Y.-C. Lai, “Cascade-based attacks on complex networks,” *Physical Review E*, vol. 66, 065102, 2002. DOI: [10.1103/PhysRevE.66.065102](https://doi.org/10.1103/PhysRevE.66.065102). [Accessible manuscript](https://arxiv.org/abs/cond-mat/0301086). Supports the overload-cascade mechanism; our persistent workload and local redistribution rules differ from its shortest-path load model.
2. D. J. Watts and S. H. Strogatz, “Collective dynamics of ‘small-world’ networks,” *Nature*, vol. 393, pp. 440–442, 1998. DOI: [10.1038/30918](https://doi.org/10.1038/30918). Background for the small-world generator.
3. A.-L. Barabási and R. Albert, “Emergence of scaling in random networks,” *Science*, vol. 286, pp. 509–512, 1999. DOI: [10.1126/science.286.5439.509](https://doi.org/10.1126/science.286.5439.509). [Manuscript](https://arxiv.org/abs/cond-mat/9910332). Background for preferential-attachment graphs; finite N=100 graphs are BA samples, not proof of a power law.
4. R. G. Sanfelice, R. Goebel, and A. R. Teel, “Generalized solutions to hybrid dynamical systems,” *ESAIM: Control, Optimisation and Calculus of Variations*, vol. 14, pp. 699–724, 2008. [Author-hosted paper](https://webpages.math.luc.edu/~rgoebel1/publications/journals/SanfeliceGoebelTeel08ESAIMCOCV.pdf). Background for continuous flows and discrete jumps, not a network-specific collapse formula.
5. C. M. Grinstead and J. L. Snell, *Introduction to Probability*, 2nd ed., American Mathematical Society, 2003; freely available CHANCE edition dated July 4, 2006. [Textbook](https://math.dartmouth.edu/~prob/prob/prob.pdf), Chapter 11. Standard absorbing-state and first-passage reasoning; our continuous-state recurrence is obtained directly by conditioning on the next demand increment.
6. C. Boettiger, N. Ross, and A. Hastings, “Early warning signals: the charted and uncharted territories,” *Theoretical Ecology*, 2013. DOI: [10.1007/s12080-013-0192-6](https://doi.org/10.1007/s12080-013-0192-6). [Manuscript](https://arxiv.org/abs/1305.6700). Explains why abrupt transitions do not automatically imply critical slowing down. We do not claim that phenomenon in this model.

## Software and services

7. A. A. Hagberg, D. A. Schult, and P. J. Swart, “Exploring network structure, dynamics, and function using NetworkX,” in *Proceedings of the 7th Python in Science Conference*, 2008, pp. 11–15. [Paper](https://aric.hagberg.org/papers/hagberg-2008-exploring.pdf). [Generator documentation](https://networkx.org/documentation/stable/reference/generators.html), including the independent-edge G(n,p) random graph generator.
8. C. R. Harris et al., “Array programming with NumPy,” *Nature*, vol. 585, pp. 357–362, 2020. DOI: [10.1038/s41586-020-2649-2](https://doi.org/10.1038/s41586-020-2649-2). [Official citation](https://numpy.org/citing-numpy/).
9. J. D. Hunter, “Matplotlib: A 2D graphics environment,” *Computing in Science & Engineering*, vol. 9, no. 3, pp. 90–95, 2007. DOI: [10.1109/MCSE.2007.55](https://doi.org/10.1109/MCSE.2007.55). [Official citation](https://matplotlib.org/stable/project/citing.html).
10. Python Software Foundation, [Python](https://www.python.org/); Project Jupyter, [Jupyter](https://jupyter.org/); Google, [Google Colaboratory](https://colab.research.google.com/) and [Colab MCP](https://github.com/googlecolab/colab-mcp); GitHub, [GitHub](https://github.com/). Used for development, execution and version control. Local execution versions are recorded in `results/validation/environment.json`; Colab versions may differ.
11. OpenAI, Codex/ChatGPT assistance, October 2026. Used in code drafting, mathematical explanations and experiment preparation. This acknowledgement does not substitute for primary mathematical references or verification; the group must review and understand the submitted work.

Web references accessed October 30, 2026. Only cite sources actually used in the final report; retain appropriate software acknowledgement. No bibliographic claim of novelty is supported by this short literature review.
