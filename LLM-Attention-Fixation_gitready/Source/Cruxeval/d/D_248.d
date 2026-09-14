import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] a, long[] b) 
{
    a.sort();
    b.sort().reverse();
    return a ~ b;
}
unittest
{
    alias candidate = f;

    assert(candidate([666L], []) == [666L]);
}
void main(){}
