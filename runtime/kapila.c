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
#define MAX_ALLOCS 8192
static void* allocations[MAX_ALLOCS];
static int alloc_count = 0;

/* CLI arguments */
static int g_argc = 0;
static char** g_argv = NULL;

/* Variable storage */
#define MAX_VARS 256
typedef struct {
    char name[128];
    Value value;
} VarEntry;
static VarEntry variables[MAX_VARS];
static int var_count = 0;

/* ============================================================
 * Runtime Initialization
 * ============================================================ */

void kapila_init(void) {
    sp = 0;
    alloc_count = 0;
    var_count = 0;
}

void kapila_init_args(int argc, char** argv) {
    kapila_init();
    g_argc = argc;
    g_argv = argv;
}

void kapila_cleanup(void) {
    for (int i = 0; i < alloc_count; i++) {
        free(allocations[i]);
    }
    alloc_count = 0;
    sp = 0;
    var_count = 0;
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
    stack[sp].s = (char*)s;
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

bool pop_bool(void) {
    Value v = pop();
    switch (v.type) {
        case VAL_BOOL: return v.b;
        case VAL_INT:  return v.i != 0;
        case VAL_FLOAT: return v.f != 0.0;
        case VAL_STR:  return v.s != NULL && v.s[0] != '\0';
        case VAL_LIST: return v.list != NULL && v.list->len > 0;
    }
    return false;
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
    if (a.type == VAL_STR && b.type == VAL_STR) {
        /* String concatenation */
        size_t la = strlen(a.s), lb = strlen(b.s);
        char* r = (char*)kapila_alloc(la + lb + 1);
        strcpy(r, a.s);
        strcat(r, b.s);
        push_str(r);
    } else if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
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
 * Math Operations
 * ============================================================ */

void abs_op(void) {
    Value a = pop();
    if (a.type == VAL_FLOAT) push_float(fabs(a.f));
    else push_int(a.i < 0 ? -a.i : a.i);
}

void min_op(void) {
    Value b = pop(), a = pop();
    double na = as_number(a), nb = as_number(b);
    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT)
        push_float(na < nb ? na : nb);
    else
        push_int(a.i < b.i ? a.i : b.i);
}

void max_op(void) {
    Value b = pop(), a = pop();
    double na = as_number(a), nb = as_number(b);
    if (a.type == VAL_FLOAT || b.type == VAL_FLOAT)
        push_float(na > nb ? na : nb);
    else
        push_int(a.i > b.i ? a.i : b.i);
}

void pow_op(void) {
    Value b = pop(), a = pop();
    push_float(pow(as_number(a), as_number(b)));
}

void sqrt_op(void) {
    Value a = pop();
    push_float(sqrt(as_number(a)));
}

void floor_op(void) {
    Value a = pop();
    push_int((int64_t)floor(as_number(a)));
}

void ceil_op(void) {
    Value a = pop();
    push_int((int64_t)ceil(as_number(a)));
}

void round_op(void) {
    Value a = pop();
    push_int((int64_t)round(as_number(a)));
}

/* ============================================================
 * Comparison Operations
 * ============================================================ */

void lt_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b))
        push_bool(as_number(a) < as_number(b));
    else
        push_bool(a.i < b.i);
}

void gt_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b))
        push_bool(as_number(a) > as_number(b));
    else
        push_bool(a.i > b.i);
}

void eq_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b))
        push_bool(as_number(a) == as_number(b));
    else if (a.type == VAL_STR && b.type == VAL_STR)
        push_bool(strcmp(a.s, b.s) == 0);
    else if (a.type == VAL_BOOL && b.type == VAL_BOOL)
        push_bool(a.b == b.b);
    else
        push_bool(a.i == b.i);
}

void neq_op(void) {
    eq_op();
    not_op();
}

void lte_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b))
        push_bool(as_number(a) <= as_number(b));
    else
        push_bool(a.i <= b.i);
}

void gte_op(void) {
    Value b = pop(), a = pop();
    if (is_numeric(a) && is_numeric(b))
        push_bool(as_number(a) >= as_number(b));
    else
        push_bool(a.i >= b.i);
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
    Value b = pop(), a = pop();
    push_value(a);
    push_value(b);
    push_value(a);
}

void rot_op(void) {
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
        const char* s = v.s;
        int len = 0;
        while (*s) {
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
        size_t la = strlen(a.s), lb = strlen(b.s);
        char* r = (char*)kapila_alloc(la + lb + 1);
        strcpy(r, a.s);
        strcat(r, b.s);
        push_str(r);
    } else {
        push_str("");
    }
}

void str_at_op(void) {
    Value idx = pop();
    Value str_val = pop();
    if (str_val.type == VAL_STR && idx.type == VAL_INT) {
        const char* s = str_val.s;
        int target = (int)idx.i, pos = 0;
        while (*s && pos < target) {
            if ((*s & 0xC0) != 0x80) pos++;
            s++;
        }
        if (*s) {
            int char_len = 1;
            if ((*s & 0xF0) == 0xF0) char_len = 4;
            else if ((*s & 0xE0) == 0xE0) char_len = 3;
            else if ((*s & 0xC0) == 0xC0) char_len = 2;
            char* r = (char*)kapila_alloc(char_len + 1);
            memcpy(r, s, char_len);
            r[char_len] = '\0';
            push_str(r);
        } else {
            push_str("");
        }
    } else {
        push_str("");
    }
}

void str_split_op(void) {
    /* ( str delim -- list ) */
    Value delim = pop();
    Value str_val = pop();
    KList* result = list_new();
    if (str_val.type == VAL_STR && delim.type == VAL_STR) {
        char* s = kapila_strdup(str_val.s);
        const char* d = delim.s;
        size_t dlen = strlen(d);
        if (dlen == 0) {
            /* Split each character */
            const char* p = str_val.s;
            while (*p) {
                int clen = 1;
                if ((*p & 0xF0) == 0xF0) clen = 4;
                else if ((*p & 0xE0) == 0xE0) clen = 3;
                else if ((*p & 0xC0) == 0xC0) clen = 2;
                char* ch = (char*)kapila_alloc(clen + 1);
                memcpy(ch, p, clen);
                ch[clen] = '\0';
                Value v; v.type = VAL_STR; v.s = ch;
                list_push_item(result, v);
                p += clen;
            }
        } else {
            char* token = s;
            char* found;
            while ((found = strstr(token, d)) != NULL) {
                *found = '\0';
                Value v; v.type = VAL_STR; v.s = kapila_strdup(token);
                list_push_item(result, v);
                token = found + dlen;
            }
            Value v; v.type = VAL_STR; v.s = kapila_strdup(token);
            list_push_item(result, v);
        }
    }
    push_list(result);
}

void str_join_op(void) {
    /* ( list delim -- str ) */
    Value delim = pop();
    Value list_val = pop();
    if (list_val.type == VAL_LIST && delim.type == VAL_STR) {
        /* Calculate total length */
        size_t total = 0;
        size_t dlen = strlen(delim.s);
        for (int i = 0; i < list_val.list->len; i++) {
            Value item = list_val.list->items[i];
            if (item.type == VAL_STR) total += strlen(item.s);
            else total += 20; /* enough for numbers */
            if (i > 0) total += dlen;
        }
        char* r = (char*)kapila_alloc(total + 1);
        r[0] = '\0';
        for (int i = 0; i < list_val.list->len; i++) {
            if (i > 0) strcat(r, delim.s);
            Value item = list_val.list->items[i];
            if (item.type == VAL_STR) {
                strcat(r, item.s);
            } else if (item.type == VAL_INT) {
                char buf[32];
                sprintf(buf, "%lld", (long long)item.i);
                strcat(r, buf);
            } else if (item.type == VAL_FLOAT) {
                char buf[32];
                sprintf(buf, "%g", item.f);
                strcat(r, buf);
            }
        }
        push_str(r);
    } else {
        push_str("");
    }
}

void str_substring_op(void) {
    /* ( str start end -- substr ) */
    Value end_v = pop();
    Value start_v = pop();
    Value str_val = pop();
    if (str_val.type == VAL_STR) {
        int start = (int)start_v.i;
        int end = (int)end_v.i;
        int slen = (int)strlen(str_val.s);
        if (start < 0) start = 0;
        if (end > slen) end = slen;
        if (start >= end) {
            push_str("");
        } else {
            int len = end - start;
            char* r = (char*)kapila_alloc(len + 1);
            memcpy(r, str_val.s + start, len);
            r[len] = '\0';
            push_str(r);
        }
    } else {
        push_str("");
    }
}

void str_find_op(void) {
    /* ( str pattern -- index ) */
    Value pattern = pop();
    Value str_val = pop();
    if (str_val.type == VAL_STR && pattern.type == VAL_STR) {
        char* found = strstr(str_val.s, pattern.s);
        if (found) push_int((int64_t)(found - str_val.s));
        else push_int(-1);
    } else {
        push_int(-1);
    }
}

void str_replace_op(void) {
    /* ( str old new -- newstr ) */
    Value new_s = pop();
    Value old_s = pop();
    Value str_val = pop();
    if (str_val.type == VAL_STR && old_s.type == VAL_STR && new_s.type == VAL_STR) {
        const char* src = str_val.s;
        size_t old_len = strlen(old_s.s);
        size_t new_len = strlen(new_s.s);
        if (old_len == 0) {
            push_str(kapila_strdup(src));
            return;
        }
        /* Count occurrences */
        int count = 0;
        const char* p = src;
        while ((p = strstr(p, old_s.s)) != NULL) {
            count++;
            p += old_len;
        }
        size_t result_len = strlen(src) + count * ((int)new_len - (int)old_len);
        char* r = (char*)kapila_alloc(result_len + 1);
        char* dst = r;
        p = src;
        while (*p) {
            if (strncmp(p, old_s.s, old_len) == 0) {
                memcpy(dst, new_s.s, new_len);
                dst += new_len;
                p += old_len;
            } else {
                *dst++ = *p++;
            }
        }
        *dst = '\0';
        push_str(r);
    } else {
        push_str("");
    }
}

void str_trim_op(void) {
    /* ( str -- trimmed ) */
    Value v = pop();
    if (v.type == VAL_STR) {
        const char* start = v.s;
        while (*start && isspace((unsigned char)*start)) start++;
        const char* end = v.s + strlen(v.s) - 1;
        while (end > start && isspace((unsigned char)*end)) end--;
        size_t len = end - start + 1;
        char* r = (char*)kapila_alloc(len + 1);
        memcpy(r, start, len);
        r[len] = '\0';
        push_str(r);
    } else {
        push_str("");
    }
}

void str_upper_op(void) {
    Value v = pop();
    if (v.type == VAL_STR) {
        char* r = kapila_strdup(v.s);
        for (char* p = r; *p; p++) *p = (char)toupper((unsigned char)*p);
        push_str(r);
    } else {
        push_str("");
    }
}

void str_lower_op(void) {
    Value v = pop();
    if (v.type == VAL_STR) {
        char* r = kapila_strdup(v.s);
        for (char* p = r; *p; p++) *p = (char)tolower((unsigned char)*p);
        push_str(r);
    } else {
        push_str("");
    }
}

void str_starts_with_op(void) {
    Value prefix = pop();
    Value str_val = pop();
    if (str_val.type == VAL_STR && prefix.type == VAL_STR) {
        push_bool(strncmp(str_val.s, prefix.s, strlen(prefix.s)) == 0);
    } else {
        push_bool(false);
    }
}

void str_ends_with_op(void) {
    Value suffix = pop();
    Value str_val = pop();
    if (str_val.type == VAL_STR && suffix.type == VAL_STR) {
        size_t slen = strlen(str_val.s);
        size_t suflen = strlen(suffix.s);
        if (suflen > slen) {
            push_bool(false);
        } else {
            push_bool(strcmp(str_val.s + slen - suflen, suffix.s) == 0);
        }
    } else {
        push_bool(false);
    }
}

void str_contains_op(void) {
    Value substr = pop();
    Value str_val = pop();
    if (str_val.type == VAL_STR && substr.type == VAL_STR) {
        push_bool(strstr(str_val.s, substr.s) != NULL);
    } else {
        push_bool(false);
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

KList* list_copy(KList* src) {
    KList* dst = list_new();
    for (int i = 0; i < src->len; i++) {
        list_push_item(dst, src->items[i]);
    }
    return dst;
}

void list_new_op(void) {
    push_list(list_new());
}

void list_push_op(void) {
    /* ( list item -- newlist ) */
    Value item = pop();
    Value list_val = pop();
    if (list_val.type == VAL_LIST) {
        KList* result = list_copy(list_val.list);
        list_push_item(result, item);
        push_list(result);
    } else {
        push_list(list_new());
    }
}

void list_len_op(void) {
    Value v = pop();
    if (v.type == VAL_LIST) {
        push_int(v.list->len);
    } else if (v.type == VAL_STR) {
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
        if (i >= 0 && i < list_val.list->len)
            push_value(list_val.list->items[i]);
        else
            push_int(0);
    } else {
        push_int(0);
    }
}

void list_first_op(void) {
    Value list_val = pop();
    if (list_val.type == VAL_LIST && list_val.list->len > 0)
        push_value(list_val.list->items[0]);
    else
        push_int(0);
}

void list_rest_op(void) {
    Value list_val = pop();
    KList* rest = list_new();
    if (list_val.type == VAL_LIST && list_val.list->len > 1) {
        for (int i = 1; i < list_val.list->len; i++)
            list_push_item(rest, list_val.list->items[i]);
    }
    push_list(rest);
}

void list_last_op(void) {
    Value list_val = pop();
    if (list_val.type == VAL_LIST && list_val.list->len > 0)
        push_value(list_val.list->items[list_val.list->len - 1]);
    else
        push_int(0);
}

void list_reverse_op(void) {
    Value list_val = pop();
    KList* result = list_new();
    if (list_val.type == VAL_LIST) {
        for (int i = list_val.list->len - 1; i >= 0; i--)
            list_push_item(result, list_val.list->items[i]);
    }
    push_list(result);
}

static int value_compare(const void* a, const void* b) {
    const Value* va = (const Value*)a;
    const Value* vb = (const Value*)b;
    double na = 0, nb = 0;
    if (va->type == VAL_INT) na = (double)va->i;
    else if (va->type == VAL_FLOAT) na = va->f;
    if (vb->type == VAL_INT) nb = (double)vb->i;
    else if (vb->type == VAL_FLOAT) nb = vb->f;
    if (va->type == VAL_STR && vb->type == VAL_STR)
        return strcmp(va->s, vb->s);
    if (na < nb) return -1;
    if (na > nb) return 1;
    return 0;
}

void list_sort_op(void) {
    Value list_val = pop();
    if (list_val.type == VAL_LIST) {
        KList* result = list_copy(list_val.list);
        qsort(result->items, result->len, sizeof(Value), value_compare);
        push_list(result);
    } else {
        push_list(list_new());
    }
}

void list_is_empty_op(void) {
    Value list_val = pop();
    if (list_val.type == VAL_LIST)
        push_bool(list_val.list->len == 0);
    else
        push_bool(true);
}

void list_concat_op(void) {
    /* ( list1 list2 -- combined ) */
    Value b = pop(), a = pop();
    KList* result = list_new();
    if (a.type == VAL_LIST) {
        for (int i = 0; i < a.list->len; i++)
            list_push_item(result, a.list->items[i]);
    }
    if (b.type == VAL_LIST) {
        for (int i = 0; i < b.list->len; i++)
            list_push_item(result, b.list->items[i]);
    }
    push_list(result);
}

void list_take_op(void) {
    /* ( list n -- sublist ) */
    Value n = pop();
    Value list_val = pop();
    KList* result = list_new();
    if (list_val.type == VAL_LIST) {
        int count = (int)n.i;
        if (count > list_val.list->len) count = list_val.list->len;
        for (int i = 0; i < count; i++)
            list_push_item(result, list_val.list->items[i]);
    }
    push_list(result);
}

void list_drop_items_op(void) {
    /* ( list n -- sublist ) */
    Value n = pop();
    Value list_val = pop();
    KList* result = list_new();
    if (list_val.type == VAL_LIST) {
        int start = (int)n.i;
        if (start < 0) start = 0;
        for (int i = start; i < list_val.list->len; i++)
            list_push_item(result, list_val.list->items[i]);
    }
    push_list(result);
}

void list_contains_op(void) {
    /* ( list item -- bool ) */
    Value item = pop();
    Value list_val = pop();
    if (list_val.type == VAL_LIST) {
        for (int i = 0; i < list_val.list->len; i++) {
            Value cur = list_val.list->items[i];
            if (cur.type == item.type) {
                if (cur.type == VAL_INT && cur.i == item.i) { push_bool(true); return; }
                if (cur.type == VAL_FLOAT && cur.f == item.f) { push_bool(true); return; }
                if (cur.type == VAL_STR && strcmp(cur.s, item.s) == 0) { push_bool(true); return; }
                if (cur.type == VAL_BOOL && cur.b == item.b) { push_bool(true); return; }
            }
        }
    }
    push_bool(false);
}

void list_index_of_op(void) {
    /* ( list item -- index ) */
    Value item = pop();
    Value list_val = pop();
    if (list_val.type == VAL_LIST) {
        for (int i = 0; i < list_val.list->len; i++) {
            Value cur = list_val.list->items[i];
            if (cur.type == item.type) {
                if (cur.type == VAL_INT && cur.i == item.i) { push_int(i); return; }
                if (cur.type == VAL_FLOAT && cur.f == item.f) { push_int(i); return; }
                if (cur.type == VAL_STR && strcmp(cur.s, item.s) == 0) { push_int(i); return; }
                if (cur.type == VAL_BOOL && cur.b == item.b) { push_int(i); return; }
            }
        }
    }
    push_int(-1);
}

void range_op(void) {
    /* ( start end -- list ) */
    Value end_v = pop();
    Value start_v = pop();
    KList* result = list_new();
    int64_t s = start_v.i, e = end_v.i;
    for (int64_t i = s; i < e; i++) {
        Value v; v.type = VAL_INT; v.i = i;
        list_push_item(result, v);
    }
    push_list(result);
}

void iota_op(void) {
    /* ( n -- list ) */
    Value n = pop();
    KList* result = list_new();
    for (int64_t i = 0; i < n.i; i++) {
        Value v; v.type = VAL_INT; v.i = i;
        list_push_item(result, v);
    }
    push_list(result);
}

/* ============================================================
 * Higher-Order Operations (block-based)
 * ============================================================ */

void map_block_op(KBlock fn) {
    /* ( list -- newlist ) - fn operates on each element */
    Value list_val = pop();
    KList* result = list_new();
    if (list_val.type == VAL_LIST) {
        for (int i = 0; i < list_val.list->len; i++) {
            push_value(list_val.list->items[i]);
            fn();
            list_push_item(result, pop());
        }
    }
    push_list(result);
}

void filter_block_op(KBlock fn) {
    /* ( list -- newlist ) - fn returns bool for each element */
    Value list_val = pop();
    KList* result = list_new();
    if (list_val.type == VAL_LIST) {
        for (int i = 0; i < list_val.list->len; i++) {
            push_value(list_val.list->items[i]);
            fn();
            if (pop_bool()) {
                list_push_item(result, list_val.list->items[i]);
            }
        }
    }
    push_list(result);
}

void fold_block_op(KBlock fn) {
    /* ( list init -- result ) - fn operates on acc and each element */
    Value acc = pop();
    Value list_val = pop();
    if (list_val.type == VAL_LIST) {
        for (int i = 0; i < list_val.list->len; i++) {
            push_value(acc);
            push_value(list_val.list->items[i]);
            fn();
            acc = pop();
        }
    }
    push_value(acc);
}

void each_block_op(KBlock fn) {
    /* ( list -- ) - fn called for each element */
    Value list_val = pop();
    if (list_val.type == VAL_LIST) {
        for (int i = 0; i < list_val.list->len; i++) {
            push_value(list_val.list->items[i]);
            fn();
        }
    }
}

void times_block_op(KBlock fn) {
    /* ( n -- ) - fn called n times, pushes index then pops after */
    Value n = pop();
    for (int64_t i = 0; i < n.i; i++) {
        push_int(i);
        fn();
        pop(); /* discard loop index result */
    }
}

void while_block_op(KBlock cond, KBlock body) {
    /* ( -- ) - execute body while cond returns true */
    while (1) {
        cond();
        if (!pop_bool()) break;
        body();
    }
}

void until_block_op(KBlock cond, KBlock body) {
    /* ( -- ) - execute body until cond returns true */
    while (1) {
        cond();
        if (pop_bool()) break;
        body();
    }
}

void if_block_op(KBlock then_fn) {
    /* ( bool -- ) - execute then_fn if true */
    if (pop_bool()) {
        then_fn();
    }
}

void ifelse_block_op(KBlock then_fn, KBlock else_fn) {
    /* ( bool -- ) - execute then_fn if true, else_fn if false */
    if (pop_bool()) {
        then_fn();
    } else {
        else_fn();
    }
}

void do_block_op(KBlock fn) {
    fn();
}

/* ============================================================
 * Variable Storage
 * ============================================================ */

void var_set(const char* name, Value v) {
    /* Check if variable already exists */
    for (int i = 0; i < var_count; i++) {
        if (strcmp(variables[i].name, name) == 0) {
            variables[i].value = v;
            return;
        }
    }
    /* Add new variable */
    if (var_count < MAX_VARS) {
        strncpy(variables[var_count].name, name, 127);
        variables[var_count].name[127] = '\0';
        variables[var_count].value = v;
        var_count++;
    }
}

Value var_get(const char* name) {
    for (int i = 0; i < var_count; i++) {
        if (strcmp(variables[i].name, name) == 0) {
            return variables[i].value;
        }
    }
    /* Return 0 if not found */
    Value v;
    v.type = VAL_INT;
    v.i = 0;
    return v;
}

/* ============================================================
 * Type Conversion
 * ============================================================ */

void to_string_op(void) {
    Value v = pop();
    char* buf;
    switch (v.type) {
        case VAL_INT:
            buf = (char*)kapila_alloc(32);
            sprintf(buf, "%lld", (long long)v.i);
            push_str(buf);
            break;
        case VAL_FLOAT:
            buf = (char*)kapila_alloc(32);
            sprintf(buf, "%g", v.f);
            push_str(buf);
            break;
        case VAL_BOOL:
            push_str(v.b ? "true" : "false");
            break;
        case VAL_STR:
            push_str(v.s);
            break;
        case VAL_LIST:
            push_value(v);
            /* Simplified: just push "[list]" */
            push_str("[list]");
            break;
    }
}

void to_int_op(void) {
    Value v = pop();
    switch (v.type) {
        case VAL_INT:   push_int(v.i); break;
        case VAL_FLOAT: push_int((int64_t)v.f); break;
        case VAL_BOOL:  push_int(v.b ? 1 : 0); break;
        case VAL_STR:   push_int(atoll(v.s)); break;
        default:        push_int(0); break;
    }
}

void to_float_op(void) {
    Value v = pop();
    switch (v.type) {
        case VAL_INT:   push_float((double)v.i); break;
        case VAL_FLOAT: push_float(v.f); break;
        case VAL_BOOL:  push_float(v.b ? 1.0 : 0.0); break;
        case VAL_STR:   push_float(atof(v.s)); break;
        default:        push_float(0.0); break;
    }
}

/* ============================================================
 * CLI Arguments
 * ============================================================ */

void args_count_op(void) {
    push_int(g_argc);
}

void args_get_op(void) {
    /* ( index -- string ) */
    Value idx = pop();
    int i = (int)idx.i;
    if (i >= 0 && i < g_argc) {
        push_str(g_argv[i]);
    } else {
        push_str("");
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
            printf("%s", v.b ? "true" : "false");
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

void read_line_op(void) {
    /* ( -- str ) Read a line from stdin */
    char buf[4096];
    if (fgets(buf, sizeof(buf), stdin) != NULL) {
        /* Remove trailing newline */
        size_t len = strlen(buf);
        if (len > 0 && buf[len - 1] == '\n') buf[len - 1] = '\0';
        push_str(kapila_strdup(buf));
    } else {
        push_str("");
    }
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
