/*
 * Kapila Runtime Library
 * ಕಪಿಲ - A Kannada Programming Language
 */

#ifndef KAPILA_H
#define KAPILA_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

/* ============================================================
 * Value Types
 * ============================================================ */

typedef enum {
    VAL_INT,
    VAL_FLOAT,
    VAL_BOOL,
    VAL_STR,
    VAL_LIST
} ValueType;

/* Forward declaration */
typedef struct KList KList;

typedef struct {
    ValueType type;
    union {
        int64_t i;      /* ಪೂರ್ಣಾಂಕ - integer */
        double f;       /* ದಶಮಾಂಶ - float */
        bool b;         /* ಬೂಲ್ - boolean */
        char* s;        /* ಪಠ್ಯ - string */
        KList* list;    /* ಪಟ್ಟಿ - list */
    };
} Value;

/* List structure */
struct KList {
    Value* items;
    int len;
    int cap;
};

/* ============================================================
 * Runtime Initialization
 * ============================================================ */

void kapila_init(void);
void kapila_cleanup(void);

/* ============================================================
 * Stack Operations
 * ============================================================ */

#define STACK_SIZE 1024

extern Value stack[STACK_SIZE];
extern int sp;

void push_int(int64_t n);
void push_float(double n);
void push_bool(bool b);
void push_str(const char* s);
void push_list(KList* list);
void push_value(Value v);

Value pop(void);
Value peek(void);

/* ============================================================
 * Arithmetic Operations - ಅಂಕಗಣಿತ
 * ============================================================ */

void add_op(void);      /* + ಕೂಡು */
void sub_op(void);      /* - ಕಳೆ */
void mul_op(void);      /* * ಗುಣಿಸು */
void div_op(void);      /* / ಭಾಗಿಸು */
void mod_op(void);      /* % ಶೇಷ */

/* ============================================================
 * Comparison Operations - ಹೋಲಿಕೆ
 * ============================================================ */

void lt_op(void);       /* < ಕಿರಿದು */
void gt_op(void);       /* > ಹಿರಿದು */
void eq_op(void);       /* = ಸಮ */
void neq_op(void);      /* != ಸಮನಲ್ಲ */
void lte_op(void);      /* <= */
void gte_op(void);      /* >= */

/* ============================================================
 * Logic Operations - ತರ್ಕ
 * ============================================================ */

void and_op(void);      /* ಮತ್ತು */
void or_op(void);       /* ಅಥವಾ */
void not_op(void);      /* ಅಲ್ಲ */

/* ============================================================
 * Stack Manipulation - ರಾಶಿ ನಿರ್ವಹಣೆ
 * ============================================================ */

void dup_op(void);      /* ನಕಲು - duplicate top */
void drop_op(void);     /* ಬಿಡು - discard top */
void swap_op(void);     /* ಅದಲುಬದಲು - swap top two */
void over_op(void);     /* ಮೇಲೆ - copy second to top */
void rot_op(void);      /* ತಿರುಗಿಸು - rotate top three */

/* ============================================================
 * String Operations - ಪಠ್ಯ ಕಾರ್ಯಗಳು
 * ============================================================ */

void str_len_op(void);      /* ಉದ್ದ - string length */
void str_concat_op(void);   /* string concatenation */
void str_at_op(void);       /* character at index */

/* ============================================================
 * List Operations - ಪಟ್ಟಿ ಕಾರ್ಯಗಳು
 * ============================================================ */

KList* list_new(void);
void list_free(KList* list);
void list_push_item(KList* list, Value v);

void list_new_op(void);     /* create empty list */
void list_push_op(void);    /* ಸೇರಿಸು - append to list */
void list_len_op(void);     /* ಉದ್ದ - list length */
void list_at_op(void);      /* ತೆಗೆ - get item at index */
void list_first_op(void);   /* ಮೊದಲ - first item */
void list_rest_op(void);    /* ಉಳಿದ - all but first */

/* ============================================================
 * I/O Operations - ಇನ್‌ಪುಟ್/ಔಟ್‌ಪುಟ್
 * ============================================================ */

void print_op(void);        /* ಮುದ್ರಿಸು - print value */
void println_op(void);      /* print with newline */
void file_read_op(void);    /* ಓದು - read file */
void file_write_op(void);   /* ಬರೆ - write file */

/* ============================================================
 * Memory Management - ಸ್ಮೃತಿ ನಿರ್ವಹಣೆ
 * ============================================================ */

char* kapila_strdup(const char* s);
void* kapila_alloc(size_t size);

#endif /* KAPILA_H */
