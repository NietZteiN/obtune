import std.math;
import std.typecons;
long[][] f(long[][] array) 
{
    long[][] return_arr;
    foreach (a; array) {
        return_arr ~= a.dup;
    }
    return return_arr;
}
unittest
{
    alias candidate = f;

    assert(candidate([[1L, 2L, 3L], [], [1L, 2L, 3L]]) == [[1L, 2L, 3L], [], [1L, 2L, 3L]]);
}
void main(){}
