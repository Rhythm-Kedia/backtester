# Assignment 2

This is more of how we can use CPU to make our code faster. Yes, we can use @jit in python, but still you need to have an idea how does multithreading works and what is the idea behind it.

## The codes :

1. Ex1 , Ex2 , Ex3 : Basic multithreading with lock features
2. Naive, Parallel , and, driver : Multithreading to do matrix multiplication

### Using the code:

For Ex1 , Ex2 , Ex3 : 
Just read and execute the code.

For Naive, Parallel , and, driver:

- do : g++ -Wall driver.cpp {strat}.cpp -o {strat}

    Where strat is the name of the strat Naive and Parallel. On running you will see the execution times.
  For example : For me on entry of 500 , I got 0.67s for Naive and 0.14s for Parallel.
