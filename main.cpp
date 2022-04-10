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

// Pin calls this function every time a new instruction is encountered
VOID Instruction(INS ins, VOID *v)
{
    outfile << INS_Address(ins) << "," << OPCODE_StringShort(INS_Opcode(ins)) << "," << CATEGORY_StringShort(INS_Category(ins)) << "," << INS_IsBranch(ins) << "," << INS_IsControlFlow(ins) << ",";
    outfile << INS_IsMemoryRead(ins) << "," << INS_IsMemoryWrite(ins) << "," << INS_IsCall(ins) << ",";

    outfile << "R[";
    for (UINT32 i = 0; i < INS_MaxNumRRegs(ins); i++) 
    {
        outfile << REG_FullRegName(INS_RegR(ins, i));
        if (i != INS_MaxNumRRegs(ins) - 1)
            outfile << " ";
    }
    outfile << "]" << "," << "W[";
    for (UINT32 i = 0; i < INS_MaxNumWRegs(ins); i++) 
    {
        outfile << REG_FullRegName(INS_RegW(ins, i));
        if (i != INS_MaxNumWRegs(ins) - 1)
            outfile << " ";
    }
    outfile << "]" << endl;
    counter++;
}

// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
    outfile << endl;
    cout << counter << endl;
}

// argc, argv are the entire command line, including pin -t <toolname> -- ...
int main(int argc, char * argv[])
{
    // Initialize pin
    PIN_Init(argc, argv);
	
    outfile.open(KnobOutputFile.Value().c_str());
    outfile << "Address,Opcode,Category,isBranch,isControlFlow,isMemoryRead,isMemoryWrite,isCall,Read_Regsiters,Write_Registers" << endl;

    // Register Instruction to be called to instrument instructions
    INS_AddInstrumentFunction(Instruction, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);

    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}
