import std.math;
import std.typecons;

string f(string text, string value) 
{
    auto text_list = text.dup;
    text_list ~= value;
    return text_list.idup;
}
unittest
{
    alias candidate = f;

    assert(candidate("bcksrut", "q") == "bcksrutq");
}
void main(){}
