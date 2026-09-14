import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] plot, long delin) 
{
    long split = -1;
    foreach (i, n; plot)
    {
        if (n == delin)
        {
            split = i;
            break;
        }
    }
    if (split != -1)
    {
        return plot[0 .. split] ~ plot[split + 1 .. $];
    }
    else
    {
        return plot;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L, 3L, 4L], 3L) == [1L, 2L, 4L]);
}
void main(){}
