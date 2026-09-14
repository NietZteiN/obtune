import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text, string value) 
{
    long[] indexes;
    foreach (i; 0 .. text.length)
    {
        if (text[i] == value[0] && (i == 0 || text[i-1] != value[0]))
        {
            indexes ~= i;
        }
    }
    if (indexes.length % 2 == 1)
    {
        return text;
    }
    return text[indexes[0]+1 .. indexes[$-1]];
}
unittest
{
    alias candidate = f;

    assert(candidate("btrburger", "b") == "tr");
}
void main(){}
