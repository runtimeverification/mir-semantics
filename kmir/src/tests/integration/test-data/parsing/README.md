This folder contains `.mir` files for testing the K definition of mir syntax.
These `.mir` files are not necessary legal mir programs or a complete mir representation of an executable rust program.

Instructions for running the tests:

Generate the `mir` output (runtime-optimisd) for a source file `*.rs`:
```rustc enum.rs --emit mir -o enum.txt```

Genrate all intermediate `mir` representation of a source file, the following command could be used:
``` rustc main.rs -Z dump-mir=main ```

Run ``` rustc -Z help ``` to get more options for querying the complition process.