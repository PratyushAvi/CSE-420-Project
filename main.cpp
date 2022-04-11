#include <iostream>
#include <fstream> 
#include <stdio.h>
#include <assert.h>
#include <math.h>
#include "pin.H"

using namespace std;
// This knob will set the outfile name
KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
			    "o", "results.out", "specify optional output file name");

UINT64 counter = 0;
ofstream outfile;
UINT32 memcounter = 0;

// Pin calls this function every time a new instruction is encountered
VOID Instruction(INS ins, VOID *v)
{
    outfile << INS_Address(ins) << ",";
    outfile << "\"" << INS_Disassemble(ins) << "\",";
    outfile << OPCODE_StringShort(INS_Opcode(ins)) << ",";
    outfile << CATEGORY_StringShort(INS_Category(ins)) << ",";
    outfile << INS_IsBranch(ins) << ",";
    outfile << INS_IsControlFlow(ins) << ",";
    outfile << INS_IsMemoryRead(ins) << ",";
    outfile << INS_IsMemoryWrite(ins) << ",";
    outfile << INS_IsCall(ins) << ",";

    /*****************************************
     * Add read registers and memory to data
    *****************************************/

    outfile << "R[";
    for (UINT32 i = 0; i < INS_MaxNumRRegs(ins); i++) 
    {
        outfile << REG_FullRegName(INS_RegR(ins, i)) << " ";
    }

    for (UINT32 memOps = 0; memOps < INS_MemoryOperandCount(ins); memOps++)
    {   
        memcounter++;
        if (INS_MemoryOperandIsRead(ins, memOps))
        {
            UINT32 n = INS_MemoryOperandIndexToOperandIndex(ins, memOps);
            outfile << INS_OperandMemoryDisplacement(ins, n) 
                + INS_OperandMemoryBaseReg(ins, n) 
                + INS_OperandMemoryIndexReg(ins, n) 
                * INS_OperandMemoryScale(ins, n) << "M ";
        }
    }
    outfile << "]" << "," << "W[";

    /*****************************************
     * Add write registers and memory to data
    *****************************************/

    for (UINT32 i = 0; i < INS_MaxNumWRegs(ins); i++) 
    {
        outfile << REG_FullRegName(INS_RegW(ins, i)) << " ";
    }

    for (UINT32 memOps = 0; memOps < INS_MemoryOperandCount(ins); memOps++)
    {
        if (INS_MemoryOperandIsWritten(ins, memOps))
        {
            UINT32 n = INS_MemoryOperandIndexToOperandIndex(ins, memOps);
            outfile << INS_OperandMemoryDisplacement(ins, n) 
                + INS_OperandMemoryBaseReg(ins, n) 
                + INS_OperandMemoryIndexReg(ins, n) 
                * INS_OperandMemoryScale(ins, n) << "M ";
        }
    }
    outfile << "]" << endl;
    
    counter++;
}

// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
    outfile << endl;
    cout << counter << endl;
    cout << memcounter << endl;
}

// argc, argv are the entire command line, including pin -t <toolname> -- ...
int main(int argc, char * argv[])
{
    // Initialize pin
    PIN_Init(argc, argv);
	
    outfile.open(KnobOutputFile.Value().c_str());
    outfile << "Address,INS,Opcode,Category,isBranch,isControlFlow,isMemoryRead,isMemoryWrite,isCall,Read_Regsiters,Write_Registers" << endl;

    // Register Instruction to be called to instrument instructions
    INS_AddInstrumentFunction(Instruction, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);

    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}
