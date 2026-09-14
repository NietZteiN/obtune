import std.math;
import std.typecons;

long f(string[] items, string target) 
{
    foreach (i, item; items)
    {
        if (item == target)
            return i;
    }
    return -1;
}
unittest
{
    alias candidate = f;

    assert(candidate(["1", "+", "-", "**", "//", "*", "+"], "**") == 3L);
}
void main(){}
