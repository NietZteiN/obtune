import std.math;
import std.typecons;
import std.algorithm;

long[] f(long[] a) 
{
    if (a.length >= 2 && a[0] > 0 && a[1] > 0) {
        a.reverse();
        return a;
    }
    a ~= 0;
    return a;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == [0L]);
}
void main(){}
