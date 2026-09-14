import std.math;
import std.typecons;
import std.conv;
import std.string;

string f(string text) 
{
    text = text.toLower();
    auto head = text[0..1].toUpper();
    auto tail = text[1..$];
    return head ~ tail;
}
unittest
{
    alias candidate = f;

    assert(candidate("Manolo") == "Manolo");
}
void main(){}
