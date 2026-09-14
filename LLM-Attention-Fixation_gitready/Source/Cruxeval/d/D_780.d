import std.math;
import std.typecons;
import std.array;
import std.conv;
import std.string;

string f(long[] ints) 
{
    long[301] counts;
    counts[] = 0;

    foreach (i; ints)
    {
        counts[i]++;
    }

    string[] r;
    foreach (i; 0 .. counts.length)
    {
        if (counts[i] >= 3)
        {
            r ~= to!string(i);
        }
    }

    counts[] = 0;
    return r.join(" ");
}
unittest
{
    alias candidate = f;

    assert(candidate([2L, 3L, 5L, 2L, 4L, 5L, 2L, 89L]) == "2");
}
void main(){}
