import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    return text ~ "#";
}
unittest
{
    alias candidate = f;

    assert(candidate("the cow goes moo") == "the cow goes moo#");
}
void main(){}
