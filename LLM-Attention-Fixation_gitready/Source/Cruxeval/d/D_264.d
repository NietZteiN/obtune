import std.math;
import std.typecons;
import std.array;

string f(string test_str) 
{
    auto s = test_str.replace("a", "A");
    return s.replace("e", "A");
}
unittest
{
    alias candidate = f;

    assert(candidate("papera") == "pApArA");
}
void main(){}
