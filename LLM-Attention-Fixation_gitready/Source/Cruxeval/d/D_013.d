import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long f(string[] names) 
{
    long numberOfNames = 0;
    foreach (i; names)
    {
        if (i.canBeOnlyAlpha)
        {
            numberOfNames++;
        }
    }
    return numberOfNames;
}

bool canBeOnlyAlpha(string s)
{
    foreach (c; s)
    {
        if (!('a' <= c && c <= 'z') && !('A' <= c && c <= 'Z'))
        {
            return false;
        }
    }
    return true;
}

unittest
{
    alias candidate = f;

    assert(candidate(["sharron", "Savannah", "Mike Cherokee"]) == 2L);
}
void main(){}
