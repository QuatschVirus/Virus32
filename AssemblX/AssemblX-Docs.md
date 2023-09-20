# Virus32 - 32bit CPU / Computer

## Memory Locations:
### Data Bus (Storage):
  - Deposit Register for depositing data during an instruction. Gets cleared on EI
  - Register A-D
  - RAM
  - GRAM
  - Character-GRAM
  - Argument Bus
  - ALU-A
  - ALU-B
  - ALU-C
  - ALU-OA
  - ALU-OB

### System

- Instruction Register (36bit)
- RAM Address Register  
- Subcommand-Register
    
---

All WE-Signals on Data Bus:
1. Deposit
2. A
3. B
4. C
5. D
6. RAM
7. Port
8. Arg Bus
9. GRAM / CharRAM
10. ALU-A
11. ALU-B
12. ALU-C

All OE-Signals on Data Bus:
1. Deposit
2. A
3. B
4. C
5. D
6. RAM
7. Port
8. Arg Bus
9. ALU-OA
10. ALU-OB

All WE-Signals on Arg Bus:
1. RAM Addr
2. GRAM Addr
3. Data Bus
4. Instruction Counter

ALL OE-Signals on Arg Bus:
1. InstReg (On by default)
2. Data Bus


## AssemblX

### Definitions
- Primary Registers: The internal Registers A through D
- Registers (in the context of AssemblX): Primary Registers plus the ALU registers
- Port: Refers to the Data Bus Port
- Simple Storage: Primary Registers, ALU registers and Port
- GRAM: Graphics RAM, meaning GRAM or CharRAM depending on the GPU mode

### AssemblXS (AssemblX Subcommands)
| Id  | Name | Name Explanation   | Functionality                                                                           |
|:---:|:----:|--------------------|-----------------------------------------------------------------------------------------|
| 000 | EIS  | End Instruction    | End Instruction (Clear Deposit, Reset WE and OE)                                        |
| 001 | DWE  | Data Write Enable  | Enables one of the Data Bus Accessors                                                   |
| 010 | DOE  | Data Output Enable | Enables one of the Data Bus Writers                                                     |
| 011 | AWE  | Arg Write Enable   | Enables one of the Arg Bus Accessors                                                    |
| 100 | AOE  | Arg Output Enable  | Enables one of the Arg Bus Writers                                                      |
| 101 | ALU  | ...                | Sets the ALU operator                                                                   |
| 110 | GPU  | ...                | GPU Control (abcd: a controls mode, b controls render, c controls clear, d is reserved) |
| 111 | ITR  | Interrupt          | Starts / Awaits an interrupt (Selected by Bit 8)                                        |

### AssemblX Commands
|  Id  | Name | Name Explanation            | Argument Structure | Argument Explanation                                           | Functionality                                                                                                 |
|:----:|:----:|-----------------------------|-------------------:|----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| 0000 | NOP  | No Operation                |                    |                                                                | Do nothing                                                                                                    |
| 0001 |  CD  | Copy Data                   |         `AAAABBBB` | A: Select source, B: Select target; both out of Simple Storage | Reads data from source and copies it into target                                                              |
| 0010 |  SD  | Swap Data                   |         `AAAABBBB` | Select two out of Simple Storage                               | Swaps the data between the to selected storages                                                               |
| 0011 |  LD  | Load Data                   |                    | The data to store                                              | Stores the given data directly into the Register A                                                            |
| 0100 | SMA  | Set Memory Address          |                    | The RAM address to set                                         | Sets the address the RAM is pointing to. Since it has only 24bit addresses, only  the first 24 Bits get used  |
| 0101 | SGMA | Set Graphics Memory Address |                    | The GRAM address to set                                        | Sets the address the GRAM is pointing to. Since it has only 24bit addresses, only  the first 24 Bits get used |
| 0110 | CLD  | Clear Data                  |             `AAAA` | The Register to clear                                          | Clears the given register (by setting every bit to 0)                                                         |
| 0111 | JMP  | Jump                        |                    | The index to jump to                                           | Unconditionally jumps the the specified index                                                                 |
| 1000 | DJMP | Dynamic Jump                |             `AAAA` | Select index source                                            | Jumps to the index read from Source                                                                           |
| 1001 | JMPE | Jump if Equals              |                    | The index to jump to                                           | Jumps to the specified index if ALU_A == ALU_B                                                                |
| 1010 |  IR  | Interrupt                   |             `ABBB` | A: The operation (Trigger or Await), B: the interrupt          | Triggers/Awaits the specified interrupt                                                                       |
| 1011 | GPU  | ...                         |             `ABCD` | A: GPU mode, B: (Re)Render, C: Clear screen                    | Controls the GPU                                                                                              |
| 1100 | ALU  | ...                         |             `AAAA` | Sets the operation the ALU performs                            | Control the ALU                                                                                               |
| 1101 |      |                             |                    |                                                                |                                                                                                               |
| 1110 |      |                             |                    |                                                                |                                                                                                               |
| 1111 | HLT  | Halt                        |                    |                                                                | Stops the instruction counter, which also stops the whole processor                                           |