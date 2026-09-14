import std.math;
import std.typecons;
import std.array;
import std.algorithm;

string[] f(long number) 
{
    enum transl = ["A", "B", "C", "D", "E"];
    string[] result;

    foreach (i, key; transl)
    {
        if ((i + 1) % number == 0)
        {
            result ~= key;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate(2L) == ["B", "D"]);
}
void main(){}
