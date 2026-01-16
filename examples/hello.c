#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// === Kapila Runtime ===

typedef enum { VAL_INT, VAL_FLOAT, VAL_BOOL, VAL_STR } ValueType;

typedef struct {
    ValueType type;
    union {
        long long i;
        double f;
        bool b;
        char* s;
    };
} Value;

#define STACK_SIZE 1024
Value stack[STACK_SIZE];
int sp = 0;

void stack_init() { sp = 0; }

void push_int(long long n) {
    stack[sp].type = VAL_INT;
    stack[sp].i = n;
    sp++;
}

void push_float(double n) {
    stack[sp].type = VAL_FLOAT;
    stack[sp].f = n;
    sp++;
}

void push_bool(bool b) {
    stack[sp].type = VAL_BOOL;
    stack[sp].b = b;
    sp++;
}

void push_str(char* s) {
    stack[sp].type = VAL_STR;
    stack[sp].s = s;
    sp++;
}

Value pop() { return stack[--sp]; }
Value peek() { return stack[sp-1]; }

// Arithmetic
void add_op() {
    Value b = pop(), a = pop();
    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT)
        push_float((a.type == VAL_FLOAT ? a.f : a.i) + (b.type == VAL_FLOAT ? b.f : b.i));
    else push_int(a.i + b.i);
}

void sub_op() {
    Value b = pop(), a = pop();
    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT)
        push_float((a.type == VAL_FLOAT ? a.f : a.i) - (b.type == VAL_FLOAT ? b.f : b.i));
    else push_int(a.i - b.i);
}

void mul_op() {
    Value b = pop(), a = pop();
    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT)
        push_float((a.type == VAL_FLOAT ? a.f : a.i) * (b.type == VAL_FLOAT ? b.f : b.i));
    else push_int(a.i * b.i);
}

void div_op() {
    Value b = pop(), a = pop();
    double av = a.type == VAL_FLOAT ? a.f : a.i;
    double bv = b.type == VAL_FLOAT ? b.f : b.i;
    push_float(av / bv);
}

void mod_op() {
    Value b = pop(), a = pop();
    push_int(a.i % b.i);
}

// Comparison
void lt_op() { Value b = pop(), a = pop(); push_bool(a.i < b.i); }
void gt_op() { Value b = pop(), a = pop(); push_bool(a.i > b.i); }
void eq_op() { Value b = pop(), a = pop(); push_bool(a.i == b.i); }
void neq_op() { Value b = pop(), a = pop(); push_bool(a.i != b.i); }
void lte_op() { Value b = pop(), a = pop(); push_bool(a.i <= b.i); }
void gte_op() { Value b = pop(), a = pop(); push_bool(a.i >= b.i); }

// Logic
void and_op() { Value b = pop(), a = pop(); push_bool(a.b && b.b); }
void or_op() { Value b = pop(), a = pop(); push_bool(a.b || b.b); }
void not_op() { Value a = pop(); push_bool(!a.b); }

// Stack ops
void dup_op() { Value a = peek(); stack[sp++] = a; }
void drop_op() { sp--; }
void swap_op() { Value b = pop(), a = pop(); stack[sp++] = b; stack[sp++] = a; }

// Print
void print_op() {
    Value v = pop();
    switch(v.type) {
        case VAL_INT: printf("%lld\n", v.i); break;
        case VAL_FLOAT: printf("%g\n", v.f); break;
        case VAL_BOOL: printf("%s\n", v.b ? "ಸರಿ" : "ತಪ್ಪು"); break;
        case VAL_STR: printf("%s\n", v.s); break;
    }
}

// === Generated Code ===

void word_ವರ_ccd_ಗ() {
    dup_op();
    mul_op();
}

int main() {
    stack_init();
    
    push_int(5);
    push_int(3);
    add_op();
    print_op();
    push_int(10);
    push_int(4);
    sub_op();
    print_op();
    push_int(6);
    push_int(7);
    mul_op();
    print_op();
    push_int(5);
    word_ವರ_ccd_ಗ();
    print_op();
    push_str("ನಮಸ್ಕಾರ ಪ್ರಪಂಚ!");
    print_op();
    
    return 0;
}