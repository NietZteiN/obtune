import std.math;
import std.typecons;
import std.algorithm;
import std.string;

string f(string x) 
{
    if (x == x.toLower)
        return x;
    else
    {
        auto reversed = x[$-1..0];
        return reversed;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("ykdfhp") == "ykdfhp");
}
void main(){}
