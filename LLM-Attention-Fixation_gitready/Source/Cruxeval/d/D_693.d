import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text) 
{
    auto n = cast(int)text.indexOf('8');
    string result;
    foreach (_; 0..n)
    {
        result ~= "x0";
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("sa832d83r xd 8g 26a81xdf") == "x0x0");
}
void main(){}
