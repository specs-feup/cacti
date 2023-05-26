# CACTI 

This repository holds the code, specific to each compiler, that is necessary to:
- Test the compilers ability to correctly parse the input source code
- Test the compilers ability to correctly generate a source file with an identical structure to the one input by the user

## About CACTI 

**CACTI** (**C**ompiler **A**nalysis, **C**omparison & **T**esting **I**nfrastructure) is a project being developed by four software-engineering students, for the Capstone Project curricular unit.

As the name suggests, CACTI wishes to study and compare the capabilities of different compilers, by collecting/creating several input C and C++ files that represent various functionalities of each language, and by defining and implementing tests for each transpiliation task (parsing, code generation, querying and transformation).

## Members

### Students 
- Fábio Morais (<a href="https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico=202008052">202008052</a>) - Faculty of Engineering, University of Porto, Portugal
- Francisco Prada (<a href="https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico=202004646">202004646</a>) - Faculty of Engineering, University of Porto, Portugal
- Guilherme Sequeira (<a href="https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico=202004648">202004648</a>) - Faculty of Engineering, University of Porto, Portugal
- Pedro Ramalho (<a href="https://sigarra.up.pt/feup/pt/fest_geral.cursos_list?pv_num_unico=202004715">202004715</a>) - Faculty of Engineering, University of Porto, Portugal

### Tutors

- <a href="https://sigarra.up.pt/feup/pt/func_geral.formview?p_codigo=519965">João Bispo</a> - Faculty of Engineering, University of Porto, Portugal
- <a href="https://sigarra.up.pt/feup/pt/func_geral.formview?p_codigo=662695">Luís Sousa</a> - Faculty of Engineering, University of Porto, Portugal

## How to run

In order to launch CACTI, you may run the following command:

```
$ python3 cacti.py -S <source_path> -T <transpiler_name>
```

CACTI offers a sample of mandatory arguments (like the ones above, `-S` and `-T`), as well as some additional flags, in order to customize the output. Below is an explanation of the current implemented arguments and flags:
- `-S <source_path>` - specify the path to the source files which are to be tested
- `-T <transpiler>` - the name of the transpiler which is to be tested
- `-vi`, `-vc` - enable verbose idempotency & correctness, respectively
- `-std <CXX>` - specify the C/C++ standard to be used
- `-opt <O>` - specify the optimization flag that is to be used by Clang's `emit_llvm` flag (e.g, `O0`)
- `it <N>` - specify the maximum number of idempotency tries 

*Note: in order to run it is necessary to have Python 3 or above.*

## Sources

- [cppreference](https://en.cppreference.com) - 
the source files in this repository were adapted from the example code available here.