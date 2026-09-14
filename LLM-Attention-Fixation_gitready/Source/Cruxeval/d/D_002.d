import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    auto new_text = text.replace("+", "");
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate("hbtofdeiequ") == "hbtofdeiequ");
}
void main(){}
