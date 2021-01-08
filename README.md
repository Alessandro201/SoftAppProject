# SoftAppProject
This is the webpage made for  the 
<a href="https://github.com/anuzzolese/genomics-unibo/tree/master/2020-2021/project">Data Analysis Project</a> of the software application course of Genomics.

<br>

<h2>Goal</h2>

<i>"The COVID-19 DisGeNET data collection is the result of applying state-of-the art text
mining tools developed by MedBioinformatics solutions to the LitCovid dataset
<a href="https://pubmed.ncbi.nlm.nih.gov/32157233/">Chen et al., 2020</a>, 
to identify mentions of diseases, signs and symptoms. The LitCovid dataset contains a selection of
papers referring to Coronavirus 19 disease."</i>
<br>
The goal of the project is to write a program able to analyse two datasets about
diseases and genes obtained from the COVID-19 DisGeNET data collection and present the results in
a web-based user interface.

<br>

<h2>Components</h2>

The program is divided in four components:

- <a href="https://github.com/AlessandroPoletti/SoftAppProject/blob/master/functions.py">functions.py</a>
Is the part2 described in the project specifications which contains all the operations to perform
on the two datasets<br>

- <a href="https://github.com/AlessandroPoletti/SoftAppProject/blob/master/website.py">website.py</a>
Is the part3 described in the project specifications which creates the webpage, get the inputs from the user and presents the results<br>

- <a href="https://github.com/AlessandroPoletti/SoftAppProject/blob/master/mediator.py">mediator.py</a>
Is the part1 described in the project specifications which connects part2 and part3<br>

- <a href="https://github.com/AlessandroPoletti/SoftAppProject/blob/master/settings.py">settings.py</a>
Contains the global variables of the program like the path to the datasets<br>
