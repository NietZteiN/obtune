import std.math;
import std.typecons;
import std.array;
import std.algorithm;
import std.range;

long f(long[] array, long elem) 
{
    long found = -1;
    array.reverse();
    foreach (i, value; array.enumerate)
    {
        if (value == elem)
        {
            found = i;
            break;
        }
    }
    array.reverse();
    return found;
}
unittest
{
    alias candidate = f;

    assert(candidate([5L, -3L, 3L, 2L], 2L) == 0L);
}
void main(){}
