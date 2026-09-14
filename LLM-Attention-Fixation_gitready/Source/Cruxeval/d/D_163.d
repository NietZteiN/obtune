import std.math;
import std.typecons;
import std.array;

string f(string text, string space_symbol, long size) 
{
    auto spaces = replicate(space_symbol, cast(int)(size - text.length));
    return text ~ spaces;
}
unittest
{
    alias candidate = f;

    assert(candidate("w", "))", 7L) == "w))))))))))))");
}
void main(){}
