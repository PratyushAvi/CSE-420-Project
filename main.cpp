#include <iostream>
#include <fstream> 
#include <stdio.h>
#include <assert.h>
#include <math.h>
#include "pin.H"
#include <set>
#include <map>
#include <deque>

using namespace std;
// This knob will set the outfile name
KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
			    "o", "results.out", "specify optional output file name");

UINT64 counter = 0;
ofstream outfile;

struct Node {
    UINT64 ins_number;
    bool marked;
    set<Node*> children; 
};

map<UINT64, Node*> graph;
map<UINT32, Node*> w_history_reg;
map<UINT32, Node*> w_history_mem;
set<Node*> branch_ins;
UINT64 control_flow = 0;

void docount() 
{
    counter++;
    outfile << counter << endl;
    Node* node = new Node;
    node->ins_number = counter;
    node->marked = false;
    graph[counter] = node;
}

void readReg(UINT32 r_reg)
{

    map<UINT32, Node*>::iterator it = w_history_reg.find(r_reg);
    if (it != w_history_reg.end())
    {
        Node* dep_ins = it->second;
        Node* node = graph.find(counter)->second;
        node->children.insert(dep_ins);
     
        // Node* dep_ins = it->second;
        // map<UINT64, Node*>::iterator it2 = graph.find(counter);
        // if (it2 != graph.end())
        // {
        //     Node* node = it2->second;
        //     node->children.insert(dep_ins);
        // }
    }
}

void readMem(UINT32 r_addr)
{
    map<UINT32, Node*>::iterator it = w_history_mem.find(r_addr);
    if (it != w_history_mem.end())
    {
        Node* dep_ins = it->second;
        Node* node = graph.find(counter)->second;
        node->children.insert(dep_ins);

        // Node* dep_ins = it->second;
        // map<UINT64, Node*>::iterator it2 = graph.find(counter);
        // if (it2 != graph.end())
        // {
        //     Node* node = it2->second;
        //     node->children.insert(dep_ins);
        // }
    }
}

void writeReg(UINT32 w_reg)
{
    // map<UINT64, Node*>::iterator it = graph.find(counter);
    // if (it != graph.end())
    //     w_history_reg[w_reg] = it->second;

    w_history_reg[w_reg] = graph.find(counter)->second;
}

void writeMem(UINT32 w_addr)
{
    // map<UINT64, Node*>::iterator it = graph.find(counter);
    // if (it != graph.end())
        // w_history_mem[w_addr] = it->second;
    w_history_mem[w_addr] = graph.find(counter)->second;
}

void isBranchINS()
{
    // Node* branch_node = graph.find(counter);
    // if (branch_node == graph.end())
    //     return;

    Node* branch_node = graph.find(counter)->second;
    branch_ins.insert(branch_node);
    deque<Node*> dq;
    dq.push_back(branch_node);

    while (!dq.empty())
    {
        Node* node = dq.front();
        dq.pop_front();
        if (!node->marked)
        {
            node->marked = true;
            control_flow++;
        }
        for (Node* v: node->children)
        {
            if (!v->marked)
                dq.push_back(v);
        }
    }
}

// Pin calls this function every time a new instruction is encountered
VOID Instruction(INS ins, VOID *v)
{
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, IARG_END);
    
    // HANDLE ALL READS AND WRITES
    for (UINT32 i = 0; i < INS_MaxNumRRegs(ins); i++) 
    {
        INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)readReg, IARG_UINT32, REG_FullRegName(INS_RegR(ins, i)), IARG_END);
    }
    for (UINT32 memOps = 0; memOps < INS_MemoryOperandCount(ins); memOps++)
    {   
        UINT32 n = INS_MemoryOperandIndexToOperandIndex(ins, memOps);
        UINT32 fulladdr = INS_OperandMemoryDisplacement(ins, n) 
            + INS_OperandMemoryBaseReg(ins, n) 
            + INS_OperandMemoryIndexReg(ins, n) 
            * INS_OperandMemoryScale(ins, n);

        if (INS_MemoryOperandIsRead(ins, memOps))
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)readMem, IARG_UINT32, fulladdr, IARG_END);
        
        if (INS_MemoryOperandIsWritten(ins, memOps))
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)writeMem, IARG_UINT32, fulladdr, IARG_END);
    }
    for (UINT32 i = 0; i < INS_MaxNumWRegs(ins); i++) 
    {
        INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)writeReg, IARG_UINT32, REG_FullRegName(INS_RegW(ins, i)), IARG_END);
    }

    if (INS_IsBranch(ins))
    {
        INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)isBranchINS, IARG_END);
    }
}

// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
    outfile << endl;
    cout << "INS_COUNT: " << counter << endl;
    cout << "Control-Flow: " << control_flow << " " << float(control_flow)/counter << "%" << endl;
    outfile.close();
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