import std.math;
import std.typecons;
import std.algorithm;
import std.array;

string[] f(string[] array, string[] arr) 
{
    string[] result;
    foreach (s; arr)
    {
        auto splitted = s.split(s);
        foreach (l; splitted)
        {
            if (l != "")
            {
                result ~= l;
            }
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate([], []) == []);
}
void main(){}
