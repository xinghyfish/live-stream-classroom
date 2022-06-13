#include <stdio.h>
#include <stdlib.h>

#define MemERR() perror("[Memery Error]NO ENOUGH SPACE\n")
#define AccessERR() perror("[Memory Error]MEMORY ACESS ERROR\n")
#define DUMB -1
#define ALLOC 0
#define RECLM 1

struct Block {
    int address;
    int size;
    struct Block *front;
    struct Block *next;
};

struct Table {
    struct Block* head;
    int size;
};

struct Table *unallocTable, *allocTable;
struct Block* (*AllocMenFunc[3])(int);

/* function table */
/* assistant functions */
int isEmpty(struct Table *table);
struct Block* Init(int size, int address);
void PrintTable(struct Table *table);
void AllocOperation(int opt);
void ReclaimOperation();
/* algorithms */
struct Block* FirstFit(int size);
struct Block* BestFit(int size);
struct Block* WorstFit(int size);
void TableInsert(struct Block *block, int type);
int AllocMem(int size, int opt);
void ReclaimMem(int address, int size);
void Combine(struct Block *block);

/* functions start here */
/* return true if the table is empty */
int isEmpty(struct Table *table) 
{
    return table->size == 0;
}

/* initialie a block */
struct Block* Init(int size, int address)
{
    struct Block *block;
    block = (struct Block*)malloc(sizeof(struct Block));
    block->front = NULL;
    block->next = NULL;
    block->size = size;
    block->address = address;
} 

/* insert a block into Table */
void TableInsert(struct Block *block, int type) 
{
    struct Table *table;
    if (type == ALLOC) table = allocTable;
    else table = unallocTable;

    int index = 0;
    if (isEmpty(table)) {   // no previous node
        block->front = table->head;
        table->head->next = block;
        table->size++;
    }
    else {
        struct Block *preBlock = table->head;
        while (preBlock->next != NULL && preBlock->next->address < block->address)
            preBlock = preBlock->next;
        // find previous node, insert node into the list
        block->next = preBlock->next;
        if (preBlock->next != NULL) preBlock->next->front = block;
        preBlock->next = block;
        block->front = preBlock;
        table->size++;  // length increment

        struct Block* tempBlock = block->next;
        while (tempBlock != NULL)
            tempBlock = tempBlock->next;
        if (type == RECLM)
            Combine(block);
    }
}

/* First-Fit Algorithm to find the unallocated memory block. */
struct Block* FirstFit(int size) 
{
    struct Block* block = unallocTable->head;
    // seek for the suitable block
    while (block != NULL) {
        if (block->size >= size)
            break;
        block = block->next;
    }

    return block;
}

/* Best-Fit Algorithm to find the unallocated memory block. */
struct Block* BestFit(int size) 
{
    struct Block* block = unallocTable->head;
    struct Block* candidate = Init(__INT32_MAX__, -1);
    // seek for the smallest suitable block
    while (block != NULL) {
        if (block->size >= size && block->size < candidate->size)
            candidate = block;
        block = block->next;
    }

    if (candidate->size == __INT32_MAX__)
        return NULL;
    else return candidate;
}

/* Worst-Fit Algorithm to find the unallocated memory. */
struct Block* WorstFit(int size) 
{
    struct Block* block = unallocTable->head;
    struct Block* candidate = Init(0, -1);
    // seek for the biggest suitable block
    while (block != NULL) {
        if (block->size >= size && block->size > candidate->size)
            candidate = block;
        block = block->next;
    }

    if (candidate->size == 0)
        return NULL;
    else return candidate;
}

/* Combine unallocated memory block in succession to a whole block. */
void Combine(struct Block *block)
{
    struct Block *preBlock = block->front, *nextBlock = block->next;
    if (preBlock->address + preBlock->size == block->address)
    {   // adjacent to front block ==> combine
        block->address = preBlock->address;
        block->size += preBlock->size;
        preBlock->front->next = block;
        block->front = preBlock->front;
        // delete prevoid node
        free(preBlock);
        unallocTable->size--;
    }
    if (nextBlock != NULL && block->address + block->size == nextBlock->address)
    {   // adjacent to next block
        block->size += nextBlock->size;
        block->next = nextBlock->next;
        if (nextBlock->next != NULL) nextBlock->next->front = block;
        // delete next node
        free(nextBlock);
        unallocTable->size--;
        block = block->next;

        while (block != NULL) { // update index of nodes behind
            block = block->next;
        }
    }
}

/* Apply different algorithm to allocate memory. */
int AllocMem(int size, int opt)
{
    int address = -1;
    struct Block* block = AllocMenFunc[opt](size);

    // no enough space
    if (block == NULL) {
        MemERR();
        return address;
    }
    // same size as block
    else if (block->size == size) {
        // delete node from list
        struct Block *preBlock = block->front;
        preBlock->next = block->next;
        if (block->next) block->next->front = preBlock;
        TableInsert(block, ALLOC);
        address = block->address;
        unallocTable->size--;
    }
    else {
        // update date of block and creae a new block
        address = block->address + block->size - size;
        struct Block *allocBlock = Init(size, address);
        block->size -= size;
        TableInsert(allocBlock, ALLOC);
    }

    return address;
}

/* Allocate memory by algorithm code opt. */
void AllocOperation(int opt)
{
    int size, address;
    /* invalid code */
    if (opt < 0 || opt > 2) {
        printf("Wrong Algorithm Code!\n");
        return;
    }

    printf("Input application:\n");
    scanf("%d", &size);
    getchar();
    address = AllocMem(size, opt);
    if (address != -1) 
        printf("Allocation Success! ADDRESS = %d\n", address);
    
    PrintTable(unallocTable);
    PrintTable(allocTable);
}

/* Reclaim memory by starting address and block size. */
void ReclaimMem(int address, int size)
{
    if (isEmpty(allocTable)) {
        AccessERR();
        return;
    }

    struct Block *block = allocTable->head;
    while (block != NULL) {
        // find the block
        if (address == block->address && size == block->size)
            break;
        block = block->next;
    }
    if (block == NULL) { // block not found
        AccessERR();
        return;
    }
    // delete node from the list
    block->front->next = block->next;
    if (block->next != NULL) block->next->front = block->front;
    struct Block* temp = block;
    while (temp != NULL) {  // update index of nodes behind
        temp = temp->next;
    }
    allocTable->size--;
    TableInsert(block, RECLM);
}

/* Recalim memory. */
void ReclaimOperation()
{
    int size, address;

    printf("Input address and size:\n");
    scanf("%d%d", &address, &size);
    getchar();
    ReclaimMem(address, size);
    
    PrintTable(unallocTable);
    PrintTable(allocTable);
}

/* Print specific table. */
void PrintTable(struct Table* table)
{
    if (table == unallocTable)
        printf("*********Unallocated Table**********\n");
    else if (table == allocTable)
        printf("***********Allocated Table**********\n");
    if (!isEmpty(table))
    {
        printf("index****address****end*****size****\n");
        printf("------------------------------------\n");
        struct Block *block = table->head;
        int index = 0;
        while (block->next != NULL)
        {
            block = block->next;
            printf("%-9d%-11d%-8d%-7d\n", 
                index++, block->address, block->address + block->size - 1, block->size);
            printf("------------------------------------\n");
        }
        printf("\n");
    }
    else printf("%12sEmpty Table!%-12s\n", "[", "]");
}

int main(int argc, char const *argv[])
{
    // init two main tables
    unallocTable = (struct Table*)malloc(sizeof(struct Table));
    allocTable = (struct Table*)malloc(sizeof(struct Table));

    // table: head->block0->block1->...
    struct Block* unallocHead, *allocHead;
    unallocHead = Init(DUMB, DUMB);
    allocHead = Init(DUMB, DUMB);
    unallocTable->head = unallocHead;
    allocTable->head = allocHead;
    allocTable->size = 0;

    // init memory
    struct Block* initBlock;
    initBlock = Init(640, 0);
    unallocHead->next = initBlock;
    initBlock->front = unallocHead;
    unallocTable->size = 1;
    // init allocation algorithm
    AllocMenFunc[0] = FirstFit; 
    AllocMenFunc[1] = BestFit;
    AllocMenFunc[2] = WorstFit;
    // print 2 tables
    PrintTable(unallocTable);
    // run
    char command;
    int opt;
    while (1) {
        printf("Enter the allocate or reclaim (a/r), or press other key to exit.\n");
        scanf("%c", &command);
        getchar();
        switch (command)
        {
        case 'a':   // allocation
            printf("allocation algproithm(0: First Fit; 1: Best Fit; 2: Worst Fit): \n");
            scanf("%d", &opt);
            getchar();
            AllocOperation(opt);
            break;
        case 'r':   // reclaim
            ReclaimOperation();
            break;
        default:    // none, break
            exit(0);
        }
    }

    return 0;
}
