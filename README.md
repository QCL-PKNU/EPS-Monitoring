
# EPS Monitoring system



## Installation


Clone Project

```bash
  git clone https://github.com/QCL-PKNU/EPS-Monitoring.git
  cd  EPS-Monitoring 
  cd deps

```
## Project Structure


    .
    ├── deps                    # Our main folder consists of connection GPIO of Raspberry Pi
    ├── deps_sensor             # Arduino code 
    ├── deps_standalone         # Contains of the mimic codes from deps package that used for testing our project.
    └── README.md
## Environment Setup

To run this project, you may find the requirement and some configuration from our documentation which locate in [here](https://github.com/QCL-PKNU/EPS-Monitoring/blob/main/deps/doc/EPS%20%EB%AA%A8%EB%8B%88%ED%84%B0%EB%A7%81%20%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%A8%20%EC%84%A4%EC%B9%98%20%EB%B0%8F%20%EC%82%AC%EC%9A%A9%EB%B2%95.docx).


#### Run the project 
```bash
  python src/deps_main.py
```

## Features updates
- New update UI based on 7 inches screen of Raspberry Pi
- Thermal Image 
- Current Consumption



## Documentation

Documentation of the project structure can be found [here](https://github.com/QCL-PKNU/EPS-Monitoring/tree/main/deps/doc).

