import std.math;
import std.typecons;

long[] f(long[] arr) 
{
    auto count = arr.length;
    auto sub = arr.dup;
    for (size_t i = 0; i < count; i += 2) {
        sub[i] *= 5;
    }
    return sub;
}
unittest
{
    alias candidate = f;

    assert(candidate([-3L, -6L, 2L, 7L]) == [-15L, -6L, 10L, 7L]);
}
void main(){}
