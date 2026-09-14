import std.math;
import std.typecons;
import std.algorithm;
import std.string;

string f(string text, string wrong, string right) 
{
    auto new_text = text.replace(wrong, right);
    return toUpper(new_text);
}
unittest
{
    alias candidate = f;

    assert(candidate("zn kgd jw lnt", "h", "u") == "ZN KGD JW LNT");
}
void main(){}
