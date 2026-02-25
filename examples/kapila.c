/*
 * Kapila Runtime Library Implementation
 * ಕಪಿಲ - A Kannada Programming Language
 */

#include "kapila.h"

/* ============================================================
 * Global State
 * ============================================================ */

Value stack[STACK_SIZE];
int sp = 0;

/* Memory tracking for cleanup */
#define MAX_ALLOCS 4096
static void* allocations[MAX_ALLOCS];
static int alloc_count = 0;

/* ============================================================
 * Runtime Initialization
 * ============================================================ */

void kapila_init(void) {
    sp = 0;
    alloc_count = 0;
}

void kapila_cleanup(void) {
    for (int i = 0; i < alloc_count; i++) {
        free(allocations[i]);
    }
    alloc_count = 0;
    sp = 0;
}

/* ============================================================
 * Memory Management
 * ============================================================ */

void* kapila_alloc(size_t size) {
    void* ptr = malloc(size);
    if (ptr && alloc_count < MAX_ALLOCS) {
        allocations[alloc_count++] = ptr;
    }
    return ptr;
}

char* kapila_strdup(const char* s) {
    size_t len = strlen(s) + 1;
    char* copy = (char*)kapila_alloc(len);
    if (copy) {
        memcpy(copy, s, len);
    }
    return copy;
}

/* ============================================================
 * Stack Operations
 * ============================================================ */

void push_int(int64_t n) {
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

void push_str(const char* s) {
    stack[sp].type = VAL_STR;
    stack[sp].s = (char*)s;  /* String literals are not copied */
    sp++;
}

void push_list(KList* list) {
    stack[sp].type = VAL_LIST;
    stack[sp].list = list;
    sp++;
}

void push_value(Value v) {
    stack[sp++] = v;
}

Value pop(void) {
    return stack[--sp];
}

Value peek(void) {
    return stack[sp - 1];
}

/* ============================================================
 * Helper: Get numeric value as double
 * ============================================================ */

static double as_number(Value v) {
    if (v.type == VAL_FLOAT) return v.f;
    if (v.type == VAL_INT) return (double)v.i;
    return 0.0;
}

static bool is_numeric(Value v) {
    return v.type == VAL_INT || v.type == VAL_FLOAT;
}

/* ============================================================
 * Arithmetic Operations
 * ============================================================ */

void add_op(void) {
    Value b = pop(), a = pop();
    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
        push_float(as_number(a) + as_number(b));
    } else {
        push_int(a.i + b.i);
    }
}

void sub_op(void) {
    Value b = pop(), a = pop();
    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
        push_float(as_number(a) - as_number(b));
    } else {
        push_int(a.i - b.i);
    }
}

void mul_op(void) {
    Value b = pop(), a = pop();
    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
        push_float(as_number(a) * as_number(b));
    } else {
        push_int(a.i * b.i);
    }
}

void div_op(void) {
    Value b = pop(), a = pop();
    push_float(as_number(a) / as_number(b));
}

void mod_op(void) {
    Value b = pop(), a = pop();
    push_int(a.i % b.i);
}

/* ============================================================
 * Comparison Operations (now work with floats!)
 * ============================================================ */

void lt_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b)) {
        push_bool(as_number(a) < as_number(b));
    } else {
        push_bool(a.i < b.i);
    }
}

void gt_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b)) {
        push_bool(as_number(a) > as_number(b));
    } else {
        push_bool(a.i > b.i);
    }
}

void eq_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b)) {
        push_bool(as_number(a) == as_number(b));
    } else if (a.type == VAL_STR && b.type == VAL_STR) {
        push_bool(strcmp(a.s, b.s) == 0);
    } else if (a.type == VAL_BOOL && b.type == VAL_BOOL) {
        push_bool(a.b == b.b);
    } else {
        push_bool(a.i == b.i);
    }
}

void neq_op(void) {
    eq_op();
    not_op();
}

void lte_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b)) {
        push_bool(as_number(a) <= as_number(b));
    } else {
        push_bool(a.i <= b.i);
    }
}

void gte_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b)) {
        push_bool(as_number(a) >= as_number(b));
    } else {
        push_bool(a.i >= b.i);
    }
}

/* ============================================================
 * Logic Operations
 * ============================================================ */

void and_op(void) {
    Value b = pop(), a = pop();
    push_bool(a.b && b.b);
}

void or_op(void) {
    Value b = pop(), a = pop();
    push_bool(a.b || b.b);
}

void not_op(void) {
    Value a = pop();
    push_bool(!a.b);
}

/* ============================================================
 * Stack Manipulation
 * ============================================================ */

void dup_op(void) {
    Value a = peek();
    push_value(a);
}

void drop_op(void) {
    sp--;
}

void swap_op(void) {
    Value b = pop(), a = pop();
    push_value(b);
    push_value(a);
}

void over_op(void) {
    /* Copy second item to top: a b -- a b a */
    Value b = pop(), a = pop();
    push_value(a);
    push_value(b);
    push_value(a);
}

void rot_op(void) {
    /* Rotate top three: a b c -- b c a */
    Value c = pop(), b = pop(), a = pop();
    push_value(b);
    push_value(c);
    push_value(a);
}

/* ============================================================
 * String Operations
 * ============================================================ */

void str_len_op(void) {
    Value v = pop();
    if (v.type == VAL_STR) {
        /* Count UTF-8 characters, not bytes */
        const char* s = v.s;
        int len = 0;
        while (*s) {
            /* Skip continuation bytes (10xxxxxx) */
            if ((*s & 0xC0) != 0x80) len++;
            s++;
        }
        push_int(len);
    } else {
        push_int(0);
    }
}

void str_concat_op(void) {
    Value b = pop(), a = pop();
    if (a.type == VAL_STR && b.type == VAL_STR) {
        size_t len_a = strlen(a.s);
        size_t len_b = strlen(b.s);
        char* result = (char*)kapila_alloc(len_a + len_b + 1);
        strcpy(result, a.s);
        strcat(result, b.s);
        push_str(result);
    } else {
        push_str("");
    }
}

void str_at_op(void) {
    Value idx = pop();
    Value str = pop();
    if (str.type == VAL_STR && idx.type == VAL_INT) {
        /* Get UTF-8 character at index */
        const char* s = str.s;
        int target = (int)idx.i;
        int pos = 0;

        while (*s && pos < target) {
            if ((*s & 0xC0) != 0x80) pos++;
            s++;
        }

        if (*s) {
            /* Find length of this UTF-8 character */
            int char_len = 1;
            if ((*s & 0xF0) == 0xF0) char_len = 4;
            else if ((*s & 0xE0) == 0xE0) char_len = 3;
            else if ((*s & 0xC0) == 0xC0) char_len = 2;

            char* result = (char*)kapila_alloc(char_len + 1);
            memcpy(result, s, char_len);
            result[char_len] = '\0';
            push_str(result);
        } else {
            push_str("");
        }
    } else {
        push_str("");
    }
}

/* ============================================================
 * List Operations
 * ============================================================ */

KList* list_new(void) {
    KList* list = (KList*)kapila_alloc(sizeof(KList));
    list->items = (Value*)kapila_alloc(sizeof(Value) * 8);
    list->len = 0;
    list->cap = 8;
    return list;
}

void list_free(KList* list) {
    /* Memory tracked by kapila_alloc, freed in cleanup */
}

void list_push_item(KList* list, Value v) {
    if (list->len >= list->cap) {
        int new_cap = list->cap * 2;
        Value* new_items = (Value*)kapila_alloc(sizeof(Value) * new_cap);
        memcpy(new_items, list->items, sizeof(Value) * list->len);
        list->items = new_items;
        list->cap = new_cap;
    }
    list->items[list->len++] = v;
}

void list_new_op(void) {
    push_list(list_new());
}

void list_push_op(void) {
    Value item = pop();
    Value list_val = pop();
    if (list_val.type == VAL_LIST) {
        list_push_item(list_val.list, item);
        push_list(list_val.list);
    }
}

void list_len_op(void) {
    Value v = pop();
    if (v.type == VAL_LIST) {
        push_int(v.list->len);
    } else if (v.type == VAL_STR) {
        /* Also works for strings */
        push_str(v.s);
        str_len_op();
    } else {
        push_int(0);
    }
}

void list_at_op(void) {
    Value idx = pop();
    Value list_val = pop();
    if (list_val.type == VAL_LIST && idx.type == VAL_INT) {
        int i = (int)idx.i;
        if (i >= 0 && i < list_val.list->len) {
            push_value(list_val.list->items[i]);
        } else {
            push_int(0);  /* Out of bounds */
        }
    } else {
        push_int(0);
    }
}

void list_first_op(void) {
    Value list_val = pop();
    if (list_val.type == VAL_LIST && list_val.list->len > 0) {
        push_value(list_val.list->items[0]);
    } else {
        push_int(0);
    }
}

void list_rest_op(void) {
    Value list_val = pop();
    if (list_val.type == VAL_LIST && list_val.list->len > 1) {
        KList* rest = list_new();
        for (int i = 1; i < list_val.list->len; i++) {
            list_push_item(rest, list_val.list->items[i]);
        }
        push_list(rest);
    } else {
        push_list(list_new());
    }
}

/* ============================================================
 * I/O Operations
 * ============================================================ */

void print_op(void) {
    Value v = pop();
    switch (v.type) {
        case VAL_INT:
            printf("%lld", (long long)v.i);
            break;
        case VAL_FLOAT:
            printf("%g", v.f);
            break;
        case VAL_BOOL:
            printf("%s", v.b ? "\xe0\xb2\xb8\xe0\xb2\xb0\xe0\xb2\xbf" :
                              "\xe0\xb2\xa4\xe0\xb2\xaa\xe0\xb3\x8d\xe0\xb2\xaa\xe0\xb3\x81");
            /* ಸರಿ / ತಪ್ಪು in UTF-8 */
            break;
        case VAL_STR:
            printf("%s", v.s);
            break;
        case VAL_LIST:
            printf("[");
            for (int i = 0; i < v.list->len; i++) {
                if (i > 0) printf(" ");
                push_value(v.list->items[i]);
                print_op();
            }
            printf("]");
            break;
    }
}

void println_op(void) {
    print_op();
    printf("\n");
}

void file_read_op(void) {
    Value filename = pop();
    if (filename.type != VAL_STR) {
        push_str("");
        return;
    }

    FILE* f = fopen(filename.s, "rb");
    if (!f) {
        push_str("");
        return;
    }

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    char* content = (char*)kapila_alloc(size + 1);
    fread(content, 1, size, f);
    content[size] = '\0';
    fclose(f);

    push_str(content);
}

void file_write_op(void) {
    Value content = pop();
    Value filename = pop();

    if (filename.type != VAL_STR || content.type != VAL_STR) {
        push_bool(false);
        return;
    }

    FILE* f = fopen(filename.s, "wb");
    if (!f) {
        push_bool(false);
        return;
    }

    fputs(content.s, f);
    fclose(f);
    push_bool(true);
}
