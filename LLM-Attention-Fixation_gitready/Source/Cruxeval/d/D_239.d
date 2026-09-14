import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string text, string froms) 
{
    auto leftStripped = text.stripLeft(froms);
    auto rightStripped = leftStripped.stripRight(froms);
    return rightStripped;
}
unittest
{
    alias candidate = f;

    assert(candidate("0 t 1cos ", "st 0	
  ") == "1co");
}
void main(){}
