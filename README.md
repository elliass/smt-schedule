<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/elliass/smt-schedule">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">SMT scheduling
</h3>

  <p align="center">
    Scheduling UWB-TSCH network communications using an SMT solver
    <br />
    <a href="https://github.com/elliass/smt-schedule/tree/master/src"><strong>Explore the project »</strong></a>
    <br />
    <br />
    <a href="https://www.overleaf.com/project/6453e380894b146dd444f6ff">View full paper</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#architecture">Architecture</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#input">Input</a></li>
    <li><a href="#output">Output</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project aims to address the challenges of scheduling Ultra Wideband Time-Slotted Channel Hopping (UWB-TSCH) communications using a novel approach that leverages Satisfiability Modulo Theories (SMT) solvers. UWB-TSCH networks offer high data rates as well as high-precision ranging capabilities extremely useful in positioning applications. However, providing an efficient scheduling for such network is crucial in order to maximize their potential.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

[![Python][Python]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ARCHITECTURE -->
## Architecture

![Project Architecture][project-architecture]


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these steps.

### Prerequisites

For this project, you need to have the following installed:
* python

  Check if you have python installed
  ```sh
  python --version
  ```

### Installation

1. Clone the repo with HTTPS
   ```sh
   git clone https://github.com/elliass/smt-schedule.git
   ```
2. Clone the repo with SSH
   ```sh
   git clone git@github.com:elliass/smt-schedule.git
   ```
3. Install Python libraries
   ```sh
   pip install -r requirements.txt
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE -->
## Usage

Run scheduling algorithm
1. Run main with default topology and parameters
   ```sh
   python main.py
   ```
2. Run main with user topology
   ```sh
   python main.py --topology=TOPOLOGY_FOLDER
   ```
3. Run main with user parameters
   ```sh
   python main.py --max_solutions=MAX_SOLUTIONS --max_slots=MAX_SLOTS --max_channels=MAX_CHANNELS --max_retries=MAX_RETRIES
   ```

   The topology should be defined within the folder "in/". An example of topology format is described in Section <a href="#input"> Input</a>

4. Run main with network simulation
   ```sh
   python main.py --watch
   ```

Test scheduling algorithm
1. Test all solutions generated by the scheduling algorithm with default topology
   ```sh
   python test.py --all
   ```
2. Test all solutions generated by the scheduling algorithm with user topology
   ```sh
   python test.py --topology=TOPOLOGY_FOLDER --all
   ```
3. Test a specific solution provided by the user as a json string
   ```sh
   python test.py --solution=SOLUTION
   ```

   An example of solution not violating any constraints:
   ```js
   '{"timeslot": [3,1,2,2,4],"channel": [0,1,0,1,0]}'
   ```

   An example solution violating one constraint (shared constraint): 
   ```js
   '{"timeslot": [0,1,2,2,4],"channel": [0,1,0,1,0]}'
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- INPUT -->
## Input

The scheduling algorithm expects a JSON file describing the network topology. The file should be defined within the project folder "in/", inside a sub-folder:
   ```sh
   /in/your_topology_folder/example_topology.json
   ```

An example topology with one cell, 3 anchors and 1 tag: 

   ```js
    {
       "cell1": {
           "tags": ["t1"],
           "anchors": ["a1","a2","a3"],
           "parent": "a1",
           "next_parent": "a1"
       }
   }
   ```

The topology folder may contain multiple topology files. The scheduling algorithm will be executed for each file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- OUTPUT -->
## Output
From the example topology described in the previous section, the scheduling algorithm will produce the following outputs in the project folder "out/", inside a sub-folder related to the topology.
   ```sh
   /out/your_topology_folder/
   ```

#### Logs
The execution of the scheduling algorithm will produce logs for each topology and append them in the file logs.json. The log file provides network information as well as scheduling outcomes such as: the number of constraints generated, the number of solutions found and the execution time.

   ```js   
   {
     "cell1_t1.json": {
       "nb_nodes": 4,
       "nb_edges": 5,
       "nb_communications": 5,
       "nb_solutions": 1,
       "nb_constraints": 45,
       "nb_slots": 4,
       "nb_channels": 1,
       "nb_retries": 0,
       "edges": ["e0","e1","e2","e3","e4"],
       "communications": [["t1","a1"],["t1","a2"],["t1","a3"],["a2","a1"],["a3","a1"]],
       "solutions": [{"timeslot": [3,1,2,2,4],"channel": [0,1,0,1,0]}],
       "processing_time": 0.06272697448730469
     }
   }
   ```
  

#### Solutions
Each solution is represented with a list of timeslots and channels assigned to each edge in the network. Hence, the first "e0" is assigned the timeslot 3 and the channel 0. Solutions are written in the file solutions.json.

   ```js
   [
     {
       "timeslot": [3,1,2,2,4],
       "channel": [0,1,0,1,0]
     }
   ]
   ```


#### Slotframe
Each solution represents a slotframe and is be better illustrated using a table. The algorithm randomly selects one solution and outputs it in the file slotframe.json.

| ch/ts     | slot 0       | slot 1       | slot 2       | slot 3       | slot 4       |
| :---:     | :---:        | :---:        | :---:        | :---:        | :---:        |
| channel 1 |              | e1: t1 ↔ a2  | e3: a2 → a1  |              |              |
| channel 0 |              |              | e2: t1 ↔ a3  | e0: t1 ↔ a1  | e4: a3 → a1  |


#### Network communications
Additionally, the algorithm outputs the network communications inside the file communications.json
| Communication | Edge  | Nodes     |
| :---:         | :---: | :---:     |
| Ranging       | e0    | t1 ↔ a1   |
| Ranging       | e1    | t1 ↔ a2   |
| Ranging       | e2    | t1 ↔ a3   |
| Forwarding    | e3    | a2 → a1   |
| Forwarding    | e4    | a1 → a1   |

<!-- 
#### Network constraints
Additionally, the algorithm outputs the network constraints inside the file constraints.json -->


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact
Project Link: [https://github.com/elliass/smt-schedule](https://github.com/elliass/smt-schedule)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[product-screenshot]: images/screenshot.png

[project-architecture]: images/architecture.png

[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/