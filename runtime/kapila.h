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
#include <math.h>
#include <ctype.h>

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
        int64_t i;      /* integer */
        double f;       /* float */
        bool b;         /* boolean */
        char* s;        /* string */
        KList* list;    /* list */
    };
} Value;

/* List structure */
struct KList {
    Value* items;
    int len;
    int cap;
};

/* Block function pointer for higher-order operations */
typedef void (*KBlock)(void);

/* ============================================================
 * Runtime Initialization
 * ============================================================ */

void kapila_init(void);
void kapila_init_args(int argc, char** argv);
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
bool pop_bool(void);

/* ============================================================
 * Arithmetic Operations
 * ============================================================ */

void add_op(void);
void sub_op(void);
void mul_op(void);
void div_op(void);
void mod_op(void);

/* ============================================================
 * Math Operations
 * ============================================================ */

void abs_op(void);
void min_op(void);
void max_op(void);
void pow_op(void);
void sqrt_op(void);
void floor_op(void);
void ceil_op(void);
void round_op(void);

/* ============================================================
 * Comparison Operations
 * ============================================================ */

void lt_op(void);
void gt_op(void);
void eq_op(void);
void neq_op(void);
void lte_op(void);
void gte_op(void);

/* ============================================================
 * Logic Operations
 * ============================================================ */

void and_op(void);
void or_op(void);
void not_op(void);

/* ============================================================
 * Stack Manipulation
 * ============================================================ */

void dup_op(void);
void drop_op(void);
void swap_op(void);
void over_op(void);
void rot_op(void);

/* ============================================================
 * String Operations
 * ============================================================ */

void str_len_op(void);
void str_concat_op(void);
void str_at_op(void);
void str_split_op(void);
void str_join_op(void);
void str_substring_op(void);
void str_find_op(void);
void str_replace_op(void);
void str_trim_op(void);
void str_upper_op(void);
void str_lower_op(void);
void str_starts_with_op(void);
void str_ends_with_op(void);
void str_contains_op(void);

/* ============================================================
 * List Operations
 * ============================================================ */

KList* list_new(void);
void list_free(KList* list);
void list_push_item(KList* list, Value v);
KList* list_copy(KList* src);

void list_new_op(void);
void list_push_op(void);
void list_len_op(void);
void list_at_op(void);
void list_first_op(void);
void list_rest_op(void);
void list_last_op(void);
void list_reverse_op(void);
void list_sort_op(void);
void list_is_empty_op(void);
void list_concat_op(void);
void list_take_op(void);
void list_drop_items_op(void);
void list_contains_op(void);
void list_index_of_op(void);
void range_op(void);
void iota_op(void);

/* ============================================================
 * Higher-Order Operations (block-based)
 * ============================================================ */

void map_block_op(KBlock fn);
void filter_block_op(KBlock fn);
void fold_block_op(KBlock fn);
void each_block_op(KBlock fn);
void times_block_op(KBlock fn);
void while_block_op(KBlock cond, KBlock body);
void until_block_op(KBlock cond, KBlock body);
void if_block_op(KBlock then_fn);
void ifelse_block_op(KBlock then_fn, KBlock else_fn);
void do_block_op(KBlock fn);

/* ============================================================
 * Variable Storage
 * ============================================================ */

void var_set(const char* name, Value v);
Value var_get(const char* name);

/* ============================================================
 * Type Conversion
 * ============================================================ */

void to_string_op(void);
void to_int_op(void);
void to_float_op(void);

/* ============================================================
 * I/O Operations
 * ============================================================ */

void print_op(void);
void println_op(void);
void read_line_op(void);
void file_read_op(void);
void file_write_op(void);

/* ============================================================
 * CLI Arguments
 * ============================================================ */

void args_count_op(void);
void args_get_op(void);

/* ============================================================
 * Memory Management
 * ============================================================ */

char* kapila_strdup(const char* s);
void* kapila_alloc(size_t size);

#endif /* KAPILA_H */
