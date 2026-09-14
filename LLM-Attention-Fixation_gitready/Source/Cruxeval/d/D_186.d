import std.math;
import std.typecons;
import std.stdio;
import std.string;

string f(string text) 
{
    return text.strip();
}
unittest
{
    alias candidate = f;

    assert(candidate("pvtso") == "pvtso");
}
void main(){}
