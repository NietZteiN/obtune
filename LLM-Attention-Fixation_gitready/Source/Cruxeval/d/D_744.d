import std.math;
import std.typecons;
string f(string text, string new_ending) 
{
    auto result = text.dup;
    result ~= new_ending;
    return result.idup;
}
unittest
{
    alias candidate = f;

    assert(candidate("jro", "wdlp") == "jrowdlp");
}
void main(){}
