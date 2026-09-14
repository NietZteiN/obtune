import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string text) 
{
    foreach (punct; "!.?,:;".dup)
    {
        if (text.count(punct) > 1 || text.endsWith(punct))
            return "no";
    }
    return text.capitalize();
}
unittest
{
    alias candidate = f;

    assert(candidate("djhasghasgdha") == "Djhasghasgdha");
}
void main(){}
