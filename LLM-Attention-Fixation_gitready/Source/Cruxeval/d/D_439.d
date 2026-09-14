import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string value) 
{
    auto parts = value.split(" ");
    string[] selectedParts;
    foreach (i, part; parts)
    {
        if (i % 2 == 0)
        {
            selectedParts ~= part;
        }
    }
    return selectedParts.join(" ");
}
unittest
{
    alias candidate = f;

    assert(candidate("coscifysu") == "coscifysu");
}
void main(){}
