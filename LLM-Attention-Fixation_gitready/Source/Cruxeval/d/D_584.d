import std.math;
import std.typecons;
import std.string;

string f(string txt) 
{
    return txt;
}
unittest
{
    alias candidate = f;

    assert(candidate("5123807309875480094949830") == "5123807309875480094949830");
}
void main(){}
