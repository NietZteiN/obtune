import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[][] f(long[][] matrix) 
{
    matrix = matrix.reverse;
    long[][] result;
    foreach (primary; matrix) {
        primary.sort!"a > b";
        result ~= primary.dup;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate([[1L, 1L, 1L, 1L]]) == [[1L, 1L, 1L, 1L]]);
}
void main(){}
