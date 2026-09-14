import std.math;
import std.typecons;
import std.array;

long f(long num) 
{
    long[] initial = [1];
    long[] total = initial;
    for (long i = 0; i < num; i++)
    {
        total = [1];
        foreach (immutable j; 0 .. total.length - 1)
        {
            total ~= total[j] + (j + 1 < total.length ? total[j + 1] : 0);
        }
        initial ~= total[total.length - 1];
    }
    long sum = 0;
    foreach (immutable x; initial)
    {
        sum += x;
    }
    return sum;
}
unittest
{
    alias candidate = f;

    assert(candidate(3L) == 4L);
}
void main(){}
