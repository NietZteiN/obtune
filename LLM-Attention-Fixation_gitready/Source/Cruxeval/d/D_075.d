import std.math;
import std.typecons;
import std.range;

long f(long[] array, long elem) 
{
    long ind = -1;
    foreach (i, n; array)
    {
        if (n == elem)
        {
            ind = i;
            break;
        }
    }
    return ind * 2 + array[array.length - ind - 1] * 3;
}
unittest
{
    alias candidate = f;

    assert(candidate([-1L, 2L, 1L, -8L, 2L], 2L) == -22L);
}
void main(){}
