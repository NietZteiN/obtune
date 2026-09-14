import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.range;
import std.string;

string f(string postcode) 
{
    auto index = postcode.indexOf('C');
    return index != -1 ? postcode[index..$] : "";
}
unittest
{
    alias candidate = f;

    assert(candidate("ED20 CW") == "CW");
}
void main(){}
